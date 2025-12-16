# 🚀 Quick Start Guide

**Get started with MSLib in 5 minutes**

---

## Installation

### Prerequisites

- exteraGram v12.0.0+
- Python 3.11+ (Chaquopy)
- Basic Python knowledge

### Setup

1. **Download MSLib.py** to your plugins directory:
```
/storage/emulated/0/exteraGram/plugins/MSLib.py
```

2. **Restart exteraGram** to load MSLib

3. **Verify installation**: Check plugin list in Settings → Plugins

---

## Your First Plugin

### Step 1: Create Plugin File

Create `MyFirstPlugin.plugin` in plugins directory:

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class MyFirstPlugin(MSPlugin, BasePlugin):
    """My first plugin using MSLib"""
    
    def __init__(self):
        super().__init__()
    
    def on_plugin_load(self):
        super().on_plugin_load()
        self.show_bulletin("Plugin loaded! 🎉", "success")
    
    @command("hello")
    def hello_cmd(self, param, account):
        """Say hello"""
        self.show_bulletin("Hello from my first plugin! 👋", "success")
        return HookResult()
```

### Step 2: Load Plugin

1. Go to Settings → Plugins
2. Find "MyFirstPlugin"
3. Enable it

### Step 3: Test

Type in any chat: `.hello`

You should see: "Hello from my first plugin! 👋"

---

## Core Concepts

### 1. Plugin Structure

```python
class MyPlugin(MSPlugin, BasePlugin):
    """Plugin description"""
    
    def __init__(self):
        super().__init__()
        # Initialize variables
    
    def on_plugin_load(self):
        super().on_plugin_load()
        # Setup code runs when plugin loads
```

**Key points:**
- Inherit from both `MSPlugin` and `BasePlugin`
- Always call `super().__init__()` and `super().on_plugin_load()`

### 2. Commands

```python
@command("mycommand")
def my_command(self, param, account):
    """Command description"""
    # Your code here
    return HookResult()
```

**Key points:**
- Use `@command()` decorator
- First two params: `param` and `account`
- Always return `HookResult`

### 3. Storage

```python
# Save data
self.db.set("key", "value")

# Load data
value = self.db.get("key", "default")

# Delete data
self.db.pop("key")
```

### 4. Notifications

```python
# Show success message
self.show_bulletin("Success!", "success")

# Show error
self.show_bulletin("Error!", "error")

# Show info
self.show_bulletin("Info", "info")
```

---

## Common Examples

### Counter Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class Counter(MSPlugin, BasePlugin):
    """Simple counter plugin"""
    
    @command("count")
    def count_cmd(self, param, account):
        """Increment counter"""
        count = self.db.get("count", 0)
        count += 1
        self.db.set("count", count)
        self.show_bulletin(f"Count: {count}", "info")
        return HookResult()
    
    @command("reset")
    def reset_cmd(self, param, account):
        """Reset counter"""
        self.db.set("count", 0)
        self.show_bulletin("Counter reset!", "success")
        return HookResult()
```

### Greeting Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class Greeter(MSPlugin, BasePlugin):
    """Greeting plugin"""
    
    @command("greet")
    def greet_cmd(self, param, account, name: str):
        """Greet someone: .greet John"""
        self.show_bulletin(f"Hello, {name}! 👋", "success")
        return HookResult()
    
    @command("setname")
    def setname_cmd(self, param, account, name: str):
        """Save your name"""
        self.db.set(f"name_{account.id}", name)
        self.show_bulletin(f"Name saved: {name}", "success")
        return HookResult()
    
    @command("myname")
    def myname_cmd(self, param, account):
        """Show your saved name"""
        name = self.db.get(f"name_{account.id}", "Unknown")
        self.show_bulletin(f"Your name: {name}", "info")
        return HookResult()
```

### Calculator Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class Calculator(MSPlugin, BasePlugin):
    """Simple calculator"""
    
    @command("add", aliases=["sum", "+"])
    def add_cmd(self, param, account, a: int, b: int):
        """Add two numbers: .add 5 10"""
        result = a + b
        self.show_bulletin(f"{a} + {b} = {result}", "success")
        return HookResult()
    
    @command("subtract", aliases=["sub", "-"])
    def sub_cmd(self, param, account, a: int, b: int):
        """Subtract: .subtract 10 5"""
        result = a - b
        self.show_bulletin(f"{a} - {b} = {result}", "success")
        return HookResult()
    
    @command("multiply", aliases=["mul", "*"])
    def mul_cmd(self, param, account, a: float, b: float):
        """Multiply: .multiply 5 3"""
        result = a * b
        self.show_bulletin(f"{a} × {b} = {result}", "success")
        return HookResult()
```

---

## Next Steps

### 📚 Learn More

- [Command System](command-system.md) - Advanced command features
- [Storage & Caching](storage-caching.md) - Data persistence
- [MSPlugin Overview](msplugin-overview.md) - Full plugin capabilities
- [UI Components](ui-components.md) - Settings and dialogs

### 💡 Tips

1. **Use type hints** - Automatic argument conversion
```python
def cmd(self, param, account, num: int):  # Converts to int automatically
```

2. **Add docstrings** - Shows in help
```python
@command("help")
def help_cmd(self, param, account):
    """This appears in help text"""
```

3. **Handle errors** - Graceful failure
```python
@command("safe")
def safe_cmd(self, param, account):
    pass

@safe_cmd.register_error_handler
def handle_error(param, account, error):
    return HookResult.from_string(f"Error: {error}")
```

4. **Use logging** - Debug your plugin
```python
self.log("Debug message")
self.info("Info message")
self.error("Error message")
```

5. **Test thoroughly** - Test all scenarios

---

## Troubleshooting

### Plugin doesn't load

1. Check Python syntax
2. Verify MSLib is loaded first
3. Check error logs in plugin settings
4. Ensure proper inheritance

### Command not working

1. Check command prefix (default: `.`)
2. Verify return statement (`return HookResult()`)
3. Check arguments match usage
4. Look for error handler

### Data not saving

1. Check db operations
2. Verify plugin loaded successfully
3. Check permissions
4. Look for exceptions

---

## Getting Help

- [Documentation](README.md) - Full documentation
- [Examples](examples.md) - More examples
- [GitHub Issues](https://github.com/Miracle-Studios/MSLib/issues) - Report bugs
- [Telegram](https://t.me/MiracleStudios) - Community support

---

**Ready for more?** → [Command System](command-system.md)
