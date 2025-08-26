"""
Common fixtures and utilities for PlugFlow tests
"""
import textwrap
from pathlib import Path
import pytest
from plugflow import PluginManager, BasePlugin


@pytest.fixture
def plugin_writer():
    """Fixture that provides a helper function to write test plugins"""
    def write_plugin(tmpdir: Path, name: str, body: str, as_pkg=False):
        if as_pkg:
            pkg = tmpdir / name
            pkg.mkdir()
            (pkg / "__init__.py").write_text(textwrap.dedent(body), encoding="utf-8")
            return pkg
        else:
            f = tmpdir / f"{name}.py"
            f.write_text(textwrap.dedent(body), encoding="utf-8")
            return f
    return write_plugin


@pytest.fixture
def sample_plugin_code():
    """Fixture providing sample plugin code templates"""
    return {
        "basic": """
            from plugflow import BasePlugin
            class BasicPlugin(BasePlugin):
                name = "basic"
                
                def on_event(self, event, data, manager):
                    if event == "test":
                        return "basic_response"
        """,
        
        "command_handler": """
            from plugflow import BasePlugin
            class CommandPlugin(BasePlugin):
                name = "command"
                
                def handle_command(self, command, args):
                    if command == "hello":
                        return f"Hello, {args}!"
                    return None
        """,
        
        "filter": """
            from plugflow import BasePlugin
            class FilterPlugin(BasePlugin):
                name = "filter"
                priority = 10
                
                def filter_message(self, text):
                    return text.replace("bad", "good")
        """,
        
        "lifecycle": """
            from plugflow import BasePlugin
            
            # Global state for testing lifecycle
            _lifecycle_state = {"loaded": False, "unloaded": False}
            
            class LifecyclePlugin(BasePlugin):
                name = "lifecycle"
                
                def on_load(self, manager):
                    global _lifecycle_state
                    _lifecycle_state["loaded"] = True
                    
                def on_unload(self, manager):
                    global _lifecycle_state
                    _lifecycle_state["unloaded"] = True
                    
                def handle_command(self, command, args):
                    if command == "state":
                        return str(_lifecycle_state)
        """
    }
