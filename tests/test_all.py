
import sys, time
from pathlib import Path
import textwrap

import pytest

from plugflow import PluginManager, BasePlugin

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

def test_load_file_and_package(tmp_path: Path):
    # file plugin
    file_body = """
from plugflow import BasePlugin
class A(BasePlugin):
    name = "A"
    def on_event(self, event, data, manager): 
        if event == "ping": 
            return "pong"
"""
    write_plugin(tmp_path, "a_plugin", file_body)

    # package plugin (via register)
    pkg_body = """
from plugflow import BasePlugin
class B(BasePlugin):
    name = "B"
def register(context):
    return [B]
"""
    write_plugin(tmp_path, "b_pkg", pkg_body, as_pkg=True)

    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()

    assert set(mgr.list_plugins()) == {"A", "B"}
    res = mgr.dispatch_event("ping")
    assert "pong" in res

def test_message_flow_and_commands(tmp_path: Path):
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
    write_plugin(tmp_path, "mix", body)

    mgr = PluginManager([str(tmp_path)])
    mgr.load_all()

    out = mgr.handle_message("this is bad")
    assert "this is b*d" not in out  # filter changes input but doesn't generate responses
    out = mgr.handle_message("/hello world")
    assert "hi world" in out

def test_hot_add(tmp_path: Path):
    mgr = PluginManager([str(tmp_path)], hot_reload=True, poll_interval=0.2)
    mgr.load_all()

    # Add new plugin on the fly
    body = """
from plugflow import BasePlugin
class H(BasePlugin):
    name = "Hot"
    def handle_command(self, command, args):
        if command == "hot":
            return "loaded"
"""
    write_plugin(tmp_path, "hot_plg", body)
    time.sleep(0.6)  # wait for watcher

    assert "Hot" in mgr.list_plugins()
    out = mgr.handle_message("/hot")
    assert "loaded" in out
