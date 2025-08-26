"""
Basic smoke tests for PlugFlow
This file contains minimal tests to verify basic functionality.
More comprehensive tests are in the unit/ and integration/ directories.
"""
import time
from pathlib import Path
import textwrap
import pytest
from plugflow import PluginManager, BasePlugin


def write_plugin(tmpdir: Path, name: str, body: str, as_pkg=False):
    """Helper function to write test plugins"""
    if as_pkg:
        pkg = tmpdir / name
        pkg.mkdir()
        (pkg / "__init__.py").write_text(textwrap.dedent(body), encoding="utf-8")
        return pkg
    else:
        f = tmpdir / f"{name}.py"
        f.write_text(textwrap.dedent(body), encoding="utf-8")
        return f


def test_basic_loading(tmp_path: Path):
    """Test that plugins can be loaded"""
    body = """
from plugflow import BasePlugin
class TestPlugin(BasePlugin):
    name = "test"
    def on_event(self, event, data, manager): 
        if event == "ping": 
            return "pong"
"""
    write_plugin(tmp_path, "test_plugin", body)

    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()

    assert "test" in mgr.list_plugins()
    res = mgr.dispatch_event("ping")
    assert "pong" in res


def test_basic_commands(tmp_path: Path):
    """Test basic command handling"""
    body = """
from plugflow import BasePlugin
class CmdPlugin(BasePlugin):
    name = "cmd"
    def handle_command(self, command, args):
        if command == "hello":
            return "hi " + args
"""
    write_plugin(tmp_path, "cmd_plugin", body)

    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()

    out = mgr.handle_message("/hello world")
    assert "hi world" in out


def test_hot_reload(tmp_path: Path):
    """Test hot reload functionality"""
    mgr = PluginManager([str(tmp_path)], hot_reload=True, poll_interval=0.2)
    mgr.load_all()

    # Add new plugin on the fly
    body = """
from plugflow import BasePlugin
class HotPlugin(BasePlugin):
    name = "hot"
    def handle_command(self, command, args):
        if command == "test":
            return "hot_loaded"
"""
    write_plugin(tmp_path, "hot_plugin", body)
    time.sleep(0.6)  # wait for watcher

    assert "hot" in mgr.list_plugins()
    out = mgr.handle_message("/test")
    assert "hot_loaded" in out
    
    mgr.stop()


def test_default_empty_paths():
    """Test manager with no plugin paths"""
    mgr = PluginManager()
    assert mgr.paths == []
    assert mgr.list_plugins() == []
