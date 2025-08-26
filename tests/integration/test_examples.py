"""
Integration tests based on CLI tool example
"""
import pytest
from pathlib import Path
from plugflow import PluginManager, BasePlugin


def test_cli_like_plugin_system(tmp_path: Path, plugin_writer):
    """Test a CLI-like plugin system similar to the examples"""
    
    # Create a crypto plugin like in examples
    crypto_plugin = """
from plugflow import BasePlugin
import hashlib
import base64

class CryptoPlugin(BasePlugin):
    name = "crypto"
    version = "1.0.0"
    description = "Cryptographic utilities"
    
    def handle_command(self, command, args):
        if command == "hash":
            if not args:
                return "Usage: hash <text>"
            return hashlib.sha256(args.encode()).hexdigest()
        elif command == "base64":
            if not args:
                return "Usage: base64 <text>"
            return base64.b64encode(args.encode()).decode()
        return None
"""
    
    # Create a file utils plugin
    fileutils_plugin = """
from plugflow import BasePlugin
import os

class FileUtilsPlugin(BasePlugin):
    name = "fileutils"
    version = "1.0.0"
    description = "File utilities"
    
    def handle_command(self, command, args):
        if command == "pwd":
            return os.getcwd()
        elif command == "ls":
            try:
                path = args if args else "."
                items = os.listdir(path)
                return "\\n".join(items)
            except:
                return "Error listing directory"
        return None
"""
    
    plugin_writer(tmp_path, "crypto", crypto_plugin)
    plugin_writer(tmp_path, "fileutils", fileutils_plugin)
    
    # Create CLI-like manager
    mgr = PluginManager([str(tmp_path)], context={"cli_mode": True})
    mgr.load_all()
    
    # Test crypto commands
    result = mgr.handle_message("/hash hello")
    assert len(result) == 1
    assert len(result[0]) == 64  # SHA256 hex length
    
    result = mgr.handle_message("/base64 hello")
    assert "aGVsbG8=" in result  # base64 of "hello"
    
    # Test file commands
    result = mgr.handle_message("/pwd")
    assert len(result) == 1
    import os
    # Should be a path - check that it's an absolute path
    assert os.path.isabs(result[0])  # Should be an absolute path
    
    # Test error handling
    result = mgr.handle_message("/hash")
    assert "Usage: hash" in result[0]


def test_web_server_like_plugins(tmp_path: Path, plugin_writer):
    """Test web server-like plugin system"""
    
    # Echo plugin like in web server example
    echo_plugin = """
from plugflow import BasePlugin

class EchoPlugin(BasePlugin):
    name = "echo"
    version = "1.0.0"
    
    def process_request(self, path, data):
        if path == "/echo":
            return {"status": "success", "echo": data.get("message", "")}
        return None
"""
    
    # Reverse plugin
    reverse_plugin = """
from plugflow import BasePlugin

class ReversePlugin(BasePlugin):
    name = "reverse"
    version = "1.0.0"
    
    def process_request(self, path, data):
        if path == "/reverse":
            text = data.get("text", "")
            return {"status": "success", "reversed": text[::-1]}
        return None
"""
    
    plugin_writer(tmp_path, "echo", echo_plugin)
    plugin_writer(tmp_path, "reverse", reverse_plugin)
    
    mgr = PluginManager([str(tmp_path)], context={"server_mode": True})
    mgr.load_all()
    
    # Simulate web requests using broadcast
    echo_results = mgr.broadcast("process_request", "/echo", {"message": "hello world"})
    valid_echo = [r for r in echo_results if r is not None]
    assert len(valid_echo) == 1
    assert valid_echo[0]["echo"] == "hello world"
    
    reverse_results = mgr.broadcast("process_request", "/reverse", {"text": "hello"})
    valid_reverse = [r for r in reverse_results if r is not None]
    assert len(valid_reverse) == 1
    assert valid_reverse[0]["reversed"] == "olleh"


def test_chat_bot_like_system(tmp_path: Path, plugin_writer):
    """Test chat bot-like plugin system similar to Telegram example"""
    
    # Command echo plugin
    cmd_echo = """
from plugflow import BasePlugin

class CmdEchoPlugin(BasePlugin):
    name = "cmd_echo"
    version = "1.0.0"
    
    def handle_command(self, command, args):
        if command == "echo":
            return f"You said: {args}"
        elif command == "ping":
            return "pong"
        return None
"""
    
    # Profanity filter
    profanity_filter = """
from plugflow import BasePlugin

class ProfanityFilter(BasePlugin):
    name = "profanity_filter"
    priority = 100  # High priority to filter first
    
    def filter_message(self, text):
        # Simple profanity filter
        bad_words = ["spam", "badword"]
        filtered = text
        for word in bad_words:
            filtered = filtered.replace(word, "***")
        return filtered
"""
    
    # Utils plugin
    cmd_utils = """
from plugflow import BasePlugin
import random
import time

class CmdUtilsPlugin(BasePlugin):
    name = "cmd_utils"
    version = "1.0.0"
    
    def handle_command(self, command, args):
        if command == "random":
            try:
                max_num = int(args) if args else 100
                return str(random.randint(1, max_num))
            except:
                return "Usage: random [max_number]"
        elif command == "time":
            return str(int(time.time()))
        return None
"""
    
    plugin_writer(tmp_path, "cmd_echo", cmd_echo)
    plugin_writer(tmp_path, "profanity_filter", profanity_filter)
    plugin_writer(tmp_path, "cmd_utils", cmd_utils)
    
    mgr = PluginManager([str(tmp_path)], context={"bot_mode": True})
    mgr.load_all()
    
    # Test message filtering
    result = mgr.handle_message("this contains spam here")
    # The profanity filter should have processed the message before any handlers
    
    # Test commands
    result = mgr.handle_message("/echo hello world")
    assert "You said: hello world" in result
    
    result = mgr.handle_message("/ping")
    assert "pong" in result
    
    result = mgr.handle_message("/random 10")
    assert len(result) == 1
    assert result[0].isdigit()
    
    result = mgr.handle_message("/time")
    assert len(result) == 1
    assert result[0].isdigit()


def test_gui_app_like_system(tmp_path: Path, plugin_writer):
    """Test GUI application-like plugin system"""
    
    # Text analysis plugin
    text_analysis = """
from plugflow import BasePlugin

class TextAnalysisPlugin(BasePlugin):
    name = "text_analysis"
    version = "1.0.0"
    
    def analyze_text(self, text):
        words = text.split()
        return {
            "word_count": len(words),
            "char_count": len(text),
            "char_count_no_spaces": len(text.replace(" ", "")),
            "line_count": len(text.split("\\n"))
        }
"""
    
    # Text styling plugin
    text_styling = """
from plugflow import BasePlugin

class TextStylingPlugin(BasePlugin):
    name = "text_styling"
    version = "1.0.0"
    
    def apply_style(self, text, style):
        if style == "uppercase":
            return text.upper()
        elif style == "lowercase":
            return text.lower()
        elif style == "title":
            return text.title()
        elif style == "reverse":
            return text[::-1]
        return text
"""
    
    plugin_writer(tmp_path, "text_analysis", text_analysis)
    plugin_writer(tmp_path, "text_styling", text_styling)
    
    mgr = PluginManager([str(tmp_path)], context={"gui_mode": True})
    mgr.load_all()
    
    # Test text analysis
    analysis_results = mgr.broadcast("analyze_text", "Hello world\nThis is a test")
    valid_analysis = [r for r in analysis_results if r is not None]
    assert len(valid_analysis) == 1
    
    stats = valid_analysis[0]
    assert stats["word_count"] == 6
    assert stats["char_count"] > 0
    assert stats["line_count"] == 2
    
    # Test text styling
    styling_results = mgr.broadcast("apply_style", "hello world", "uppercase")
    valid_styling = [r for r in styling_results if r is not None]
    assert len(valid_styling) == 1
    assert valid_styling[0] == "HELLO WORLD"
