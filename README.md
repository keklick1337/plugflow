# PlugFlow

A powerful and flexible Python plugin system that enables dynamic loading, hot-reloading, and management of plugins in your applications. Build extensible software with ease!

[![Python Version](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://python.org) [![Python Version](https://img.shields.io/badge/python-3.9%2B-lime.svg)](https://python.org) [![Python Version](https://img.shields.io/badge/python-3.10%2B-red.svg)](https://python.org) [![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org) [![Python Version](https://img.shields.io/badge/python-3.12%2B-green.svg)](https://python.org) [![Python Version](https://img.shields.io/badge/python-3.13%2B-lime.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Dynamic Plugin Loading**: Load plugins at runtime from files or directories
- **Hot Reload**: Automatically detect and reload plugin changes during development
- **Event System**: Inter-plugin communication through events and hooks
- **Lifecycle Management**: Complete plugin lifecycle with load/unload hooks
- **Type Safety**: Full type hints support for better development experience
- **Error Isolation**: Plugin errors don't crash your application
- **Package Support**: Support for both single-file and package-style plugins
- **Priority System**: Control plugin loading order with priority settings
- **Context Sharing**: Share application context between plugins
- **Framework Agnostic**: Works with any Python application or framework

## Installation

Install PlugFlow using pip:

```bash
pip install plugflow
```

Or install from source:

```bash
git clone https://github.com/keklick1337/plugflow.git
cd plugflow
pip install -e .
```

## Quick Start

### Basic Usage

```python
from plugflow import PluginManager

# Create plugin manager with plugins directory
manager = PluginManager(plugins_paths=["plugins/"])

# Load all plugins from configured paths
manager.load_all()

# Process a command through plugins
result = manager.handle_command("hello", "world")
print(result)  # Output from plugin that handles "hello" command

# Send events to plugins
manager.dispatch_event("user_login", {"user_id": 123})
```

### Creating a Simple Plugin

Create a file `plugins/greeter.py`:

```python
from plugflow import BasePlugin

class GreeterPlugin(BasePlugin):
    name = "greeter"
    version = "1.0.0"
    priority = 10  # Higher priority loads first
    
    def on_load(self, manager):
        """Called when plugin is loaded"""
        print(f"Greeter plugin v{self.version} loaded!")
    
    def handle_command(self, command: str, args: str):
        """Handle commands"""
        if command == "hello":
            return f"Hello, {args}!"
        elif command == "goodbye":
            return f"Goodbye, {args}!"
        return None  # Command not handled
    
    def on_event(self, event: str, data, manager):
        """Handle events from other plugins"""
        if event == "user_login":
            print(f"User {data['user_id']} logged in!")
```

### Package-Style Plugin

Create a directory `plugins/advanced_greeter/`:

```
plugins/advanced_greeter/
├── __init__.py
├── handlers.py
└── utils.py
```

`plugins/advanced_greeter/__init__.py`:
```python
from plugflow import BasePlugin
from .handlers import CommandHandler
from .utils import format_message

class AdvancedGreeterPlugin(BasePlugin):
    name = "advanced_greeter"
    version = "2.0.0"
    
    def __init__(self):
        super().__init__()
        self.handler = CommandHandler()
    
    def handle_command(self, command: str, args: str):
        if command in ["greet", "welcome"]:
            return self.handler.handle_greeting(command, args)
        return None
```

## Core Components

### PluginManager

The main class that manages plugin lifecycle and coordination:

```python
from plugflow import PluginManager

manager = PluginManager(
    auto_reload=True,    # Enable hot reload
    context={"app": my_app}  # Share context with plugins
)

# Load plugins
manager.load_plugin("path/to/plugin.py")
manager.load_all()  # Load all plugins from configured paths

# Manage plugins
manager.reload_plugin("plugin_name")
manager.unload_plugin("plugin_name")

# Plugin communication
result = manager.handle_command("command", "args")
manager.dispatch_event("event_name", data)

# Get plugin information
plugins = manager.list_plugins()
plugin = manager.get_plugin("plugin_name")
```

### BasePlugin

Base class for all plugins:

```python
from plugflow import BasePlugin
from typing import Optional, Any

class MyPlugin(BasePlugin):
    name = "my_plugin"           # Required: unique plugin name
    version = "1.0.0"           # Required: plugin version
    priority = 10               # Optional: loading priority (higher first)
    dependencies = ["other"]    # Optional: plugin dependencies
    
    def on_load(self, manager) -> None:
        """Called when plugin is loaded"""
        pass
    
    def on_unload(self, manager) -> None:
        """Called when plugin is unloaded"""
        pass
    
    def handle_command(self, command: str, args: str) -> Optional[str]:
        """Handle commands - return result or None if not handled"""
        return None
    
    def filter_message(self, text: str) -> Optional[str]:
        """Filter/modify messages - return modified text or None"""
        return None
    
    def on_event(self, event: str, data: Any, manager) -> None:
        """Handle events from other plugins"""
        pass
```

## Advanced Features

### Hot Reload

Enable automatic plugin reloading during development:

```python
manager = PluginManager(
    plugins_paths=["plugins/"],
    hot_reload=True  # Enable hot reload for development
)
manager.load_all()

# Now edit your plugins - changes will be detected automatically!
```

### Context Sharing

Share application state and resources with plugins:

```python
# Create manager with shared context
context = {
    "database": db_connection,
    "config": app_config,
    "logger": logger
}
manager = PluginManager(context=context)

# Plugins can access context
class DatabasePlugin(BasePlugin):
    def on_load(self, manager):
        db = self.context.get("database")
        logger = self.context.get("logger")
        logger.info("Database plugin connected!")
```

### Event System

Plugins can communicate through events:

```python
# Plugin A sends event
class PublisherPlugin(BasePlugin):
    def handle_command(self, command, args):
        if command == "notify":
            # Dispatch event to all plugins
            self.manager.dispatch_event("notification", {
                "message": args,
                "timestamp": time.time()
            })

# Plugin B receives event
class SubscriberPlugin(BasePlugin):
    def on_event(self, event, data, manager):
        if event == "notification":
            print(f"Received: {data['message']}")
```

### Plugin Dependencies

Specify plugin loading order with dependencies:

```python
class DatabasePlugin(BasePlugin):
    name = "database"
    priority = 100  # Load first

class UserPlugin(BasePlugin):
    name = "user_manager"
    dependencies = ["database"]  # Load after database
    
    def on_load(self, manager):
        # Database plugin is guaranteed to be loaded
        db_plugin = manager.get_plugin("database")
```

### Error Handling

Plugins are isolated - errors don't crash your application:

```python
class FaultyPlugin(BasePlugin):
    def handle_command(self, command, args):
        if command == "crash":
            raise Exception("Plugin error!")
        return None

# Manager handles plugin errors gracefully
try:
    result = manager.handle_command("crash", "")
except Exception as e:
    print(f"Plugin error handled: {e}")
# Application continues running
```

## Example Applications

PlugFlow includes comprehensive examples in the `examples/` directory:

### 1. CLI Tool (`examples/cli_tool/`)

Professional command-line utility with plugin-based commands:

```bash
cd examples/cli_tool
python cli.py help          # Show all commands
python cli.py hash md5 "test"  # Cryptographic operations
python cli.py tree . 2      # File system utilities
```

**Features**: Type-safe plugins, clean output, debug mode, comprehensive help

### 2. Telegram Bot (`examples/tg_stub/`)

Production-ready bot simulation with advanced features:

```bash
cd examples/tg_stub
python bot.py              # Clean production mode
python bot.py --debug      # Development mode with logs
```

**Features**: Command handling, message filtering, dynamic help, hot reload

### 3. GUI Application (`examples/tk_app/`)

Sophisticated tkinter application with plugin integration:

```bash
cd examples/tk_app
python app.py
```

**Features**: Menu integration, real-time logging, file operations, event system

### 4. Web Server (`examples/web_server/`)

Flask-based web application with plugin routes:

```bash
cd examples/web_server
python server.py
```

**Features**: Dynamic routing, middleware, API endpoints, template system

## Plugin Development Guide

### Basic Plugin Structure

```python
from plugflow import BasePlugin
from typing import Optional

class MyPlugin(BasePlugin):
    # Plugin metadata
    name = "my_plugin"
    version = "1.0.0"
    description = "My awesome plugin"
    author = "Your Name"
    
    def on_load(self, manager):
        """Initialize plugin resources"""
        self.data = {}
        print(f"{self.name} loaded!")
    
    def on_unload(self, manager):
        """Clean up plugin resources"""
        self.data.clear()
        print(f"{self.name} unloaded!")
    
    def handle_command(self, command: str, args: str) -> Optional[str]:
        """Process commands"""
        commands = {
            "status": self._status,
            "set": self._set_data,
            "get": self._get_data
        }
        
        if command in commands:
            return commands[command](args)
        return None
    
    def _status(self, args: str) -> str:
        return f"Plugin {self.name} v{self.version} - {len(self.data)} items"
    
    def _set_data(self, args: str) -> str:
        key, value = args.split("=", 1)
        self.data[key] = value
        return f"Set {key} = {value}"
    
    def _get_data(self, args: str) -> str:
        return self.data.get(args, "Key not found")
```

### Best Practices

1. **Error Handling**: Always handle exceptions gracefully
2. **Resource Cleanup**: Implement `on_unload` for proper cleanup
3. **Type Hints**: Use type annotations for better code quality
4. **Documentation**: Document your plugin's commands and features
5. **Testing**: Create unit tests for your plugins
6. **Versioning**: Use semantic versioning for your plugins

### Plugin Testing

```python
import unittest
from plugflow import PluginManager
from my_plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.manager = PluginManager(plugins_paths=[])
        self.plugin = MyPlugin()
        self.manager.register_plugin(self.plugin)
    
    def test_command_handling(self):
        result = self.plugin.handle_command("status", "")
        self.assertIn("Plugin my_plugin", result)
    
    def test_data_operations(self):
        self.plugin.handle_command("set", "key=value")
        result = self.plugin.handle_command("get", "key")
        self.assertEqual(result, "value")
```

## API Reference

### PluginManager

#### Methods

- `load_plugin(path: str) -> bool`: Load a plugin from file
- `load_all() -> int`: Load all plugins from configured paths
- `unload_plugin(name: str) -> bool`: Unload a plugin by name
- `reload_plugin(name: str) -> bool`: Reload a plugin
- `handle_command(command: str, args: str) -> Optional[str]`: Process command through plugins
- `dispatch_event(event: str, data: Any) -> None`: Send event to all plugins
- `list_plugins() -> List[str]`: Get list of loaded plugin names
- `get(name: str) -> Optional[BasePlugin]`: Get plugin instance by name
- `get_plugin(name: str) -> Optional[BasePlugin]`: Get plugin by name

#### Properties

- `auto_reload: bool`: Enable/disable hot reload
- `context: Dict[str, Any]`: Shared context dictionary

### BasePlugin

#### Required Attributes

- `name: str`: Unique plugin identifier
- `version: str`: Plugin version

#### Optional Attributes

- `priority: int`: Loading priority (default: 0)
- `dependencies: List[str]`: Required plugins
- `description: str`: Plugin description
- `author: str`: Plugin author

#### Methods

- `on_load(manager: PluginManager) -> None`: Initialization hook
- `on_unload(manager: PluginManager) -> None`: Cleanup hook
- `handle_command(command: str, args: str) -> Optional[str]`: Command handler
- `filter_message(text: str) -> Optional[str]`: Message filter
- `on_event(event: str, data: Any, manager: PluginManager) -> None`: Event handler

## Performance Tips

1. **Lazy Loading**: Load plugins only when needed
2. **Caching**: Cache plugin results for expensive operations
3. **Priority Optimization**: Use priorities to control loading order
4. **Resource Management**: Properly clean up plugin resources
5. **Event Filtering**: Only subscribe to relevant events

## Troubleshooting

### Common Issues

**Plugin Not Loading**
```python
# Check plugin file syntax
manager.load_plugin("plugin.py")  # Returns False if failed

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Import Errors**
```python
# Ensure plugin directory is in Python path
import sys
sys.path.append("plugins")
```

**Hot Reload Not Working**
```python
# Ensure auto_reload is enabled
manager = PluginManager(auto_reload=True)

# Check file permissions and watching capability
```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = PluginManager(auto_reload=True)
# Now you'll see detailed plugin loading information
```

## Contributing

We welcome contributions!

### Development Setup

```bash
git clone https://github.com/keklick1337/plugflow.git
cd plugflow
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with love for the Python community**

PlugFlow makes it easy to create extensible applications. Start building your plugin ecosystem today!
