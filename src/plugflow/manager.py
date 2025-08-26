
from __future__ import annotations
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import inspect

from .base import BasePlugin
from .loader import discover_and_load
from .watcher import DirectoryWatcher

class PluginRecord:
    __slots__ = ("plugin", "path", "module")
    def __init__(self, plugin: BasePlugin, path: Path, module) -> None:
        self.plugin = plugin
        self.path = path
        self.module = module

class PluginManager:
    def __init__(self,
                 plugins_paths: List[str | Path],
                 context: Any = None,
                 recursive: bool = True,
                 hot_reload: bool = False,
                 poll_interval: float = 1.0,
                 logger: Optional[logging.Logger] = None) -> None:
        self.paths = [Path(p) for p in plugins_paths]
        self.context = context
        self.recursive = recursive
        self.hot_reload = hot_reload
        self.poll_interval = poll_interval
        self.log = logger or self._default_logger()
        self._lock = threading.RLock()
        self._records: Dict[str, PluginRecord] = {}
        self._watchers: List[DirectoryWatcher] = []

    def _default_logger(self) -> logging.Logger:
        logger = logging.getLogger("plugflow")
        if not logger.handlers:
            h = logging.StreamHandler()
            fmt = logging.Formatter("[%(asctime)s] %(levelname)s plugflow: %(message)s", "%H:%M:%S")
            h.setFormatter(fmt)
            logger.addHandler(h)
        # Default to WARNING - only show when explicitly enabled
        if logger.level == logging.NOTSET:
            logger.setLevel(logging.WARNING)
        return logger

    # --- Loading ---
    def load_all(self) -> None:
        for p in self.paths:
            self.load_from_path(p)
        if self.hot_reload:
            self._start_watchers()

    def _start_watchers(self) -> None:
        for p in self.paths:
            watcher = DirectoryWatcher(
                root=p,
                interval=self.poll_interval,
                recursive=self.recursive,
                on_change=self._on_fs_change,
                on_delete=self._on_fs_delete,
            )
            watcher.start()
            self._watchers.append(watcher)
            self.log.info(f"Watching {p} for plugin changes...")

    def stop(self) -> None:
        for w in self._watchers:
            w.stop()
        self._watchers.clear()

    def load_from_path(self, path: Path) -> None:
        if not path.exists():
            self.log.warning(f"Plugins path not found: {path}")
            return
        loaded = 0
        with self._lock:
            for plugin, p, module in discover_and_load(path, self.context, recursive=self.recursive):
                self._add_record(plugin, p, module)
                loaded += 1
        if loaded:
            self.log.debug(f"Loaded {loaded} plugin(s) from {path}")

    def _add_record(self, plugin: BasePlugin, path: Path, module) -> None:
        name = plugin.plugin_name
        # unload if duplicate
        old = self._records.get(name)
        if old:
            try:
                old.plugin.on_unload(self)
            except Exception as e:
                self.log.exception(f"Error on_unload({name}): {e}")
        self._records[name] = PluginRecord(plugin, path, module)
        try:
            plugin.on_load(self)
        except Exception as e:
            self.log.exception(f"Error on_load({name}): {e}")
        self.log.debug(f"Plugin ready: {name} ({getattr(plugin, 'version', 'n/a')}) from {path}")

    def _on_fs_change(self, target: Path) -> None:
        # On any change - try to load what's in the folder
        self.log.debug(f"Change detected: {target}")
        try:
            self.load_from_path(target if target.is_dir() else target.parent)
        except Exception as e:
            self.log.exception(f"Hot reload failed for {target}: {e}")

    def _on_fs_delete(self, target: Path) -> None:
        # Unload plugins whose path == target
        with self._lock:
            to_remove = [k for k, rec in self._records.items() if rec.path == target]
            for k in to_remove:
                rec = self._records.pop(k)
                try:
                    rec.plugin.on_unload(self)
                except Exception as e:
                    self.log.exception(f"Error on_unload({k}): {e}")
                self.log.debug(f"Plugin unloaded due to deletion: {k} from {target}")

    # --- Introspection ---
    def list_plugins(self) -> List[str]:
        with self._lock:
            return sorted(self._records.keys())

    def get(self, name: str) -> Optional[BasePlugin]:
        with self._lock:
            rec = self._records.get(name)
            return rec.plugin if rec else None

    # --- Dispatching ---
    def dispatch_event(self, event: str, data: Any = None) -> List[Any]:
        results: List[Any] = []
        with self._lock:
            plugins = sorted(self._records.values(), key=lambda r: getattr(r.plugin, 'priority', 100))
            for rec in plugins:
                plg = rec.plugin
                if hasattr(plg, "handles") and not plg.handles(event):
                    continue
                if hasattr(plg, "on_event") and callable(plg.on_event):
                    try:
                        results.append(plg.on_event(event, data, self))
                    except Exception as e:
                        self.log.exception(f"Plugin {plg.plugin_name} on_event error: {e}")
        return results

    def broadcast(self, method: str, *args, **kwargs) -> List[Any]:
        results: List[Any] = []
        with self._lock:
            for rec in self._records.values():
                plg = rec.plugin
                if hasattr(plg, method):
                    fn = getattr(plg, method)
                    if callable(fn):
                        try:
                            results.append(fn(*args, **kwargs))
                        except Exception as e:
                            self.log.exception(f"Plugin {plg.plugin_name} {method} error: {e}")
        return results

    # --- Chat helpers ---
    def handle_message(self, text: str) -> List[str]:
        responses: List[str] = []
        current = text

        # 1) Filters
        with self._lock:
            plugins = sorted(self._records.values(), key=lambda r: getattr(r.plugin, 'priority', 100))
            for rec in plugins:
                plg = rec.plugin
                if hasattr(plg, "filter_message") and callable(plg.filter_message):
                    try:
                        new_text = plg.filter_message(current)
                        if isinstance(new_text, str):
                            current = new_text
                    except Exception as e:
                        self.log.exception(f"Plugin {plg.plugin_name} filter_message error: {e}")

        # 2) Commands / text
        cmd = None
        args = ""
        if current.strip().startswith("/"):
            # format: /cmd rest...
            parts = current.strip().split(maxsplit=1)
            cmd = parts[0].lstrip("/")
            args = parts[1] if len(parts) > 1 else ""

        with self._lock:
            for rec in plugins:
                plg = rec.plugin
                if cmd and hasattr(plg, "handle_command") and callable(plg.handle_command):
                    try:
                        res = plg.handle_command(cmd, args)
                        if res is not None:
                            responses.append(str(res))
                    except Exception as e:
                        self.log.exception(f"Plugin {plg.plugin_name} handle_command error: {e}")
                elif not cmd and hasattr(plg, "on_message") and callable(getattr(plg, "on_message")):
                    # arbitrary text processing
                    try:
                        res = plg.on_message(current, self)  # type: ignore[attr-defined]
                        if res is not None:
                            if isinstance(res, list):
                                responses.extend(map(str, res))
                            else:
                                responses.append(str(res))
                    except Exception as e:
                        self.log.exception(f"Plugin {plg.plugin_name} on_message error: {e}")

        return responses
