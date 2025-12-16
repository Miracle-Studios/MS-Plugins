# 📑 Complete API Reference

**Comprehensive reference for all MSLib classes and functions**

---

## 📦 Overview

MSLib exports **180+ functions** and **36 classes** covering:
- Command system
- Storage & caching
- UI components
- Telegram API
- Utilities
- Localization
- And more...

---

## 🎯 Quick Reference

### Most Used

```python
# Logging
from MSLib import logger
logger.info("Message")

# Notifications
from MSLib import BulletinHelper
BulletinHelper.show_success("Done!")

# Storage
from MSLib import JsonDB
db = JsonDB("data.json")

# Commands
from MSLib import command
@command()
def my_cmd(self, param, account):
    pass

# Plugin Base
from MSLib import MSPlugin
class MyPlugin(MSPlugin, BasePlugin):
    pass
```

---

## 📚 Classes

### Core Plugin Classes

#### `MSPlugin`
Enhanced base plugin class.

**Methods:**
- `get(key, default=None)` - Get from database
- `set(key, value)` - Save to database
- `pop(key, default=None)` - Delete from database
- `log(message)` - Log info message
- `debug(message)` - Log debug message
- `info(message)` - Log info message
- `warn(message)` - Log warning
- `error(message)` - Log error
- `show_bulletin(message, type)` - Show notification
- `format_size(bytes)` - Format file size
- `format_duration(seconds)` - Format duration
- `copy_to_clipboard(text, show_bulletin)` - Copy to clipboard
- `localise(key)` - Get localized string
- `get_setting(key, default)` - Get plugin setting
- `set_setting(key, value)` - Set plugin setting
- `run_on_ui_thread(func)` - Execute on UI thread
- `run_on_queue(func)` - Execute on background thread

**Properties:**
- `db` - JsonDB instance
- `lstrings` - Localized strings dict
- `strings` - All strings dict

**Example:**
```python
class MyPlugin(MSPlugin, BasePlugin):
    def __init__(self):
        super().__init__()
    
    def on_plugin_load(self):
        super().on_plugin_load()
        self.log("Loaded!")
```

---

### Command System

#### `Command`
Represents a command with metadata.

**Attributes:**
- `func` - Command function
- `name` - Command name
- `args` - List of ArgSpec
- `subcommands` - Dict of subcommands
- `error_handler` - Error handler function
- `aliases` - List of aliases
- `doc` - Documentation key
- `enabled` - Enable/disable state

**Methods:**
- `subcommand(name)` - Decorator for subcommands
- `register_error_handler(func)` - Register error handler
- `add_alias(alias)` - Add alias
- `remove_alias(alias)` - Remove alias
- `is_enabled(plugin_instance)` - Check if enabled
- `get_subcommand(name)` - Get subcommand
- `has_subcommands()` - Check if has subcommands
- `list_subcommands()` - List subcommand names

#### `Dispatcher`
Command dispatcher.

**Attributes:**
- `plugin_id` - Plugin identifier
- `prefix` - Command prefix
- `commands_priority` - Priority level
- `listeners` - Dict of commands
- `aliases` - Dict of aliases
- `before_hooks` - List of before hooks
- `after_hooks` - List of after hooks

**Methods:**
- `register_command(name)` - Decorator to register command
- `unregister_command(name)` - Unregister command
- `set_prefix(prefix)` - Set command prefix
- `add_alias(command_name, alias)` - Add alias
- `remove_alias(alias)` - Remove alias
- `get_command(name)` - Get command by name or alias
- `get_all_commands()` - Get all commands dict
- `get_command_with_aliases(name)` - Get command and its aliases
- `execute_command(command, args, plugin_instance, context)` - Execute command
- `dispatch(message_text, param, account, plugin_instance)` - Dispatch command from text
- `set_command_enabled(name, enabled, plugin_instance)` - Enable/disable command
- `is_command_enabled(name, plugin_instance)` - Check if enabled
- `get_enabled_commands(plugin_instance)` - List enabled commands
- `get_disabled_commands(plugin_instance)` - List disabled commands
- `reset_command(name)` - Reset to original state
- `get_command_info(name)` - Get command metadata
- `get_all_commands_info()` - Get all commands metadata
- `format_command_list(plugin_instance)` - Format commands for display
- `generate_help_text(command_name, strings)` - Generate help for command
- `generate_all_commands_help(strings, plugin_instance)` - Generate help for all
- `validate_command_name(name)` - Validate command name
- `check_alias_conflicts()` - Check alias conflicts
- `bulk_enable_commands(names, plugin_instance)` - Enable multiple
- `bulk_disable_commands(names, plugin_instance)` - Disable multiple
- `enable_all_commands(plugin_instance)` - Enable all
- `disable_all_commands(plugin_instance)` - Disable all
- `clear_all_commands()` - Remove all
- `add_before_hook(hook)` - Add before hook
- `add_after_hook(hook)` - Add after hook
- `remove_before_hook(hook)` - Remove before hook
- `remove_after_hook(hook)` - Remove after hook
- `clear_hooks()` - Clear all hooks
- `register_help_command(strings)` - Register built-in help

#### `CommandContext`
Command execution context.

**Attributes:**
- `command_name` - Name of command
- `raw_text` - Original message text
- `args` - Parsed arguments tuple
- `param` - CommandParams object
- `account` - User account
- `plugin_instance` - Plugin instance
- `dispatcher` - Dispatcher instance

#### `ArgSpec`
Argument specification for command.

**Attributes:**
- `name` - Parameter name
- `annotation` - Type annotation
- `kind` - Parameter kind
- `default` - Default value
- `is_optional` - Is optional flag

**Methods:**
- `from_parameter(param)` - Create from inspect.Parameter

#### `CommandParams`
Command parameters wrapper.

**Attributes:**
- `text` - Message text
- `entities` - Message entities
- `peer` - Peer ID
- `replyToMsg` - Reply to message
- `replyToTopMsg` - Reply to top message

**Methods:**
- `html()` - Get HTML representation
- `markdown()` - Get Markdown representation

---

### Storage Classes

#### `JsonDB`
JSON-based database.

**Methods:**
- `set(key, value)` - Set value
- `get(key, default=None)` - Get value
- `pop(key, default=None)` - Remove and return
- `keys()` - Get all keys
- `values()` - Get all values
- `items()` - Get all items
- `clear()` - Clear all data
- `__contains__(key)` - Check if key exists
- `__len__()` - Get size

**Example:**
```python
db = JsonDB("data.json")
db.set("key", "value")
value = db.get("key")
```

#### `CacheFile`
Binary cache file with compression.

**Methods:**
- `read()` - Read from file
- `write(content)` - Write to file
- `get_content()` - Get cached content
- `clear()` - Clear cache

**Example:**
```python
cache = CacheFile("cache.bin", compress=True)
cache.write(b"data")
data = cache.get_content()
```

#### `JsonCacheFile`
JSON cache file.

**Methods:**
- `read()` - Read JSON
- `write(data)` - Write JSON
- `get_content()` - Get data
- `reset()` - Reset to default

---

### UI Classes

#### `BulletinHelper`
Show notifications.

**Methods:**
- `show_success(message)` - Success notification (green)
- `show_error(message)` - Error notification (red)
- `show_info(message)` - Info notification (blue)
- `show_warning(message)` - Warning notification (orange)
- `show_copied_to_clipboard()` - "Copied!" notification

**Example:**
```python
from MSLib import BulletinHelper

BulletinHelper.show_success("Done!")
BulletinHelper.show_error("Failed!")
```

#### `AlertDialogBuilder`
Build alert dialogs.

**Methods:**
- `setTitle(title)` - Set title
- `setMessage(message)` - Set message
- `setPositiveButton(text, callback)` - Add positive button
- `setNegativeButton(text, callback)` - Add negative button
- `show()` - Show dialog

#### `Spinner`
Loading spinner context manager.

**Usage:**
```python
from MSLib import Spinner

with Spinner("Loading..."):
    # Long operation
    process_data()
```

---

### Telegram API

#### `TelegramAPI`
Telegram API helper.

**Classes:**
- `Result` - API result wrapper
- `TLRPCException` - TLRPC error
- `SearchFilter` - Message search filters

**Methods:**
- `send(request, account, callback)` - Send API request

**Example:**
```python
from MSLib import TelegramAPI

api = TelegramAPI()
result = api.Result()

def callback(res, err):
    if err:
        print(f"Error: {err}")
    else:
        print(f"Success: {res}")

api.send(request, account, callback)
```

#### `Requests`
Telegram request helpers.

**Methods:**
- `get_user(user_id, callback, account)` - Get user
- `get_chat(chat_id, callback, account)` - Get chat
- `get_full_user(user_id, callback, account)` - Get full user
- `get_full_chat(chat_id, callback, account)` - Get full chat
- `search_messages(...)` - Search messages

---

### Entity Parsing

#### `HTML`
HTML entity parser.

**Methods:**
- `parse(html_text)` - Parse HTML to ParsedMessage
- `unparse(text, entities)` - Convert to HTML

**Example:**
```python
from MSLib import HTML

parsed = HTML.parse("<b>Bold</b> text")
print(parsed.text)  # "Bold text"
print(parsed.entities)  # [RawEntity(...)]

html = HTML.unparse("Bold text", entities)
```

#### `Markdown`
Markdown parser.

**Methods:**
- `parse(markdown_text)` - Parse Markdown
- `unparse(text, entities)` - Convert to Markdown

#### `RawEntity`
Raw entity data.

**Attributes:**
- `type` - Entity type (TLEntityType)
- `offset` - Start offset
- `length` - Length
- `extra` - Extra data (URL, language, etc.)

#### `TLEntityType`
Entity type enum.

**Values:**
- `BOLD`, `ITALIC`, `UNDERLINE`, `STRIKETHROUGH`
- `CODE`, `PRE`, `TEXT_LINK`
- `SPOILER`, `CUSTOM_EMOJI`, `BLOCKQUOTE`

---

### File System

#### `FileSystem`
File system utilities.

**Methods:**
- `get_plugins_dir()` - Get plugins directory
- `get_cache_dir(subdir)` - Get cache directory
- `read_file(path)` - Read file
- `write_file(path, content)` - Write file
- `delete_file(path)` - Delete file
- `file_exists(path)` - Check if exists
- `list_files(dir)` - List files
- `create_dir(path)` - Create directory

**Example:**
```python
from MSLib import FileSystem

# Read file
content = FileSystem.read_file("/path/to/file.txt")

# Write file
FileSystem.write_file("/path/to/file.txt", "content")

# Check existence
if FileSystem.file_exists("/path/to/file.txt"):
    print("File exists")
```

---

### Inline Buttons

#### `Inline`
Inline keyboard builder.

**Classes:**
- `Button` - Single button
- `Markup` - Keyboard markup
- `CallbackParams` - Callback parameters

**Methods:**
- `Button.text(text, callback_data)` - Text button
- `Button.url(text, url)` - URL button
- `Markup.from_buttons(buttons)` - Create markup

**Example:**
```python
from MSLib import Inline

# Create buttons
btn1 = Inline.Button.text("Button 1", "callback_1")
btn2 = Inline.Button.text("Button 2", "callback_2")

# Create markup
markup = Inline.Markup.from_buttons([[btn1, btn2]])

# Handle callback
@inline_handler("callback_1")
def handle_callback(self, params):
    self.show_bulletin("Button 1 clicked!", "info")
```

---

## 🔧 Functions

### Logging

#### `build_log(tag, level=logging.INFO)`
Create logger with tag.

```python
from MSLib import build_log
import logging

logger = build_log("MyPlugin", logging.DEBUG)
logger.info("Message")
```

#### `format_exc()`, `format_exc_from(e)`, `format_exc_only(e)`
Format exceptions.

```python
from MSLib import format_exc, format_exc_only

try:
    risky_operation()
except Exception as e:
    logger.error(format_exc_only(e))
```

#### `get_logs(__id__=None, times=None, lvl=None, as_list=False)`
Get filtered logs.

---

### Text Processing

#### `escape_html(text)`, `unescape_html(text)`
Escape/unescape HTML.

```python
from MSLib import escape_html, unescape_html

safe = escape_html("<script>alert('XSS')</script>")
restored = unescape_html(safe)
```

#### `pluralization_string(count, forms)`
Get plural form.

```python
from MSLib import pluralization_string

# English
text = pluralization_string(5, ["file", "files"])  # "5 files"

# Russian
text = pluralization_string(5, ["файл", "файла", "файлов"])  # "5 файлов"
```

#### `link(text, url)`
Create HTML link.

```python
from MSLib import link

html = link("Click here", "https://example.com")
# '<a href="https://example.com">Click here</a>'
```

---

### Compression

#### `compress_and_encode(data, level=9)`
Compress and base64 encode.

```python
from MSLib import compress_and_encode

encoded = compress_and_encode("Large text data...")
```

#### `decode_and_decompress(encoded_data)`
Decode and decompress.

```python
from MSLib import decode_and_decompress

data = decode_and_decompress(encoded)
```

---

### Formatting

#### `format_size(size_bytes)`
Format bytes to human-readable.

```python
from MSLib import format_size

size = format_size(1048576)  # "1.0 MB"
```

#### `format_duration(seconds)`
Format seconds to human-readable.

```python
from MSLib import format_duration

duration = format_duration(3661)  # "1h 1m 1s"
```

---

### Type Conversion

#### `arraylist_to_list(jarray)`, `list_to_arraylist(pylist)`
Convert between Python list and Java ArrayList.

```python
from MSLib import arraylist_to_list, list_to_arraylist

py_list = arraylist_to_list(java_arraylist)
java_list = list_to_arraylist([1, 2, 3])
```

#### `cast_arg(arg, target_type)`
Cast string argument to type.

```python
from MSLib import cast_arg

num = cast_arg("42", int)  # 42
flag = cast_arg("true", bool)  # True
```

#### `smart_cast(arg, annotation)`
Smart cast with Union/Optional support.

---

### Clipboard

#### `copy_to_clipboard(text, show_bulletin=True)`
Copy text to clipboard.

```python
from MSLib import copy_to_clipboard

copy_to_clipboard("Copied text")
copy_to_clipboard("Silent copy", show_bulletin=False)
```

---

### Async Operations

#### `run_on_ui_thread(func)`
Execute on UI thread.

```python
from MSLib import run_on_ui_thread

@run_on_ui_thread
def update_ui():
    # UI operations
    pass
```

#### `run_on_queue(func)`
Execute on background queue.

```python
from MSLib import run_on_queue

def background_task():
    # Heavy processing
    pass

run_on_queue(background_task)
```

---

### Localization

#### `localise(key)`
Get localized string.

```python
from MSLib import localise

text = localise("welcome_message")
```

---

### Command System

#### `create_command(func, name)`
Create Command from function.

#### `parse_args(raw_args, command_args)`
Parse command arguments.

#### `parse_quoted_args(text)`
Parse arguments with quotes.

```python
from MSLib import parse_quoted_args

args = parse_quoted_args('"arg 1" "arg 2" arg3')
# ['arg 1', 'arg 2', 'arg3']
```

#### `is_allowed_type(arg_type)`
Check if type is allowed for commands.

---

### Auto-Updater

#### `add_autoupdater_task(plugin_id, channel_id, message_id, updater)`
Add auto-update task.

#### `remove_autoupdater_task(plugin_id)`
Remove auto-update task.

#### `get_plugin(plugin_id)`
Get plugin by ID.

---

## 🎨 Decorators

### `@command(cmd=None, *, aliases=None, doc=None, enabled=None)`
Command decorator.

```python
@command("hello", aliases=["hi"], doc="greeting_doc")
def hello_cmd(self, param, account):
    pass
```

### `@uri(uri)`
URI handler decorator.

```python
@uri("tg://resolve?domain=example")
def handle_uri(self, param, account):
    pass
```

### `@message_uri(uri, support_long_click=False)`
Message URI handler.

```python
@message_uri("custom://action", support_long_click=True)
def handle_message_uri(self, param, account):
    pass
```

### `@watcher()`
Watcher decorator.

```python
@watcher()
def watch_messages(self, param, account):
    pass
```

### `@inline_handler(method, support_long_click=False)`
Inline button handler.

```python
@inline_handler("button_callback")
def handle_button(self, params):
    pass
```

---

## 🔢 Constants

```python
CACHE_DIRECTORY  # Cache directory path
PLUGINS_DIRECTORY  # Plugins directory path
COMPANION_PATH  # Companion file path
LOCALE  # Current locale ("en" or "ru")
ALLOWED_ARG_TYPES  # (str, int, float, bool, Any)
ALLOWED_ORIGIN  # (Union, Optional)
```

---

## 📊 Enums

### `TLEntityType`
Message entity types.

### `SearchFilter` (TelegramAPI.SearchFilter)
Message search filters.

---

**Next:** [Examples](examples.md) | **Previous:** [MSPlugin Overview](msplugin-overview.md)
