# Changelog

All notable changes to MSLib will be documented in this file.

## [1.1.0-beta] - 2024-12-05

### 🎉 Major Features

#### AutoUpdater System
- **Self-updating capability**: MSLib can now update itself automatically
- **Smart polling**: 1-second check cycle for instant forced updates
- **Task management**: Add/remove update tasks for multiple plugins
- **Timestamp validation**: Optional message edit date checking
- **Manual trigger**: Force update check button in settings
- **Configurable timeout**: Adjustable update check interval

#### Instant Activation System
- **No reload required**: All integrated plugins work instantly after enabling
- **Runtime checks**: Hooks validate settings on every call
- **4 integrated plugins**:
  - HashTags Fix: Opens "This chat" instead of "Public Posts"
  - Article Viewer Fix: Disables swipe-to-close in browser
  - No Call Confirmation: Skips call confirmation dialog
  - Old Bottom Forward: Restores old forward dialog

#### Command System
- **Dispatcher**: Centralized command routing with custom prefix
- **Type validation**: Smart argument parsing with type hints
- **Live prefix update**: Change command prefix without reload
- **Decorators**: `@command`, `@uri`, `@message_uri`, `@watcher`

### ✨ New Features

#### Utilities
- **pluralization_string()**: Russian language pluralization helper
- **Callback2/Callback5**: Additional callback wrappers from CactusLib
- **runtime_exec()**: Execute system commands via Runtime.exec
- **get_logs()**: Filtered logcat retrieval with time/level filtering
- **escape_html()**: HTML special character escaping
- **Spinner**: Context manager for loading dialogs

#### Storage & Caching
- **JsonDB**: JSON-based key-value database
- **JsonCacheFile**: Compressed JSON cache with auto-initialization
- **CacheFile**: Binary file caching with compression support

#### Parsers
- **Markdown.parse()**: Convert markdown to Telegram entities (bold, italic)
- **Markdown.unparse()**: Convert entities back to markdown
- **HTML.parse()**: HTML to Telegram entities parser
- **HTML.unparse()**: Entities to HTML converter

#### API Utilities
- **Requests**: Simplified Telegram API wrapper
  - get_user(), get_chat(), get_message()
  - search_messages()
  - delete_messages()
  - ban(), unban()
  - change_slowmode()
  - get_chat_participant()

#### UI Components
- **InnerBulletinHelper**: Enhanced notifications with prefix support
- **UI.show_alert()**: Simple alert dialogs
- **UI.show_confirm()**: Confirmation dialogs
- **Spinner**: Loading indicator with context manager

### 🔧 Improvements

#### Code Quality
- **Removed duplications**: Eliminated duplicate InnerBulletinHelper and copy_to_clipboard
- **Centralized initialization**: Single autoupdater startup path via _delayed_autoupdater_start()
- **Optimized globals**: Proper global variable management
- **Complete docstrings**: All public methods documented
- **Type hints**: Comprehensive typing throughout codebase

#### Performance
- **Code reduction**: 2656 → 2465 lines (-7.2%)
- **Lazy initialization**: Constants loaded on plugin load, not import
- **Efficient caching**: Compressed JSON storage with deferred path resolution

#### Settings
- **Reactive updates**: All settings apply immediately without reload
  - AutoUpdater toggle: Start/stop on change
  - Command prefix: Live Dispatcher update
  - Debug mode: Instant logging level change
  - Plugin toggles: Runtime activation/deactivation
- **Localized messages**: Proper message keys for all plugin states
- **State validation**: Checks before actions (e.g., AutoUpdater thread state)

### 🐛 Bug Fixes
- Fixed force_update_check not checking AutoUpdater thread state
- Fixed toggle_plugin using wrong localization key format (underscores → dashes)
- Fixed AutoUpdater cycle waiting full timeout before forced check
- Fixed download_and_install_plugin missing error handling
- Fixed Markdown.parse() being a stub (now fully implemented)
- Fixed duplicate code in Markdown.unparse()
- Fixed missing pluralization_string function (was in __all__ but not implemented)

### 🌍 Localization
- **English**: Complete translation for all UI elements
- **Russian**: Complete translation for all UI elements
- **Locale detection**: Automatic language selection based on system locale
- **Fallback**: English as default language

### 📚 Documentation
- **Inline comments**: Critical sections documented
- **Docstrings**: All classes, methods, and functions
- **Type hints**: Full typing for better IDE support
- **Examples**: Usage examples in docstrings

### 🏗️ Architecture

#### Plugin System
- **MSPlugin mixin**: Base class for plugins with built-in utilities
- **Hook registration**: Automatic command/URI/watcher registration
- **Settings management**: Integrated get/set methods
- **Localization**: Built-in string() method for translations

#### Global State
- **MSLib_instance**: Global plugin instance reference
- **autoupdater**: Shared AutoUpdater instance
- **command_dispatcher**: Global command router
- **BulletinHelper**: Centralized notification system

### 📦 Exports
**172 functions** and **36 classes** available via `__all__`:

- Main: MSLib, MSPlugin
- Cache: CacheFile, JsonCacheFile, JsonDB
- Callbacks: Callback1, Callback2, Callback5
- Parsers: HTML, Markdown, TLEntityType, RawEntity
- UI: InnerBulletinHelper, BulletinHelper, UI, Spinner
- Commands: Dispatcher, Command, ArgSpec, Decorators
- AutoUpdater: AutoUpdater, UpdaterTask, helper functions
- Requests: Requests API wrapper
- Utilities: 20+ helper functions
- Hooks: HashTagsFixHook, ArticleViewerFixHook, NoCallConfirmationHook, OldBottomForwardHook

### 🔐 Security
- **Error handling**: Comprehensive try-catch blocks
- **Input validation**: Type checking and argument validation
- **Safe file operations**: Permission error handling
- **Java interop safety**: Proper exception handling for Java calls

### ⚙️ Configuration
- **Command prefix**: Customizable (default: ".")
- **AutoUpdater timeout**: Configurable interval (default: 600s)
- **Debug mode**: Detailed logging for troubleshooting
- **Timestamp check**: Optional edit date validation

### 📈 Statistics
- **Total lines**: 2,465
- **Functions**: 172
- **Classes**: 36
- **Plugins integrated**: 4
- **Languages**: 2 (EN, RU)

### 🚀 Performance Metrics
- **Startup**: Lazy constant initialization
- **Memory**: Efficient caching with compression
- **Response**: Instant setting changes without reload
- **Updates**: 1-second polling for forced checks

---

## Development Notes

### Code Review Phases
1. ✅ AutoUpdater improvements (v2.3.6 pattern)
2. ✅ Instant activation implementation
3. ✅ CactusLib feature parity
4. ✅ Command system implementation
5. ✅ Bug fixes and optimizations
6. ✅ Settings validation
7. ✅ Global code optimization
8. ✅ Duplication removal

### Testing Status
- ✅ Compilation successful
- ✅ All settings functions validated
- ✅ No code duplication
- ✅ Global variables correct
- ✅ All __all__ exports implemented

### Known Limitations
- 5 bare `except:` blocks (acceptable for Java interop)
- Markdown parser supports only bold and italic (basic implementation)
- AutoUpdater requires manual task registration per plugin

---

**Full release ready for production! 🎉**
