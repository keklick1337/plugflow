
from __future__ import annotations
from abc import ABC
from typing import Any, Dict, Iterable, Optional

class BasePlugin(ABC):
    """Base plugin class.

    A plugin can define the following methods (all optional):
      - on_load(self, manager): callback right after loading
      - on_unload(self, manager): callback before unloading
      - handles(self, event: str) -> bool: filter for events
      - on_event(self, event: str, data: Any, manager) -> Any: handle arbitrary events
      - filter_message(self, text: str) -> Optional[str]: filter/transform incoming messages
      - handle_command(self, command: str, args: str): handle commands `/command args`
      - commands(self) -> Dict[str, Any]: declarative command description (optional)
    """

    name: Optional[str] = None
    version: str = "0.1.0"
    priority: int = 100

    def __init__(self, context: Any = None, **kwargs: Any) -> None:
        self.context = context
        self.config = kwargs

    # --- lifecycle ---
    def on_load(self, manager) -> None:  # pragma: no cover - default no-op
        pass

    def on_unload(self, manager) -> None:  # pragma: no cover - default no-op
        pass

    # --- events ---
    def handles(self, event: str) -> bool:
        return True

    def on_event(self, event: str, data: Any, manager) -> Any:  # pragma: no cover
        return None

    # --- chat helpers ---
    def filter_message(self, text: str) -> Optional[str]:  # pragma: no cover
        return None

    def handle_command(self, command: str, args: str):  # pragma: no cover
        return None

    def commands(self) -> Dict[str, Any]:  # pragma: no cover
        return {}

    # --- util ---
    @property
    def plugin_name(self) -> str:
        return self.name or self.__class__.__name__
