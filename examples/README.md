# PlugFlow Examples

This directory contains comprehensive examples demonstrating various use cases of the PlugFlow plugin system. Each example showcases different aspects of plugin development and integration across different application types.

## Example Applications

### 1. Tkinter GUI Application (`tk_app/`)

**Purpose**: Demonstrates advanced GUI integration with a sophisticated tkinter application featuring comprehensive plugin-based functionality.

**Key Features**:
- Advanced menu system with plugin-generated items
- Real-time activity logging with proper text formatting
- Professional UI layout with status indicators
- Plugin help system with detailed information
- Text processing and manipulation tools
- File operations with native dialogs
- Inter-plugin communication via events
- Hot reload support for development

**Plugins Included**:
- **`cmd_reverse.py`**: Simple text reversal functionality
- **`pkg_uppercase/`**: Package-style plugin demonstrating modular structure
- **`text_styling.py`**: Advanced text formatting with color picker and symbols
- **`file_operations.py`**: File save/load operations with application state management
- **`text_analysis.py`**: Comprehensive text analysis with history and statistics

**How to Run**:
```bash
cd tk_app
python app.py
```

**What You'll See**:
- Professional GUI with menu integration
- Plugin management interface
- Real-time logging display
- Text processing capabilities
- File operation dialogs
- Help system with plugin information

**Demonstrates**:
- Complex UI integration patterns
- Plugin lifecycle management in GUI context
- Event-driven plugin communication
- Professional application architecture
- User-friendly plugin help system

---

### 2. Telegram Bot Stub (`tg_stub/`)

**Purpose**: Professional simulation of a Telegram bot with advanced plugin management, debug modes, and comprehensive command system.

**Key Features**:
- **Clean Output**: Normal mode with no log spam for production use
- **Debug Mode**: Full logging and hot reload for development (`--debug` flag)
- **Dynamic Help System**: Auto-generates help from loaded plugins
- **Smart Command Handling**: Supports all plugin commands with intelligent responses
- **Message Filtering**: Silent profanity filtering with statistics
- **Plugin Hot-Reloading**: Automatic plugin updates (debug mode only)
- **Professional UX**: Clean startup, proper error handling, graceful shutdown

**Plugins Included**:
- **`cmd_echo.py`**: Communication testing commands
  - `/echo <text>` - Echoes back the provided text
  - `/ping` - Simple connectivity test with "Pong" response
- **`filter_profanity.py`**: Advanced message filtering system
  - Silently censors inappropriate content in real-time
  - `/filter_stats` - Shows session filtering statistics
  - Debug logging for development and monitoring
- **`cmd_utils.py`**: Comprehensive utility command collection
  - `/time` - Shows current time (HH:MM:SS format)
  - `/date` - Shows current date with day name
  - `/random [max]` - Generate random numbers (default 1-100)
  - `/roll` - Roll a 6-sided die (1-6)
  - `/flip` - Flip a coin (Heads/Tails)
  - `/status` - Bot status with uptime and command count
  - `/uptime` - Detailed uptime in hours/minutes/seconds
  - `/stats` - Complete session statistics

**How to Run**:
```bash
cd tg_stub
python bot.py           # Production mode (clean, no logs)
python bot.py --debug   # Development mode (full logs + hot reload)
python bot.py -v        # Verbose mode (same as debug)
```

**Interactive Examples**:
```
> /help                    # See all available plugins and commands
> /echo Hello PlugFlow!    # Test echo functionality
> /time                    # Get current time
> /random 100             # Random number 1-100
> /roll                   # Roll a die
> /status                 # Check bot status
> this damn text          # Test profanity filter (censors to "d**n")
> /filter_stats           # See filtering statistics
> quit                    # Exit cleanly
```

**Demonstrates**:
- Production-ready bot architecture with clean output
- Development-friendly features with debug mode
- Dynamic plugin discovery and help generation
- Advanced message pipeline with filtering
- Professional bot UX with proper error handling
- Plugin lifecycle management and hot-reload

---

### 3. CLI Tool (`cli_tool/`)

**Purpose**: Extensible command-line utility demonstrating how to build professional CLI tools with plugin architecture and proper type hints.

**Key Features**:
- **Clean CLI Output**: No log spam in normal mode
- **Debug Mode**: Full logging for development (`--debug` flag)
- **Type-Safe Plugins**: Custom `CLIPlugin` base class with proper type hints
- **Modular Plugin Architecture**: Separated base class for reusability
- **Comprehensive Help System**: Auto-generated help from plugin metadata
- **Error Handling**: Proper exit codes and error messages

**Plugin Architecture**:
- **`cli_plugin.py`**: Separated base class with proper type annotations
- **Type Safety**: Full type hints for better development experience
- **Abstract Methods**: Enforced plugin interface consistency

**Plugins Included**:
- **`crypto.py`**: Cryptographic operations
  - `hash <algorithm> <text>` - Generate MD5, SHA1, SHA256, SHA512 hashes
  - `encode <text>` - Base64 encoding
  - `decode <base64_text>` - Base64 decoding
  - Supports `--no-newline` flag for precise hash matching
- **`fileutils.py`**: File system utilities
  - `size <path>` - Get file/directory size with human-readable format
  - `tree [path] [max_depth]` - Display directory tree structure
  - `find <pattern> [directory]` - Find files by pattern
  - `backup <source> [destination]` - Create file/directory backups
- **`devtools.py`**: Development utilities
  - `gitinfo [path]` - Git repository information
  - `json-format <json_string_or_file>` - JSON formatting and validation
  - `count-lines [directory]` - Count lines of code with filtering
  - `gen-readme [project_name]` - Generate README template

**How to Run**:
```bash
cd cli_tool
python cli.py help                    # Show all available commands
python cli.py hash md5 "test"         # Generate MD5 hash
python cli.py --debug hash sha256 "test"  # Debug mode with logs
python cli.py tree . 2                # Show directory tree (depth 2)
```

**What You'll See**:
- Clean command-line interface
- Comprehensive help system
- Professional error handling
- Type-safe plugin development

**Demonstrates**:
- Professional CLI tool architecture
- Type-safe plugin development with custom base classes
- Modular plugin system with separated concerns
- Clean output modes for production vs development
- Comprehensive command-line argument handling

---

### 4. Web Server (`web_server/`)

**Purpose**: Demonstrates how to integrate PlugFlow with web frameworks, creating extensible web applications with plugin-based routing and middleware.

**Key Features**:
- **Plugin-Based Routing**: Automatic route registration from plugins
- **Middleware Support**: Plugin-provided middleware for request processing
- **Template System**: Plugin-extensible template rendering
- **API Endpoints**: RESTful API endpoints via plugins
- **Static File Handling**: Plugin-managed static content
- **Development Server**: Hot reload for web development

**Plugin Architecture**:
- Route registration through plugin methods
- Middleware stack management
- Template and static file serving
- Database integration examples
- Authentication and authorization plugins

**Plugins Included**:
- **`routes.py`**: Basic web routes and pages
- **`api.py`**: RESTful API endpoints
- **`auth.py`**: Authentication and user management
- **`admin.py`**: Administrative interface
- **`static.py`**: Static file and asset management

**How to Run**:
```bash
cd web_server
python server.py                # Start development server (clean output)
python server.py --debug        # Start with debug logging and plugin details
python server.py --port 9000    # Run on custom port
```

**Available Endpoints**:
```
GET  /                  # Home page
GET  /api/status        # API status endpoint
POST /api/users         # User creation
GET  /admin             # Admin interface
GET  /static/<file>     # Static file serving
```

**What You'll See**:
- Web application with plugin-generated routes
- Dynamic content from multiple plugins
- Professional web development patterns
- Plugin-based middleware processing

**Demonstrates**:
- Web framework integration with PlugFlow
- Plugin-based routing and middleware
- Professional web application architecture
- Development vs production configurations
- Plugin coordination in web context

---

## Plugin Development Features

**Demonstrated Across Examples**:
- **Hot Reload**: Automatic plugin updates during development (debug mode)
- **Command Handling**: Multiple approaches to command processing
- **UI Integration**: Seamless integration with different UI frameworks
- **Event System**: Inter-plugin communication and coordination
- **Error Isolation**: Robust error handling without affecting other plugins
- **Package Plugins**: Support for both single files and package structures
- **Type Safety**: Proper type hints and interface enforcement
- **Lifecycle Management**: Plugin loading, initialization, and cleanup

## Learning Path

**Recommended Order**:
1. **CLI Tool** - Learn basic plugin concepts and type safety
2. **Telegram Bot** - Understand command handling and message processing
3. **Tkinter GUI** - Explore UI integration and event systems
4. **Web Server** - Master advanced plugin coordination and web integration

## Development Tips

**Debug Mode Usage**:
- Use `--debug` flag in CLI and bot examples for full logging
- Hot reload is automatically enabled in debug mode
- Production mode provides clean output suitable for deployment

**Plugin Development**:
- Extend appropriate base classes (`CLIPlugin`, `BasePlugin`)
- Implement required abstract methods for type safety
- Use proper error handling to maintain application stability
- Follow the examples' patterns for consistent plugin architecture

**Type Safety**:
- Use type hints for better development experience
- Leverage custom base classes for domain-specific functionality
- Cast plugin instances when needed for proper type checking

---

**All examples demonstrate production-ready code with clean separation of concerns, proper error handling, and development-friendly features!**
