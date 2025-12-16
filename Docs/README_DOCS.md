# 📚 MSLib Documentation

**Comprehensive guide for MSLib v1.2.0 - exteraGram plugin development framework**

---

## 📖 Table of Contents

### Getting Started
- [🚀 Quick Start Guide](quick-start.md) - Get up and running in 5 minutes
- [📦 Installation](installation.md) - Setup and requirements
- [🎓 First Plugin Tutorial](first-plugin.md) - Build your first plugin step-by-step

### Core Features
- [⚡ Command System](command-system.md) - Advanced command handling with middleware
- [🔄 Auto-Updater](auto-updater.md) - Automatic plugin updates
- [💾 Storage & Caching](storage-caching.md) - Data persistence and caching
- [🌍 Localization](localization.md) - Multi-language support

### Advanced Features
- [🎨 UI Components](ui-components.md) - Settings, alerts, and dialogs
- [📡 Telegram API](telegram-api.md) - Extended Telegram API helpers
- [🔘 Inline Buttons](inline-buttons.md) - Interactive inline markup
- [📁 File System](file-system.md) - File operations and utilities
- [🔐 Data Compression](compression.md) - Compress and encode data

### MSPlugin Class
- [🧩 MSPlugin Overview](msplugin-overview.md) - Enhanced base plugin class
- [🗄️ Database Methods](msplugin-database.md) - Built-in database operations
- [📝 Logging Methods](msplugin-logging.md) - Plugin-specific logging
- [🎯 Helper Methods](msplugin-helpers.md) - Utility methods

### Utilities Reference
- [🔧 Utility Functions](utilities.md) - All utility functions
- [📊 Formatting](formatting.md) - Text and data formatting
- [🎭 Entity Parsing](entity-parsing.md) - HTML/Markdown parsing
- [⚙️ Type Conversion](type-conversion.md) - Type casting utilities

### API Reference
- [📑 Complete API Reference](api-reference.md) - All classes and functions
- [🎯 Decorators](decorators.md) - @command, @uri, @watcher, etc.
- [📦 Exported Classes](classes.md) - All exported classes
- [🔍 Constants](constants.md) - Global constants

### Best Practices
- [✅ Coding Standards](coding-standards.md) - Best practices and patterns
- [🐛 Debugging Guide](debugging.md) - Troubleshooting and debugging
- [⚡ Performance Tips](performance.md) - Optimization techniques
- [🔒 Security](security.md) - Security best practices

### Examples
- [📚 Example Gallery](examples.md) - Complete working examples
- [🎯 Common Patterns](patterns.md) - Frequently used patterns
- [🔌 Plugin Templates](templates.md) - Ready-to-use templates

### Migration & Updates
- [🔄 Migration Guide](migration.md) - Upgrading from older versions
- [📝 Changelog](changelog.md) - Version history
- [🚧 Breaking Changes](breaking-changes.md) - Important changes

---

## 🎯 Quick Navigation

### By Task

**I want to...**
- **Create a command** → [Command System](command-system.md)
- **Save data** → [Storage & Caching](storage-caching.md)
- **Show notifications** → [UI Components](ui-components.md)
- **Make API requests** → [Telegram API](telegram-api.md)
- **Add settings** → [MSPlugin Overview](msplugin-overview.md)
- **Update automatically** → [Auto-Updater](auto-updater.md)
- **Parse HTML/Markdown** → [Entity Parsing](entity-parsing.md)
- **Work with files** → [File System](file-system.md)

### By Experience Level

**📘 Beginner**
1. [Quick Start Guide](quick-start.md)
2. [First Plugin Tutorial](first-plugin.md)
3. [Command System Basics](command-system.md#basics)
4. [Storage Basics](storage-caching.md#basics)

**📗 Intermediate**
1. [MSPlugin Class](msplugin-overview.md)
2. [Advanced Commands](command-system.md#advanced)
3. [Localization](localization.md)
4. [UI Components](ui-components.md)

**📕 Advanced**
1. [Command Middleware](command-system.md#middleware)
2. [Custom Hooks](msplugin-overview.md#hooks)
3. [Performance Optimization](performance.md)
4. [Security Best Practices](security.md)

---

## 🆕 What's New in v1.2.0

### Major Features
- ✨ **Enhanced Command System** - Middleware, aliases, subcommands, context
- 🗄️ **MSPlugin Class** - Built-in database, logging, and helpers
- 📁 **FileSystem Utilities** - Comprehensive file operations
- 🗜️ **Compression Support** - Built-in compress/decompress functions
- 📡 **Extended Telegram API** - TelegramAPI class with Result/Exception handling
- 🔘 **Inline Button Framework** - Easy inline keyboard creation

### Command System Enhancements
- **Middleware Hooks** - Before/after command execution
- **Command Context** - Rich execution context
- **Alias Support** - Multiple aliases per command
- **Subcommands** - Nested command hierarchies
- **Dynamic Enable/Disable** - Runtime command control
- **Auto Help Generation** - Built-in help system
- **Quoted Arguments** - Support for "arguments with spaces"

### New Utility Functions
- `format_size()` - Human-readable file sizes
- `format_duration()` - Human-readable time durations
- `compress_and_encode()` - Compress + base64 encode
- `decode_and_decompress()` - Decode + decompress
- `parse_quoted_args()` - Parse arguments with quotes

See [Changelog](changelog.md) for complete list.

---

## 📚 Essential Concepts

### Plugin Structure
```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class MyPlugin(MSPlugin, BasePlugin):
    """Your plugin description"""
    
    def __init__(self):
        super().__init__()
        # Plugin initialization
    
    def on_plugin_load(self):
        super().on_plugin_load()
        # Setup code
    
    @command("hello")
    def hello_cmd(self, param, account):
        """Say hello"""
        self.show_bulletin("Hello, World!", "success")
        return HookResult()
```

### Key Principles
1. **Always inherit from both MSPlugin and BasePlugin**
2. **Call super() in __init__ and on_plugin_load**
3. **Commands must return HookResult**
4. **Use self.db for data persistence**
5. **Use self.log() for logging**

---

## 🔗 External Resources

- [exteraGram GitHub](https://github.com/exteraSquad/exteraGram)
- [MSLib Repository](https://github.com/Miracle-Studios/MSLib)
- [exteraGram Community](https://t.me/exteraGram)
- [Miracle Studios](https://t.me/MiracleStudios)

---

## 📄 License

MSLib is licensed under the BSD 3-Clause License. See [LICENSE](../LICENSE) for details.

---

**Ready to start?** → [Quick Start Guide](quick-start.md)
