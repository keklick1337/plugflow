
from __future__ import annotations
import threading
import time
from pathlib import Path
from typing import Callable, Dict

class DirectoryWatcher:
    """Simple file polling for hot-reload without external dependencies.

    on_change: callback(path: Path) called on modification/creation of .py or __init__.py package.
    on_delete: callback(path: Path) called on plugin deletion.
    """
    def __init__(self, root: Path, interval: float = 1.0, recursive: bool = True,
                 on_change: Callable[[Path], None] | None = None,
                 on_delete: Callable[[Path], None] | None = None) -> None:
        self.root = root
        self.interval = interval
        self.recursive = recursive
        self.on_change = on_change
        self.on_delete = on_delete
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._mtimes: Dict[Path, float] = {}

    def _iter_targets(self):
        if self.recursive:
            for p in self.root.rglob("*.py"):
                # track only root modules: single .py and __init__.py packages
                if p.name == "__init__.py" or p.parent == self.root:
                    yield p if p.name != "__init__.py" else p.parent
        else:
            for p in self.root.glob("*.py"):
                yield p
            for p in self.root.iterdir():
                if p.is_dir() and (p / "__init__.py").exists():
                    yield p

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"DirectoryWatcher({self.root})")
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        while not self._stop.is_set():
            current = set()
            for target in self._iter_targets():
                try:
                    mtime = target.stat().st_mtime
                except FileNotFoundError:
                    continue
                current.add(target)
                prev = self._mtimes.get(target)
                if prev is None:
                    self._mtimes[target] = mtime
                    if self.on_change:
                        self.on_change(target)
                elif mtime > prev + 1e-6:
                    self._mtimes[target] = mtime
                    if self.on_change:
                        self.on_change(target)

            # removed files
            removed = set(self._mtimes.keys()) - current
            for r in removed:
                self._mtimes.pop(r, None)
                if self.on_delete:
                    self.on_delete(r)
            time.sleep(self.interval)
