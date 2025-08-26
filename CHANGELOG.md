# Changelog

## 1.0.4 - UNRELEASED

### Fixed
- **Windows Compatibility**: Fixed path separator tests to work correctly on Windows by using `os.path.isabs()` instead of Unix-specific path checks

## 1.0.3 - 2025-08-26
- Fix publishing to pypi

## 1.0.2 - 2025-08-26

### Changed
- **Constructor Enhancement**: Added default value `[]` for `plugins_paths` parameter in `PluginManager.__init__()` to make it optional
- **Type Safety**: Updated type annotations to support optional `plugins_paths` parameter

### Fixed
- **Priority System**: Fixed plugin priority sorting to correctly execute higher priority plugins first
- **Recursive Loading**: Fixed recursive plugin loading to properly discover plugins in subdirectories
- **Plugin Replacement**: Fixed plugin replacement mechanism to properly unload old modules from `sys.modules` cache, ensuring clean reload when plugins with same name are loaded
- **Hot Reload**: Fixed hot reload functionality by implementing initial file scanning in DirectoryWatcher to detect existing plugins on startup
- **Hot Reload Detection**: Fixed file deletion detection in hot reload system to properly handle plugin removal
- **Cross-Platform Tests**: Fixed test compatibility issues between macOS and Linux environments for hot reload functionality
- **Documentation**: Fixed API documentation to match actual method names (`handle_message` vs `handle_command`, `get` vs `get_plugin`, etc.)
- **Method Names**: Corrected README examples to use actual method signatures

### Added
- **Plugin Management Methods**: Added `unload_plugin()` and `reload_plugin()` methods to `PluginManager`
- **Comprehensive Test Suite**: Added extensive tests covering all major functionality:
  - Default parameter handling
  - Plugin priority system
  - Lifecycle hooks (on_load/on_unload)
  - Context sharing between manager and plugins
  - Broadcast method functionality
  - Error isolation and handling
  - Hot reload functionality
  - Event system testing
  - Message filtering and command processing
  - Integration tests based on example applications
- **Test Organization**: Reorganized tests into focused unit tests (`tests/unit/`) and integration tests (`tests/integration/`)
- **Test Fixtures**: Added common test utilities in `conftest.py` for better test maintainability

### Technical Details
- Enhanced constructor usability by allowing instantiation without plugin paths
- Improved type safety with `Optional[List[Union[str, Path]]]` annotation
- Fixed priority ordering in both `dispatch_event` and `handle_message` methods
- Improved recursive directory scanning in plugin loader
- Error isolation and handling
- Selective event handling with `handles()` method
- Multiple message handlers
- Recursive vs non-recursive plugin loading
- Plugin versioning
- Plugin replacement (same name)
- Non-existent path handling

### Technical Details
- Enhanced constructor usability by allowing instantiation without plugin paths
- Improved type safety with `Optional[List[Union[str, Path]]]` annotation
- Fixed plugin execution order to match documented behavior (higher priority = earlier execution)
- Improved recursive plugin discovery algorithm for better subdirectory support

## 1.0.1 - 2025-08-26

### Fixed
- **Python Compatibility**: Fixed type hints compatibility for Python 3.8+ by using `typing.Union` instead of `|` syntax
- **API Documentation**: Corrected README.md examples to use proper `PluginManager(plugins_paths=[...])` constructor instead of deprecated `PluginManager()` 
- **Method References**: Updated API documentation to reflect actual method signatures and return types

### Technical Details
- Enhanced type safety across all modules while supporting older Python versions

This release focuses on production readiness and developer experience improvements while maintaining full API compatibility.

## 1.0.0 - 2025-08-26

### Added
- Initial release of PlugFlow
- Dynamic plugin loading with hot-reload capabilities
- Event system for inter-plugin communication
- Complete plugin lifecycle management
- Type safety with full type hints support
- Error isolation preventing plugin crashes from affecting main application
- Framework-agnostic design
- Comprehensive examples (CLI tools, web servers, GUI applications)
- Professional documentation and API reference