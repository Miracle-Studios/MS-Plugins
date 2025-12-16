# 🧩 MSPlugin Overview

**Enhanced base plugin class with built-in features**

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Basic Usage](#basic-usage)
3. [Built-in Database](#built-in-database)
4. [Logging Methods](#logging-methods)
5. [Notification Methods](#notification-methods)
6. [Formatting Methods](#formatting-methods)
7. [Clipboard Methods](#clipboard-methods)
8. [Async Methods](#async-methods)
9. [Settings Management](#settings-management)
10. [Localization](#localization)
11. [Complete Example](#complete-example)

---

## Introduction

`MSPlugin` is an enhanced base class that provides:
- ✅ Automatic database initialization
- ✅ Plugin-specific logging
- ✅ Built-in notification helpers
- ✅ Formatting utilities
- ✅ Clipboard operations
- ✅ Async task management
- ✅ Localization support
- ✅ Settings helpers

---

## Basic Usage

### Minimal Plugin

```python
from MSLib import MSPlugin
from base_plugin import BasePlugin

class MyPlugin(MSPlugin, BasePlugin):
    """My enhanced plugin"""
    
    def __init__(self):
        super().__init__()
    
    def on_plugin_load(self):
        super().on_plugin_load()
        self.log("Plugin loaded!")
```

**Important:** Always inherit from both `MSPlugin` and `BasePlugin`, and call `super()` methods!

---

## Built-in Database

MSPlugin provides automatic JSON database at `self.db`:

### Basic Operations

```python
# Save data
self.db.set("username", "John")
self.db.set("age", 25)
self.db.set("settings", {"theme": "dark"})

# Load data
username = self.db.get("username")  # "John"
age = self.db.get("age", 0)  # 25, default 0
theme = self.db.get("theme", "light")  # "light" if not found

# Delete data
self.db.pop("old_key")

# Check existence
if "username" in self.db:
    print("User exists")

# Get all keys
keys = list(self.db.keys())

# Clear all
self.db.clear()
```

### Advanced Database Usage

```python
class DataPlugin(MSPlugin, BasePlugin):
    
    def save_user_data(self, user_id: int, data: dict):
        """Save user data"""
        key = f"user_{user_id}"
        self.db.set(key, data)
        self.log(f"Saved data for user {user_id}")
    
    def get_user_data(self, user_id: int) -> dict:
        """Get user data"""
        key = f"user_{user_id}"
        return self.db.get(key, {})
    
    def delete_user(self, user_id: int):
        """Delete user data"""
        key = f"user_{user_id}"
        self.db.pop(key)
    
    def get_all_users(self) -> list:
        """Get all user IDs"""
        users = []
        for key in self.db.keys():
            if key.startswith("user_"):
                user_id = int(key.replace("user_", ""))
                users.append(user_id)
        return users
    
    def get_stats(self) -> dict:
        """Get statistics"""
        return {
            "total_users": len(self.get_all_users()),
            "db_size": len(self.db),
            "keys": list(self.db.keys())
        }
```

### Counter Example

```python
def increment_counter(self, counter_name: str) -> int:
    """Increment and return counter"""
    count = self.db.get(counter_name, 0)
    count += 1
    self.db.set(counter_name, count)
    return count

def reset_counter(self, counter_name: str):
    """Reset counter to 0"""
    self.db.set(counter_name, 0)
```

---

## Logging Methods

Plugin-specific logging with automatic prefixing:

### Available Methods

```python
# Debug (only in debug mode)
self.debug("Debug information")

# Info (general information)
self.log("Operation completed")
self.info("User logged in")

# Warning
self.warn("Deprecated feature used")

# Error
self.error("Failed to connect to API")
```

### Example Usage

```python
class LoggingPlugin(MSPlugin, BasePlugin):
    
    @command("process")
    def process_cmd(self, param, account, data: str):
        """Process data with logging"""
        
        self.debug(f"Processing data: {data}")
        
        try:
            result = self.process_data(data)
            self.info(f"Successfully processed: {result}")
            return HookResult.from_string(f"✅ Done: {result}")
        
        except ValueError as e:
            self.warn(f"Invalid data format: {e}")
            return HookResult.from_string("⚠️ Invalid format")
        
        except Exception as e:
            self.error(f"Processing failed: {e}")
            return HookResult.from_string("❌ Error occurred")
```

---

## Notification Methods

### show_bulletin()

Show notifications to user:

```python
# Success (green)
self.show_bulletin("Operation successful!", "success")

# Error (red)
self.show_bulletin("Something went wrong!", "error")

# Info (blue)
self.show_bulletin("FYI: Information here", "info")

# Warning (orange)
self.show_bulletin("Warning: Be careful", "warning")
```

### Example

```python
@command("save")
def save_cmd(self, param, account, data: str):
    """Save data"""
    try:
        self.db.set("saved_data", data)
        self.show_bulletin("✅ Data saved successfully!", "success")
    except Exception as e:
        self.error(f"Save failed: {e}")
        self.show_bulletin(f"❌ Failed to save: {e}", "error")
    
    return HookResult()
```

---

## Formatting Methods

### format_size()

Format bytes to human-readable size:

```python
size = self.format_size(1024)  # "1.0 KB"
size = self.format_size(1048576)  # "1.0 MB"
size = self.format_size(1073741824)  # "1.0 GB"
```

### format_duration()

Format seconds to human-readable duration:

```python
duration = self.format_duration(90)  # "1m 30s"
duration = self.format_duration(3661)  # "1h 1m 1s"
duration = self.format_duration(45)  # "45s"
```

### Example Usage

```python
@command("fileinfo")
def fileinfo_cmd(self, param, account, size_bytes: int):
    """Show file info"""
    
    # Format file size
    size_formatted = self.format_size(size_bytes)
    
    # Calculate download time (assuming 1 MB/s)
    download_time = size_bytes / (1024 * 1024)
    time_formatted = self.format_duration(int(download_time))
    
    self.show_bulletin(
        f"📁 File Size: {size_formatted}\\n"
        f"⏱️ Download Time: {time_formatted}",
        "info"
    )
    
    return HookResult()

@command("uptime")
def uptime_cmd(self, param, account):
    """Show plugin uptime"""
    import time
    
    if not hasattr(self, 'start_time'):
        self.start_time = time.time()
    
    uptime_seconds = int(time.time() - self.start_time)
    uptime = self.format_duration(uptime_seconds)
    
    self.show_bulletin(f"⏱️ Uptime: {uptime}", "info")
    return HookResult()
```

---

## Clipboard Methods

### copy_to_clipboard()

Copy text to clipboard with optional notification:

```python
# Copy with notification
self.copy_to_clipboard("Copied text")

# Copy silently
self.copy_to_clipboard("Copied text", show_bulletin=False)
```

### Example

```python
@command("copyid")
def copyid_cmd(self, param, account):
    """Copy your user ID"""
    user_id = str(account.id)
    self.copy_to_clipboard(user_id)
    self.show_bulletin(f"📋 ID copied: {user_id}", "success")
    return HookResult()

@command("export")
def export_cmd(self, param, account):
    """Export data to clipboard"""
    import json
    
    data = {
        "user_id": account.id,
        "data": self.db.get("user_data", {})
    }
    
    json_str = json.dumps(data, indent=2)
    self.copy_to_clipboard(json_str, show_bulletin=False)
    self.show_bulletin("✅ Data exported to clipboard!", "success")
    
    return HookResult()
```

---

## Async Methods

### run_on_ui_thread()

Execute code on UI thread:

```python
def update_ui(self):
    """Update UI (must run on UI thread)"""
    # UI operations here
    pass

@command("update")
def update_cmd(self, param, account):
    """Update UI"""
    self.run_on_ui_thread(self.update_ui)
    return HookResult()
```

### run_on_queue()

Execute code on background queue:

```python
def heavy_processing(self):
    """CPU-intensive task"""
    import time
    time.sleep(5)
    result = "Done!"
    
    # Update UI from background thread
    self.run_on_ui_thread(lambda: self.show_bulletin(result, "success"))

@command("process")
def process_cmd(self, param, account):
    """Start heavy processing"""
    self.run_on_queue(self.heavy_processing)
    self.show_bulletin("⏳ Processing started...", "info")
    return HookResult()
```

---

## Settings Management

### get_setting()

Get plugin setting value:

```python
# Get with default
value = self.get_setting("enable_feature", False)

# Use in code
if self.get_setting("debug_mode", False):
    self.debug("Debug mode active")
```

### set_setting()

Set plugin setting:

```python
self.set_setting("theme", "dark")
self.set_setting("auto_save", True)
```

### Example

```python
class SettingsPlugin(MSPlugin, BasePlugin):
    
    @command("settheme")
    def settheme_cmd(self, param, account, theme: str):
        """Set theme: .settheme dark"""
        if theme not in ["light", "dark"]:
            return HookResult.from_string("❌ Theme must be 'light' or 'dark'")
        
        self.set_setting("theme", theme)
        self.show_bulletin(f"✅ Theme set to: {theme}", "success")
        return HookResult()
    
    @command("gettheme")
    def gettheme_cmd(self, param, account):
        """Get current theme"""
        theme = self.get_setting("theme", "light")
        self.show_bulletin(f"🎨 Current theme: {theme}", "info")
        return HookResult()
    
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Apply theme on load
        theme = self.get_setting("theme", "light")
        self.log(f"Loaded theme: {theme}")
```

---

## Localization

### localise()

Get localized string:

```python
# Get localized string
text = self.localise("welcome_message")

# Use in bulletin
self.show_bulletin(self.localise("success_message"), "success")
```

### lstrings Property

Access all localized strings:

```python
# Get all strings for current locale
strings = self.lstrings

# Use in code
welcome = strings.get("welcome", "Welcome!")
```

### Define Strings

```python
class LocalizedPlugin(MSPlugin, BasePlugin):
    """Plugin with localization"""
    
    strings = {
        "en": {
            "welcome": "Welcome!",
            "goodbye": "Goodbye!",
            "error_occurred": "An error occurred",
            "success": "Success!"
        },
        "ru": {
            "welcome": "Добро пожаловать!",
            "goodbye": "До свидания!",
            "error_occurred": "Произошла ошибка",
            "success": "Успешно!"
        }
    }
    
    @command("greet")
    def greet_cmd(self, param, account):
        """Greet user in their language"""
        message = self.localise("welcome")
        self.show_bulletin(message, "success")
        return HookResult()
```

---

## Complete Example

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult
import time

class AdvancedPlugin(MSPlugin, BasePlugin):
    """Advanced plugin using all MSPlugin features"""
    
    # Localization
    strings = {
        "en": {
            "welcome": "Welcome to Advanced Plugin!",
            "saved": "Data saved successfully",
            "error": "An error occurred",
            "stats": "Statistics"
        },
        "ru": {
            "welcome": "Добро пожаловать в Advanced Plugin!",
            "saved": "Данные сохранены успешно",
            "error": "Произошла ошибка",
            "stats": "Статистика"
        }
    }
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
    
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Initialize database
        if not self.db.get("initialized"):
            self.db.set("initialized", True)
            self.db.set("load_count", 0)
            self.log("First time initialization")
        
        # Increment load counter
        count = self.db.get("load_count", 0)
        self.db.set("load_count", count + 1)
        
        # Show welcome message
        welcome = self.localise("welcome")
        self.show_bulletin(welcome, "success")
        
        self.info(f"Plugin loaded (count: {count + 1})")
    
    @command("save", aliases=["s"])
    def save_cmd(self, param, account, key: str, value: str):
        """Save data: .save mykey myvalue"""
        try:
            # Save to database
            self.db.set(key, value)
            
            # Log operation
            self.info(f"Saved: {key} = {value}")
            
            # Show success
            message = self.localise("saved")
            self.show_bulletin(f"✅ {message}", "success")
            
        except Exception as e:
            self.error(f"Save failed: {e}")
            error_msg = self.localise("error")
            self.show_bulletin(f"❌ {error_msg}: {e}", "error")
        
        return HookResult()
    
    @command("get", aliases=["g"])
    def get_cmd(self, param, account, key: str):
        """Get data: .get mykey"""
        value = self.db.get(key)
        
        if value is None:
            self.show_bulletin(f"❌ Key '{key}' not found", "error")
        else:
            self.show_bulletin(f"📦 {key} = {value}", "info")
        
        return HookResult()
    
    @command("stats")
    def stats_cmd(self, param, account):
        """Show plugin statistics"""
        
        # Calculate uptime
        uptime_sec = int(time.time() - self.start_time)
        uptime = self.format_duration(uptime_sec)
        
        # Get database info
        db_size = len(self.db)
        load_count = self.db.get("load_count", 0)
        
        # Calculate memory (example)
        import sys
        memory = sys.getsizeof(self.db)
        memory_fmt = self.format_size(memory)
        
        # Build statistics
        stats_title = self.localise("stats")
        stats = (
            f"**{stats_title}**\\n"
            f"⏱️ Uptime: {uptime}\\n"
            f"🔄 Loads: {load_count}\\n"
            f"📦 DB Size: {db_size} keys\\n"
            f"💾 Memory: {memory_fmt}"
        )
        
        self.show_bulletin(stats, "info")
        return HookResult()
    
    @command("export")
    def export_cmd(self, param, account):
        """Export database to clipboard"""
        import json
        
        # Export database
        data = dict(self.db)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Copy to clipboard
        self.copy_to_clipboard(json_str, show_bulletin=False)
        
        # Show confirmation
        size = self.format_size(len(json_str.encode()))
        self.show_bulletin(
            f"✅ Database exported!\\n"
            f"📋 Size: {size}\\n"
            f"📦 Keys: {len(data)}",
            "success"
        )
        
        return HookResult()
    
    @command("clear")
    def clear_cmd(self, param, account, confirm: str = ""):
        """Clear database: .clear yes"""
        if confirm != "yes":
            self.show_bulletin(
                "⚠️ This will delete all data!\\n"
                "Use: .clear yes",
                "warning"
            )
            return HookResult()
        
        # Clear database but keep initialization flag
        keys_to_delete = [k for k in self.db.keys() if k != "initialized"]
        for key in keys_to_delete:
            self.db.pop(key)
        
        self.warn("Database cleared by user")
        self.show_bulletin("✅ Database cleared!", "success")
        return HookResult()
    
    @command("test")
    def test_cmd(self, param, account):
        """Test all features"""
        
        def background_task():
            """Run in background"""
            self.debug("Background task started")
            time.sleep(2)
            
            # Show result on UI thread
            self.run_on_ui_thread(
                lambda: self.show_bulletin("✅ Background task completed!", "success")
            )
        
        # Start background task
        self.run_on_queue(background_task)
        
        # Show immediate feedback
        self.show_bulletin("⏳ Testing in background...", "info")
        return HookResult()
```

---

**Next:** [Storage & Caching](storage-caching.md) | **Previous:** [Command System](command-system.md)
