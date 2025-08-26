
from __future__ import annotations
import importlib.util
import sys
import types
import inspect
from pathlib import Path
from typing import Any, Iterable, List, Tuple, Dict, Optional, Set

from .base import BasePlugin

def _unique_module_name(path: Path) -> str:
    # Make module unique by absolute path and current file version
    key = str(path.resolve()) + f":{path.stat().st_mtime_ns}"
    import hashlib
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return f"plugflow_ext_{digest}"

def _iter_python_entries(plugins_dir: Path, recursive: bool = True) -> Iterable[Path]:
    """Searches for .py files and packages with __init__.py."""
    if recursive:
        for p in plugins_dir.rglob("*.py"):
            # For recursive mode, consider all .py files and packages
            if p.name == "__init__.py":
                yield p.parent  # yield the package directory
            else:
                yield p  # yield the .py file
    else:
        for p in plugins_dir.glob("*.py"):
            yield p
        for p in plugins_dir.iterdir():
            if p.is_dir() and (p / "__init__.py").exists():
                yield p

def _load_module_from_path(path: Path) -> types.ModuleType:
    if path.is_dir():
        file = path / "__init__.py"
    else:
        file = path
    module_name = _unique_module_name(path)
    spec = importlib.util.spec_from_file_location(module_name, file)
    if not spec or not spec.loader:
        raise ImportError(f"Failed to create spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module

def _instantiate_from_module(module: types.ModuleType, context: Any) -> List[BasePlugin]:
    out: List[BasePlugin] = []

    # 1) register(context) -> Iterable[BasePlugin | Type[BasePlugin]]
    reg = getattr(module, "register", None)
    if callable(reg):
        produced = list(reg(context))  # type: ignore
        for item in produced:
            if inspect.isclass(item) and issubclass(item, BasePlugin):
                out.append(item(context))
            elif isinstance(item, BasePlugin):
                out.append(item)
            else:
                raise TypeError("register() must return instances or classes of BasePlugin")
        if out:
            return out

    # 2) variables PLUGIN / PLUGINS
    for var_name in ("PLUGIN", "PLUGINS", "plugins"):
        if hasattr(module, var_name):
            obj = getattr(module, var_name)
            if isinstance(obj, BasePlugin):
                out.append(obj)
            elif isinstance(obj, Iterable):
                for el in obj:
                    if inspect.isclass(el) and issubclass(el, BasePlugin):
                        out.append(el(context))
                    elif isinstance(el, BasePlugin):
                        out.append(el)
            if out:
                return out

    # 3) all BasePlugin subclasses in module
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if issubclass(cls, BasePlugin) and cls is not BasePlugin and cls.__module__ == module.__name__:
            out.append(cls(context))
    return out

def discover_and_load(plugins_dir: Path, context: Any, recursive: bool = True) -> List[Tuple[BasePlugin, Path, types.ModuleType]]:
    """Returns list of tuples (plugin, path, module)."""
    result = []
    for item in _iter_python_entries(plugins_dir, recursive=recursive):
        module = _load_module_from_path(item if item.is_file() else Path(item))
        plugins = _instantiate_from_module(module, context)
        for plg in plugins:
            result.append((plg, Path(item), module))
    return result
