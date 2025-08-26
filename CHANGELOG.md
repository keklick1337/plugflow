# Changelog

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