"""
Tests for PluginManager core functionality
"""
import pytest
from pathlib import Path
from plugflow import PluginManager, BasePlugin


def test_default_plugins_paths():
    """Test that PluginManager can be created without plugins_paths parameter"""
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


def test_nonexistent_path_handling():
    """Test handling of non-existent plugin paths"""
    mgr = PluginManager(["/nonexistent/path"])
    mgr.load_all()  # Should not crash
    assert mgr.list_plugins() == []


def test_context_sharing(tmp_path: Path, plugin_writer):
    """Test that context is shared between manager and plugins"""
    context = {"app_name": "test_app", "version": "1.0.0"}
    
    body = """
from plugflow import BasePlugin

class ContextPlugin(BasePlugin):
    name = "context"
    
    def __init__(self, context=None):
        super().__init__()
        self.context = context
    
    def handle_command(self, command, args):
        if command == "info" and self.context:
            return f"{self.context['app_name']} v{self.context['version']}"
"""
    plugin_writer(tmp_path, "context", body)
    
    mgr = PluginManager([str(tmp_path)], context=context)
    mgr.load_all()
    
    result = mgr.handle_message("/info")
    assert "test_app v1.0.0" in result


def test_recursive_loading(tmp_path: Path, plugin_writer):
    """Test recursive plugin loading from subdirectories"""
    # Create nested directory structure
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    
    # Plugin in root
    root_body = """
from plugflow import BasePlugin
class RootPlugin(BasePlugin):
    name = "root"
"""
    plugin_writer(tmp_path, "root_plugin", root_body)
    
    # Plugin in subdirectory
    sub_body = """
from plugflow import BasePlugin
class SubPlugin(BasePlugin):
    name = "sub"
"""
    plugin_writer(subdir, "sub_plugin", sub_body)
    
    # Test recursive loading (default)
    mgr = PluginManager([str(tmp_path)], recursive=True)
    mgr.load_all()
    assert set(mgr.list_plugins()) == {"root", "sub"}
    
    # Test non-recursive loading
    mgr2 = PluginManager([str(tmp_path)], recursive=False)
    mgr2.load_all()
    assert mgr2.list_plugins() == ["root"]


def test_plugin_replacement(tmp_path: Path, plugin_writer):
    """Test that loading a plugin with the same name replaces the old one"""
    body1 = """
from plugflow import BasePlugin
class TestPlugin(BasePlugin):
    name = "test"
    version = "1.0.0"
    
    def handle_command(self, command, args):
        if command == "version":
            return self.version
"""
    
    body2 = """
from plugflow import BasePlugin  
class TestPlugin(BasePlugin):
    name = "test"
    version = "2.0.0"
    
    def handle_command(self, command, args):
        if command == "version":
            return self.version
"""
    
    plugin_writer(tmp_path, "test1", body1)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    plugin = mgr.get("test")
    assert plugin is not None
    result = mgr.handle_message("/version")
    assert "1.0.0" in result
    
    # Load second plugin with same name
    plugin_writer(tmp_path, "test2", body2)
    mgr.load_from_path(tmp_path)
    
    plugin = mgr.get("test")
    assert plugin is not None
    result = mgr.handle_message("/version")
    assert "2.0.0" in result
    assert len(mgr.list_plugins()) == 1  # Should still have only one plugin


def test_load_file_and_package(tmp_path: Path, plugin_writer):
    """Test loading both file plugins and package plugins"""
    # file plugin
    file_body = """
from plugflow import BasePlugin
class A(BasePlugin):
    name = "A"
    def on_event(self, event, data, manager): 
        if event == "ping": 
            return "pong"
"""
    plugin_writer(tmp_path, "a_plugin", file_body)

    # package plugin (via register)
    pkg_body = """
from plugflow import BasePlugin
class B(BasePlugin):
    name = "B"
def register(context):
    return [B]
"""
    plugin_writer(tmp_path, "b_pkg", pkg_body, as_pkg=True)

    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()

    assert set(mgr.list_plugins()) == {"A", "B"}
    res = mgr.dispatch_event("ping")
    assert "pong" in res
