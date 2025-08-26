"""
Tests for event system functionality
"""
import pytest
from pathlib import Path
from plugflow import PluginManager, BasePlugin


def test_event_dispatching(tmp_path: Path, plugin_writer):
    """Test basic event dispatching"""
    body = """
from plugflow import BasePlugin

class EventPlugin(BasePlugin):
    name = "event_handler"
    
    def on_event(self, event, data, manager):
        if event == "user_login":
            return f"User {data['user_id']} logged in"
        elif event == "user_logout":
            return f"User {data['user_id']} logged out"
        return None
"""
    plugin_writer(tmp_path, "events", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test login event
    results = mgr.dispatch_event("user_login", {"user_id": 123})
    assert "User 123 logged in" in results
    
    # Test logout event
    results = mgr.dispatch_event("user_logout", {"user_id": 123})
    assert "User 123 logged out" in results
    
    # Test unknown event
    results = mgr.dispatch_event("unknown_event", {})
    assert results == [None]


def test_multiple_event_handlers(tmp_path: Path, plugin_writer):
    """Test multiple plugins handling the same event"""
    body = """
from plugflow import BasePlugin

class LoggerPlugin(BasePlugin):
    name = "logger"
    priority = 100
    
    def on_event(self, event, data, manager):
        if event == "user_action":
            return f"LOG: {data['action']} by {data['user']}"

class NotificationPlugin(BasePlugin):
    name = "notification"
    priority = 50
    
    def on_event(self, event, data, manager):
        if event == "user_action":
            return f"NOTIFY: {data['action']}"

class AnalyticsPlugin(BasePlugin):
    name = "analytics"
    priority = 10
    
    def on_event(self, event, data, manager):
        if event == "user_action":
            return f"ANALYTICS: tracked {data['action']}"
"""
    plugin_writer(tmp_path, "multi_events", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    results = mgr.dispatch_event("user_action", {"action": "click", "user": "john"})
    
    # Results should be in priority order (high to low)
    assert len(results) == 3
    assert "LOG: click by john" in results[0]
    assert "NOTIFY: click" in results[1]
    assert "ANALYTICS: tracked click" in results[2]


def test_event_data_passing(tmp_path: Path, plugin_writer):
    """Test that event data is properly passed to plugins"""
    body = """
from plugflow import BasePlugin

class DataPlugin(BasePlugin):
    name = "data_handler"
    
    def on_event(self, event, data, manager):
        if event == "process_data":
            if isinstance(data, dict):
                return f"Dict with keys: {sorted(data.keys())}"
            elif isinstance(data, list):
                return f"List with {len(data)} items"
            elif isinstance(data, str):
                return f"String: {data}"
            else:
                return f"Type: {type(data).__name__}"
"""
    plugin_writer(tmp_path, "data_test", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test dict data
    results = mgr.dispatch_event("process_data", {"a": 1, "b": 2})
    assert "Dict with keys: ['a', 'b']" in results
    
    # Test list data
    results = mgr.dispatch_event("process_data", [1, 2, 3, 4])
    assert "List with 4 items" in results
    
    # Test string data
    results = mgr.dispatch_event("process_data", "hello world")
    assert "String: hello world" in results
    
    # Test None data
    results = mgr.dispatch_event("process_data", None)
    assert "Type: NoneType" in results


def test_event_without_data(tmp_path: Path, plugin_writer):
    """Test events dispatched without data"""
    body = """
from plugflow import BasePlugin

class SimpleEventPlugin(BasePlugin):
    name = "simple"
    
    def on_event(self, event, data, manager):
        if event == "startup":
            return "System started"
        elif event == "shutdown":
            return "System stopped"
"""
    plugin_writer(tmp_path, "simple_events", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test events without explicit data
    results = mgr.dispatch_event("startup")
    assert "System started" in results
    
    results = mgr.dispatch_event("shutdown")
    assert "System stopped" in results


def test_event_chain_processing(tmp_path: Path, plugin_writer):
    """Test that events can trigger other events"""
    body = """
from plugflow import BasePlugin

class ChainPlugin(BasePlugin):
    name = "chain"
    
    def on_event(self, event, data, manager):
        if event == "start_chain":
            # Trigger another event
            manager.dispatch_event("chain_step", {"step": 1})
            return "Chain started"
        elif event == "chain_step":
            step = data.get("step", 0)
            if step < 3:
                manager.dispatch_event("chain_step", {"step": step + 1})
            return f"Step {step} completed"
"""
    plugin_writer(tmp_path, "chain_events", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Start the chain
    results = mgr.dispatch_event("start_chain")
    assert "Chain started" in results
    
    # The chain should have been processed automatically
    # Note: This is a basic test - in practice, you might want to
    # implement more sophisticated chain handling


def test_event_error_handling(tmp_path: Path, plugin_writer):
    """Test that event errors are isolated"""
    body = """
from plugflow import BasePlugin

class GoodEventPlugin(BasePlugin):
    name = "good_event"
    
    def on_event(self, event, data, manager):
        if event == "test_event":
            return "good_response"

class BadEventPlugin(BasePlugin):
    name = "bad_event"
    
    def on_event(self, event, data, manager):
        if event == "test_event":
            raise Exception("Event processing error!")
"""
    plugin_writer(tmp_path, "error_events", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Should get response from good plugin, bad plugin error should be caught
    results = mgr.dispatch_event("test_event")
    
    # Should have one successful result
    assert len([r for r in results if r is not None]) == 1
    assert "good_response" in results
