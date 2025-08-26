"""
Tests for message handling and command processing
"""
import pytest
from pathlib import Path
from plugflow import PluginManager, BasePlugin


def test_message_flow_and_commands(tmp_path: Path, plugin_writer):
    """Test message filtering and command handling"""
    body = """
from plugflow import BasePlugin
class F(BasePlugin):
    name = "Filter"
    priority = 5
    def filter_message(self, text): 
        return text.replace("bad", "b*d")
class C(BasePlugin):
    name = "Cmd"
    def handle_command(self, command, args):
        if command == "hello":
            return "hi " + args
"""
    plugin_writer(tmp_path, "mix", body)

    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()

    out = mgr.handle_message("this is bad")
    assert "this is b*d" not in out  # filter changes input but doesn't generate responses
    out = mgr.handle_message("/hello world")
    assert "hi world" in out


def test_command_handlers(tmp_path: Path, plugin_writer):
    """Test command handling functionality"""
    body = """
from plugflow import BasePlugin

class EchoPlugin(BasePlugin):
    name = "echo"
    
    def handle_command(self, command, args):
        if command == "echo":
            return f"Echo: {args}"
        return None

class MathPlugin(BasePlugin):
    name = "math"
    
    def handle_command(self, command, args):
        if command == "add":
            try:
                nums = [int(x) for x in args.split()]
                return str(sum(nums))
            except:
                return "Invalid numbers"
        return None
"""
    plugin_writer(tmp_path, "commands", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test echo command
    result = mgr.handle_message("/echo hello world")
    assert "Echo: hello world" in result
    
    # Test math command
    result = mgr.handle_message("/add 1 2 3 4")
    assert "10" in result
    
    # Test invalid command
    result = mgr.handle_message("/unknown")
    assert result == []


def test_multiple_message_handlers(tmp_path: Path, plugin_writer):
    """Test multiple plugins handling the same message"""
    body = """
from plugflow import BasePlugin

class EchoPlugin(BasePlugin):
    name = "echo"
    
    def on_message(self, text, manager):
        if "echo" in text.lower():
            return f"Echo: {text}"

class UpperPlugin(BasePlugin):
    name = "upper"
    
    def on_message(self, text, manager):
        if "upper" in text.lower():
            return text.upper()
            
class ListPlugin(BasePlugin):
    name = "list"
    
    def on_message(self, text, manager):
        if "list" in text.lower():
            return ["item1", "item2", "item3"]
"""
    plugin_writer(tmp_path, "message_handlers", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test echo
    result = mgr.handle_message("please echo this")
    assert len(result) == 1
    assert "Echo: please echo this" in result
    
    # Test upper
    result = mgr.handle_message("make this upper")
    assert "MAKE THIS UPPER" in result
    
    # Test list response
    result = mgr.handle_message("show me a list")
    assert "item1" in result
    assert "item2" in result
    assert "item3" in result


def test_message_filtering(tmp_path: Path, plugin_writer):
    """Test message filtering chain"""
    body = """
from plugflow import BasePlugin

class ProfanityFilter(BasePlugin):
    name = "profanity"
    priority = 100  # High priority to run first
    
    def filter_message(self, text):
        return text.replace("badword", "***")

class UpperCaseFilter(BasePlugin):
    name = "uppercase"
    priority = 50  # Medium priority
    
    def filter_message(self, text):
        if text.startswith("SHOUT:"):
            return text[6:].upper()
        return text

class EchoHandler(BasePlugin):
    name = "echo_handler"
    
    def on_message(self, text, manager):
        return f"Processed: {text}"
"""
    plugin_writer(tmp_path, "filters", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    # Test profanity filter
    result = mgr.handle_message("this contains badword here")
    assert "Processed: this contains *** here" in result
    
    # Test chained filters
    result = mgr.handle_message("SHOUT:hello world")
    assert "Processed: HELLO WORLD" in result


def test_broadcast_method(tmp_path: Path, plugin_writer):
    """Test broadcasting method calls to all plugins"""
    body = """
from plugflow import BasePlugin

class BroadcastPlugin1(BasePlugin):
    name = "broadcast1"
    
    def custom_method(self, value):
        return f"plugin1_{value}"

class BroadcastPlugin2(BasePlugin):
    name = "broadcast2"
    
    def custom_method(self, value):
        return f"plugin2_{value}"
        
class BroadcastPlugin3(BasePlugin):
    name = "broadcast3"
    
    # This plugin doesn't have custom_method - should be ignored
    pass
"""
    plugin_writer(tmp_path, "broadcast", body)
    
    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()
    
    results = mgr.broadcast("custom_method", "test")
    assert len(results) == 2
    assert "plugin1_test" in results
    assert "plugin2_test" in results
