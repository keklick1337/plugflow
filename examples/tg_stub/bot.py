
#!/usr/bin/env python3
"""
Telegram Bot Stub - PlugFlow Example

A demonstration of how to use PlugFlow with a Telegram-style bot.
Supports hot-reloading plugins and command handling.

Usage:
    python bot.py          # Run in normal mode (minimal logs)
    python bot.py --debug  # Run in debug mode (full logs)
    python bot.py -v       # Run in verbose mode (full logs)
"""

import sys
import time
import argparse
import logging
from plugflow import PluginManager

PLUGINS_DIR = __file__.replace("bot.py", "plugins")

def setup_logging(debug_mode):
    """Setup logging based on debug mode"""
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        # Enable PlugFlow debug logging explicitly
        logging.getLogger('plugflow').setLevel(logging.DEBUG)
        print("Debug mode enabled - full plugin logs will be shown")
    else:
        # Completely disable logging for normal mode
        logging.disable(logging.CRITICAL)
        # Also specifically disable the plugflow logger
        logging.getLogger('plugflow').disabled = True

def show_help(manager):
    """Show help information including loaded plugins"""
    help_text = [
        "Telegram Bot Stub - PlugFlow Example",
        "=" * 40,
        "",
        "Available Commands:",
        "/help - Show this help message",
        "",
        "Loaded Plugins:",
    ]
    
    plugins = manager.list_plugins()
    if plugins:
        for plugin_name in plugins:
            # Get plugin instance
            plugin_instance = manager.get(plugin_name)
            if plugin_instance:
                # Get plugin info
                version = getattr(plugin_instance, 'version', 'unknown')
                description = getattr(plugin_instance, 'description', 'No description available')
                
                help_text.append(f"  • {plugin_name} (v{version})")
                help_text.append(f"    {description}")
                
                # Show commands this plugin handles
                if hasattr(plugin_instance, 'get_commands'):
                    commands = plugin_instance.get_commands()
                    if commands:
                        help_text.append(f"    Commands: {', '.join(commands)}")
                help_text.append("")
    else:
        help_text.append("  No plugins loaded")
        help_text.append("")
    
    help_text.extend([
        "Plugin Features:",
        "  • Hot reload - plugins update automatically (debug mode only)",
        "  • Command handling - type /command to execute plugin commands",
        "  • Message filtering - plugins can process and modify messages",
        "",
        "Debug Mode:",
        "  Run with --debug or -v to enable:",
        "  • Detailed plugin logs",
        "  • Hot reload functionality",
        "  • Plugin development features",
        "",
        "Type 'quit' or press Ctrl+C to exit"
    ])
    
    return "\n".join(help_text)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Telegram Bot Stub with PlugFlow')
    parser.add_argument('--debug', '-v', action='store_true', 
                       help='Enable debug mode with full plugin logs')
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Initialize plugin manager
    manager = PluginManager(
        plugins_paths=[PLUGINS_DIR],
        context={"bot": "telegram_stub", "debug": args.debug},
        hot_reload=args.debug,  # Only enable hot reload in debug mode
        poll_interval=2.0,  # Less aggressive polling
    )
    
    # Load plugins
    manager.load_all()
    
    # Startup message
    print("Telegram Bot Stub (PlugFlow Example)")
    print(f"Loaded {len(manager.list_plugins())} plugin(s)")
    if args.debug:
        print("Debug mode: ON (full logs + hot reload)")
    else:
        print("Debug mode: OFF (use --debug for full logs and hot reload)")
    print("Type /help for available commands, or 'quit' to exit")
    print("-" * 50)

    # Main bot loop
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down bot...")
            break

        if not line:
            continue
            
        # Handle quit command
        if line.lower() in ['quit', 'exit', '/quit']:
            print("Goodbye!")
            break
            
        # Handle help command
        if line.lower() in ['/help', 'help']:
            print(show_help(manager))
            continue

        # Process message through plugins
        responses = manager.handle_message(line)
        
        # Display responses
        for r in responses:
            if r:
                print(f"[BOT]: {r}")
        
        # If no responses, show a default message for unknown commands
        if not any(responses) and line.startswith('/'):
            print("[BOT]: Unknown command. Type /help for available commands.")

if __name__ == "__main__":
    main()
