#!/usr/bin/env python3
"""
Extensible CLI tool with PlugFlow plugin system.
Demonstrates how to create a command-line tool that can be extended with plugins.

Usage:
    python cli.py <command> [args...]     # Run in normal mode (no logs)
    python cli.py --debug <command>       # Run in debug mode (with logs)
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, cast
from plugflow import PluginManager, BasePlugin
from cli_plugin import CLIPlugin

PLUGINS_DIR = Path(__file__).parent / "plugins"

def setup_logging(debug_mode: bool) -> None:
    """Setup logging based on debug mode"""
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        # Enable PlugFlow debug logging explicitly
        logging.getLogger('plugflow').setLevel(logging.DEBUG)
    else:
        # Disable all logging for clean CLI output
        logging.disable(logging.CRITICAL)
        logging.getLogger('plugflow').disabled = True

class CLITool:
    def __init__(self, debug_mode: bool = False) -> None:
        setup_logging(debug_mode)
        
        self.plugin_manager = PluginManager(
            plugins_paths=[str(PLUGINS_DIR)],
            context={"cli": self, "debug": debug_mode},
            hot_reload=debug_mode,  # Only enable hot reload in debug mode
        )
        self.plugin_manager.load_all()

    def get_available_commands(self) -> Dict[str, Dict[str, str]]:
        """Get all available commands from plugins"""
        commands: Dict[str, Dict[str, str]] = {}
        for plugin_name in self.plugin_manager.list_plugins():
            plugin = self.plugin_manager.get(plugin_name)
            if plugin and hasattr(plugin, 'get_cli_commands'):
                try:
                    # Cast to CLIPlugin for proper type hints
                    cli_plugin = cast(CLIPlugin, plugin)
                    plugin_commands = cli_plugin.get_cli_commands()
                    if plugin_commands:
                        commands.update(plugin_commands)
                except Exception as e:
                    print(f"Error getting commands from {plugin_name}: {e}")
        return commands

    def execute_command(self, command: str, args: List[str]) -> Optional[bool]:
        """Execute a command through plugins"""
        for plugin_name in self.plugin_manager.list_plugins():
            plugin = self.plugin_manager.get(plugin_name)
            if plugin and hasattr(plugin, 'execute_cli_command'):
                try:
                    # Cast to CLIPlugin for proper type hints
                    cli_plugin = cast(CLIPlugin, plugin)
                    result = cli_plugin.execute_cli_command(command, args)
                    if result is not None:
                        return result
                except Exception as e:
                    print(f"Error executing command in {plugin_name}: {e}")
                    return False
        return None

    def run(self, args: Optional[List[str]] = None) -> None:
        """Main CLI entry point"""
        if args is None:
            args = sys.argv[1:]

        if not args:
            self.show_help()
            return

        command = args[0]
        command_args = args[1:] if len(args) > 1 else []

        if command in ['--help', '-h', 'help']:
            self.show_help()
            return

        if command == '--list-plugins':
            self.list_plugins()
            return

        # Try to execute command via plugins
        result = self.execute_command(command, command_args)
        if result is None:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
            sys.exit(1)
        elif result is False:
            sys.exit(1)

    def show_help(self) -> None:
        """Show help with available commands"""
        print("PlugFlow CLI Tool - Extensible command-line utility")
        print()
        print("Built-in commands:")
        print("  help, --help, -h    Show this help message")
        print("  --list-plugins      List loaded plugins")
        print()
        
        commands = self.get_available_commands()
        if commands:
            print("Plugin commands:")
            for cmd, info in commands.items():
                description = info.get('description', 'No description')
                usage = info.get('usage', cmd)
                print(f"  {usage:<20} {description}")
        else:
            print("No plugin commands available")
        print()
        print(f"Loaded plugins: {', '.join(self.plugin_manager.list_plugins())}")

    def list_plugins(self) -> None:
        """List all loaded plugins with details"""
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            print("No plugins loaded")
            return

        print("Loaded plugins:")
        for plugin_name in plugins:
            plugin = self.plugin_manager.get(plugin_name)
            if plugin:
                version = getattr(plugin, 'version', 'unknown')
                priority = getattr(plugin, 'priority', 100)
                print(f"  {plugin_name} (v{version}, priority: {priority})")

if __name__ == "__main__":
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
    tool = CLITool(debug_mode=debug_mode)
    tool.run()
