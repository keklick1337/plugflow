"""
Tests for plugin functionality and lifecycle
"""
import pytest
from pathlib import Path
from plugflow import PluginManager, BasePlugin


def test_plugin_priority_system(tmp_path: Path, plugin_writer):
    """Test that plugins are loaded and executed based on priority"""
    body = """
from plugflow import BasePlugin

class HighPriorityPlugin(BasePlugin):
    name = "high"
    priority = 100
    
    def on_event(self, event, data, manager):
        if event == "test":
            return "high_priority"

class LowPriorityPlugin(BasePlugin):
    name = "low" 
    priority = 1
    
    def on_event(self, event, data, manager):
        if event == "test":
            return "low_priority"

class MediumPriorityPlugin(BasePlugin):
    name = "medium"
    priority = 50
    
    def on_event(self, event, data, manager):
        if event == "test":
            return "medium_priority"
"""
    plugin_writer(tmp_path, "priority_test", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    results = mgr.dispatch_event("test")
    # Higher priority plugins should be processed first
    assert results == ["high_priority", "medium_priority", "low_priority"]


def test_plugin_lifecycle_hooks(tmp_path: Path, plugin_writer):
    """Test that on_load and on_unload hooks are called"""
    # We'll test this by using a global variable since we can't easily access plugin attributes
    body = """
from plugflow import BasePlugin

# Global state to track lifecycle
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
    plugin_writer(tmp_path, "lifecycle", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Check that plugin was loaded
    result = mgr.handle_message("/state")
    assert "'loaded': True" in str(result)
    assert "'unloaded': False" in str(result)


def test_plugin_versioning(tmp_path: Path, plugin_writer):
    """Test plugin version information"""
    body = """
from plugflow import BasePlugin

class VersionedPlugin(BasePlugin):
    name = "versioned"
    version = "2.1.0"
    
    def handle_command(self, command, args):
        if command == "version":
            return self.version
"""
    plugin_writer(tmp_path, "versioned", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    plugin = mgr.get("versioned")
    assert plugin is not None
    assert plugin.version == "2.1.0"
    
    result = mgr.handle_message("/version")
    assert "2.1.0" in result


def test_handles_method(tmp_path: Path, plugin_writer):
    """Test plugins with handles() method for selective event processing"""
    body = """
from plugflow import BasePlugin

class SelectivePlugin(BasePlugin):
    name = "selective"
    
    def handles(self, event):
        return event in ["allowed_event", "special_event"]
    
    def on_event(self, event, data, manager):
        return f"handled_{event}"

class AlwaysHandlePlugin(BasePlugin):
    name = "always"
    
    def on_event(self, event, data, manager):
        return f"always_{event}"
"""
    plugin_writer(tmp_path, "selective", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test selective handling
    results = mgr.dispatch_event("allowed_event")
    assert "handled_allowed_event" in results
    assert "always_allowed_event" in results
    
    # Test non-handled event
    results = mgr.dispatch_event("forbidden_event")
    assert "handled_forbidden_event" not in results
    assert "always_forbidden_event" in results


def test_error_isolation(tmp_path: Path, plugin_writer):
    """Test that plugin errors don't crash the manager"""
    body = """
from plugflow import BasePlugin

class GoodPlugin(BasePlugin):
    name = "good"
    
    def on_event(self, event, data, manager):
        if event == "test":
            return "good_result"

class BadPlugin(BasePlugin):
    name = "bad"
    
    def on_event(self, event, data, manager):
        if event == "test":
            raise Exception("Plugin error!")
            
    def handle_command(self, command, args):
        if command == "crash":
            raise ValueError("Command error!")
"""
    plugin_writer(tmp_path, "error_test", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Event dispatch should continue despite error
    results = mgr.dispatch_event("test")
    assert "good_result" in results
    assert len(results) == 1  # bad plugin result should be skipped
    
    # Command handling should continue despite error
    result = mgr.handle_message("/crash")
    assert result == []  # No successful responses
