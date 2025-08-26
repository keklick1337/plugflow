"""Basic tests for PlugFlow core functionality."""

import pytest
from pathlib import Path
import textwrap

from plugflow import PluginManager, BasePlugin


def write_plugin(tmpdir: Path, name: str, body: str, as_pkg=False):
    """Helper to write plugin files for testing."""
    if as_pkg:
        pkg = tmpdir / name
        pkg.mkdir()
        (pkg / "__init__.py").write_text(textwrap.dedent(body), encoding="utf-8")
        return pkg
    else:
        f = tmpdir / f"{name}.py"
        f.write_text(textwrap.dedent(body), encoding="utf-8")
        return f


def test_plugin_manager_creation():
    """Test that PluginManager can be created with default parameters."""
    # Test with no parameters
    mgr = PluginManager()
    assert mgr.paths == []
    assert mgr.list_plugins() == []
    
    # Test with None
    mgr2 = PluginManager(plugins_paths=None)
    assert mgr2.paths == []
    
    # Test with empty list
    mgr3 = PluginManager(plugins_paths=[])
    assert mgr3.paths == []


def test_basic_plugin_loading(tmp_path: Path):
    """Test basic plugin loading from file."""
    plugin_body = """
from plugflow import BasePlugin

class TestPlugin(BasePlugin):
    name = "test"
    
    def handle_command(self, command, args):
        if command == "hello":
            return f"Hello, {args}!"
"""
    write_plugin(tmp_path, "test_plugin", plugin_body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    assert "test" in mgr.list_plugins()
    plugin = mgr.get("test")
    assert plugin is not None
    assert plugin.plugin_name == "test"


def test_command_handling(tmp_path: Path):
    """Test command handling through plugins."""
    plugin_body = """
from plugflow import BasePlugin

class CommandPlugin(BasePlugin):
    name = "commands"
    
    def handle_command(self, command, args):
        if command == "echo":
            return f"Echo: {args}"
"""
    write_plugin(tmp_path, "cmd_plugin", plugin_body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    result = mgr.handle_message("/echo test message")
    assert len(result) == 1
    assert "Echo: test message" in result[0]


def test_event_dispatch(tmp_path: Path):
    """Test event dispatching to plugins."""
    plugin_body = """
from plugflow import BasePlugin

class EventPlugin(BasePlugin):
    name = "events"
    
    def on_event(self, event, data, manager):
        if event == "test_event":
            return f"Got: {data}"
"""
    write_plugin(tmp_path, "event_plugin", plugin_body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    results = mgr.dispatch_event("test_event", "test_data")
    assert len(results) == 1
    assert "Got: test_data" in results[0]


def test_nonexistent_path():
    """Test handling of non-existent plugin paths."""
    mgr = PluginManager(["/nonexistent/path"])
    mgr.load_all()  # Should not crash
    assert mgr.list_plugins() == []
