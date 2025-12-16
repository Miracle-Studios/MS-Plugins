# ⚡ Command System

**Advanced command handling framework with middleware, aliases, subcommands, and more**

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Basic Usage](#basic-usage)
3. [Command Decorator](#command-decorator)
4. [Command Arguments](#command-arguments)
5. [Aliases](#aliases)
6. [Subcommands](#subcommands)
7. [Middleware & Hooks](#middleware--hooks)
8. [Command Context](#command-context)
9. [Error Handling](#error-handling)
10. [Dynamic Control](#dynamic-control)
11. [Help Generation](#help-generation)
12. [Advanced Patterns](#advanced-patterns)
13. [Best Practices](#best-practices)

---

## Overview

MSLib's command system provides a powerful framework for handling user commands with automatic argument parsing, type conversion, validation, and error handling.

### Key Features

- 🎯 **Automatic Argument Parsing** - Parse and convert arguments automatically
- 🏷️ **Type Safety** - Support for str, int, float, bool, Optional, Union
- 🔄 **Aliases** - Multiple names for the same command
- 📂 **Subcommands** - Hierarchical command structures
- 🎭 **Middleware** - Before/after execution hooks
- 📝 **Auto Help** - Generate help text automatically
- ❌ **Error Handling** - Custom error handlers per command
- 🔧 **Dynamic Control** - Enable/disable commands at runtime
- 💬 **Quoted Args** - Support for "arguments with spaces"

---

## Basic Usage

### Simple Command

```python
from MSLib import command
from base_plugin import HookResult

class MyPlugin(MSPlugin, BasePlugin):
    @command("hello")
    def hello_cmd(self, param, account):
        """Say hello to the user"""
        self.show_bulletin("Hello, World!", "success")
        return HookResult()
```

**Usage:** `.hello`

### Command with Arguments

```python
@command("greet")
def greet_cmd(self, param, account, name: str):
    """Greet someone by name"""
    self.show_bulletin(f"Hello, {name}!", "success")
    return HookResult()
```

**Usage:** `.greet John`

### Multiple Arguments with Types

```python
@command("calc")
def calc_cmd(self, param, account, a: int, b: int):
    """Add two numbers"""
    result = a + b
    self.show_bulletin(f"{a} + {b} = {result}", "info")
    return HookResult()
```

**Usage:** `.calc 5 10` → `5 + 10 = 15`

---

## Command Decorator

### Syntax

```python
@command(cmd=None, *, aliases=None, doc=None, enabled=None)
def command_func(self, param, account, ...args):
    pass
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cmd` | `str` | Command name (uses function name if omitted) |
| `aliases` | `List[str]` | Alternative names for the command |
| `doc` | `str` | Documentation key in strings dict |
| `enabled` | `str\|bool` | Enable/disable via settings or boolean |

### Examples

```python
# Simple command
@command()
def test(self, param, account):
    pass

# Named command
@command("hello")
def greet(self, param, account):
    pass

# With aliases
@command("calc", aliases=["c", "math"])
def calculator(self, param, account, expr: str):
    pass

# With documentation key
@command("info", doc="info_command_description")
def show_info(self, param, account):
    pass

# Conditionally enabled
@command("admin", enabled="enable_admin_commands")
def admin_cmd(self, param, account):
    pass
```

---

## Command Arguments

### Required vs Optional Arguments

Every command receives two mandatory arguments first:
1. `param` - CommandParams with message data
2. `account` - User account instance

Additional arguments are parsed from the command text.

```python
@command("example")
def example_cmd(self, param, account, required: str, optional: str = "default"):
    """
    param - CommandParams (always present)
    account - User account (always present)
    required - Must be provided
    optional - Uses default if not provided
    """
    pass
```

**Usage:** 
- `.example hello` → `required="hello"`, `optional="default"`
- `.example hello world` → `required="hello"`, `optional="world"`

### Supported Types

| Type | Description | Example |
|------|-------------|---------|
| `str` | String | `"hello"` |
| `int` | Integer | `42` |
| `float` | Float | `3.14` |
| `bool` | Boolean | `true`, `false`, `1`, `0` |
| `Optional[T]` | Optional type | `None` or value |
| `Union[T1, T2]` | Multiple types | Tries each type |

### Type Conversion

```python
@command("mixed")
def mixed_cmd(self, param, account, text: str, num: int, flag: bool):
    """Automatic type conversion"""
    self.show_bulletin(
        f"Text: {text}\\n"
        f"Number: {num}\\n"
        f"Flag: {flag}",
        "info"
    )
    return HookResult()
```

**Usage:** `.mixed hello 42 true`

### Optional Arguments

```python
@command("search")
def search_cmd(self, param, account, query: str, limit: Optional[int] = None):
    """Search with optional limit"""
    limit = limit or 10
    self.show_bulletin(f"Searching '{query}' (limit: {limit})", "info")
    return HookResult()
```

**Usage:** 
- `.search test` → `limit=10`
- `.search test 5` → `limit=5`

### Variadic Arguments

```python
@command("echo")
def echo_cmd(self, param, account, *words: str):
    """Echo multiple words"""
    text = " ".join(words)
    self.show_bulletin(text, "info")
    return HookResult()
```

**Usage:** `.echo hello world from MSLib` → `"hello world from MSLib"`

### Quoted Arguments

Arguments with spaces can be quoted:

```python
@command("msg")
def msg_cmd(self, param, account, user: str, message: str):
    """Send message to user"""
    self.show_bulletin(f"To {user}: {message}", "info")
    return HookResult()
```

**Usage:** `.msg "John Doe" "Hello, how are you?"` 

---

## Aliases

### Basic Aliases

```python
@command("calculator", aliases=["calc", "c", "math"])
def calculator_cmd(self, param, account, expr: str):
    """Calculate expression"""
    result = eval(expr)  # Be careful with eval!
    self.show_bulletin(f"{expr} = {result}", "success")
    return HookResult()
```

**Usage:** All of these work:
- `.calculator 2+2`
- `.calc 2+2`
- `.c 2+2`
- `.math 2+2`

### Dynamic Alias Management

```python
# In Dispatcher
dispatcher = Dispatcher("my_plugin")

# Add alias at runtime
dispatcher.add_alias("calculator", "compute")

# Remove alias
dispatcher.remove_alias("compute")

# Check command with aliases
cmd, aliases = dispatcher.get_command_with_aliases("calculator")
```

---

## Subcommands

### Defining Subcommands

```python
@command("user")
def user_cmd(self, param, account):
    """User management"""
    self.show_bulletin("Use: .user info|list|add", "info")
    return HookResult()

# Method 1: Using @user_cmd.subcommand decorator
@user_cmd.subcommand("info")
def user_info(self, param, account, user_id: int):
    """Show user info"""
    self.show_bulletin(f"Info for user {user_id}", "info")
    return HookResult()

@user_cmd.subcommand("list")
def user_list(self, param, account):
    """List all users"""
    self.show_bulletin("User list...", "info")
    return HookResult()
```

**Usage:**
- `.user` → Shows usage
- `.user info 123` → Shows info for user 123
- `.user list` → Lists all users

### Subcommand Methods

```python
cmd = dispatcher.get_command("user")

# Check if command has subcommands
if cmd.has_subcommands():
    # Get specific subcommand
    subcmd = cmd.get_subcommand("info")
    
    # List all subcommands
    subcommand_names = cmd.list_subcommands()
```

---

## Middleware & Hooks

### Before Hooks

Execute before command runs. Can interrupt execution:

```python
def log_command(context: CommandContext) -> Optional[Any]:
    """Log all commands"""
    logger.info(f"Command: {context.command_name} by {context.account}")
    # Return None to continue, or any value to interrupt
    return None

def check_permission(context: CommandContext) -> Optional[Any]:
    """Check if user has permission"""
    if not user_has_permission(context.account):
        return HookResult.from_string("❌ No permission!")
    return None  # Continue

# Add hooks
dispatcher.add_before_hook(log_command)
dispatcher.add_before_hook(check_permission)
```

### After Hooks

Execute after command completes:

```python
def log_result(context: CommandContext, result: Any):
    """Log command result"""
    logger.info(f"Command {context.command_name} completed: {result}")

def track_usage(context: CommandContext, result: Any):
    """Track command usage statistics"""
    stats_db.increment(f"cmd_{context.command_name}")

# Add hooks
dispatcher.add_after_hook(log_result)
dispatcher.add_after_hook(track_usage)
```

### Hook Management

```python
# Remove hooks
dispatcher.remove_before_hook(log_command)
dispatcher.remove_after_hook(log_result)

# Clear all hooks
dispatcher.clear_hooks()
```

### Complete Example

```python
class MonitoredPlugin(MSPlugin, BasePlugin):
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Setup dispatcher
        self.dp = Dispatcher("monitored_plugin")
        
        # Add monitoring
        self.dp.add_before_hook(self.before_command)
        self.dp.add_after_hook(self.after_command)
        
        # Register commands
        @self.dp.register_command("test")
        def test_cmd(param, account):
            return HookResult.from_string("Test OK")
    
    def before_command(self, context: CommandContext):
        """Log and validate before execution"""
        self.log(f"Executing: {context.command_name}")
        
        # Rate limiting
        if self.is_rate_limited(context.account):
            return HookResult.from_string("⏱️ Rate limited!")
        
        return None  # Continue
    
    def after_command(self, context: CommandContext, result: Any):
        """Track after execution"""
        self.log(f"Completed: {context.command_name}")
        self.db.set(f"last_cmd_{context.account}", context.command_name)
```

---

## Command Context

### CommandContext Class

```python
@dataclass
class CommandContext:
    command_name: str              # Name of executed command
    raw_text: str                  # Original message text
    args: Tuple[Any, ...]         # Parsed arguments
    param: Any                     # CommandParams object
    account: Any                   # User account
    plugin_instance: Optional[Any] # Plugin instance
    dispatcher: Optional[Dispatcher] # Dispatcher instance
```

### Usage in Hooks

```python
def smart_hook(context: CommandContext):
    """Access all context data"""
    
    # Command info
    print(f"Command: {context.command_name}")
    print(f"Raw: {context.raw_text}")
    
    # Arguments
    param, account, *user_args = context.args
    
    # User info
    user_id = context.account.id
    
    # Plugin access
    if context.plugin_instance:
        context.plugin_instance.log("Hook executed")
    
    # Dispatcher access
    if context.dispatcher:
        all_cmds = context.dispatcher.get_all_commands()
```

---

## Error Handling

### Custom Error Handler

```python
@command("divide")
def divide_cmd(self, param, account, a: float, b: float):
    """Divide two numbers"""
    result = a / b
    self.show_bulletin(f"{a} / {b} = {result}", "success")
    return HookResult()

@divide_cmd.register_error_handler
def handle_divide_error(param, account, error: Exception):
    """Handle division errors"""
    if isinstance(error, ZeroDivisionError):
        return HookResult.from_string("❌ Cannot divide by zero!")
    elif isinstance(error, CannotCastError):
        return HookResult.from_string("❌ Invalid number format!")
    else:
        return HookResult.from_string(f"❌ Error: {error}")
```

### Automatic Error Types

The system raises these exceptions automatically:

- **`WrongArgumentAmountError`** - Wrong number of arguments
- **`CannotCastError`** - Type conversion failed
- **`MissingRequiredArguments`** - Command needs more arguments
- **`InvalidTypeError`** - Unsupported argument type

```python
@command("safe")
def safe_cmd(self, param, account, num: int):
    """Safe command with error handling"""
    result = num * 2
    return HookResult.from_string(f"Result: {result}")

@safe_cmd.register_error_handler
def handle_safe_error(param, account, error: Exception):
    """Handle all errors gracefully"""
    if isinstance(error, CannotCastError):
        return HookResult.from_string("❌ Please provide a valid number")
    elif isinstance(error, WrongArgumentAmountError):
        return HookResult.from_string("❌ Usage: .safe <number>")
    else:
        logger.error(f"Unexpected error: {error}")
        return HookResult.from_string("❌ Something went wrong")
```

---

## Dynamic Control

### Enable/Disable Commands

```python
# Disable command
dispatcher.set_command_enabled("admin", False)

# Enable command
dispatcher.set_command_enabled("admin", True)

# Check if enabled
if dispatcher.is_command_enabled("admin"):
    print("Admin commands are enabled")
```

### Bulk Operations

```python
# Enable multiple commands
dispatcher.bulk_enable_commands(["cmd1", "cmd2", "cmd3"])

# Disable multiple commands
dispatcher.bulk_disable_commands(["debug1", "debug2"])

# Enable all
dispatcher.enable_all_commands()

# Disable all
dispatcher.disable_all_commands()
```

### Conditional Enabling via Settings

```python
# Command enabled based on plugin setting
@command("vip", enabled="enable_vip_features")
def vip_cmd(self, param, account):
    """VIP-only command"""
    self.show_bulletin("Welcome, VIP!", "success")
    return HookResult()

# In settings
Switch(
    key="enable_vip_features",
    text="Enable VIP Features",
    default=False
)
```

### Reset to Defaults

```python
# Reset command to original state (from decorator)
dispatcher.reset_command("admin")
```

---

## Help Generation

### Auto-Generated Help

```python
# Generate help for specific command
help_text = dispatcher.generate_help_text("calculator", strings)

# Generate help for all commands
all_help = dispatcher.generate_all_commands_help(strings, plugin_instance)
```

### Built-in Help Command

```python
# Register automatic help command
dispatcher.register_help_command(strings)
```

**Usage:**
- `.help` → List all commands
- `.help calculator` → Show detailed help for calculator

### Help Text Format

Generated help includes:
- Command name and aliases
- Description (from doc parameter)
- Arguments with types
- Optional/required indicators
- Default values
- Subcommands list
- Usage example

Example output:
```
**calculator**

**Usage:** `calculator <expression>`

Evaluate mathematical expression

**Aliases:** calc, c, math

**Arguments:**
  • expression: str
```

### Custom Help

```python
@command("custom")
def custom_cmd(self, param, account):
    """Custom command"""
    pass

@command("help")
def help_cmd(self, param, account, cmd_name: Optional[str] = None):
    """Show help for commands"""
    if cmd_name:
        # Custom help for specific command
        if cmd_name == "custom":
            help_text = "Custom help text..."
        else:
            help_text = self.dp.generate_help_text(cmd_name)
    else:
        # List all commands
        help_text = self.dp.format_command_list(self)
    
    self.show_bulletin(help_text, "info")
    return HookResult()
```

---

## Advanced Patterns

### Command with Validation

```python
@command("age")
def age_cmd(self, param, account, age: int):
    """Set user age"""
    if not 0 <= age <= 150:
        return HookResult.from_string("❌ Invalid age (0-150)")
    
    self.db.set(f"age_{account.id}", age)
    self.show_bulletin(f"✅ Age set to {age}", "success")
    return HookResult()
```

### Command with State

```python
class StatefulPlugin(MSPlugin, BasePlugin):
    def __init__(self):
        super().__init__()
        self.command_state = {}
    
    @command("start")
    def start_cmd(self, param, account):
        """Start multi-step process"""
        self.command_state[account.id] = {"step": 1}
        self.show_bulletin("Step 1: Enter your name", "info")
        return HookResult()
    
    @command("next")
    def next_cmd(self, param, account, input: str):
        """Continue process"""
        state = self.command_state.get(account.id)
        if not state:
            return HookResult.from_string("Use .start first")
        
        if state["step"] == 1:
            state["name"] = input
            state["step"] = 2
            self.show_bulletin("Step 2: Enter your age", "info")
        elif state["step"] == 2:
            state["age"] = input
            self.show_bulletin(
                f"Done! Name: {state['name']}, Age: {state['age']}",
                "success"
            )
            del self.command_state[account.id]
        
        return HookResult()
```

### Command with API Call

```python
from MSLib import Requests, Callback1

@command("weather")
def weather_cmd(self, param, account, city: str):
    """Get weather for city"""
    
    def on_success(response):
        data = response.json()
        temp = data["main"]["temp"]
        self.show_bulletin(f"🌡️ {city}: {temp}°C", "info")
    
    def on_error(error):
        self.show_bulletin(f"❌ Error: {error}", "error")
    
    # Make API request
    Requests.get(
        f"https://api.weather.com/v1/city/{city}",
        on_success,
        on_error
    )
    
    self.show_bulletin("⏳ Loading weather...", "info")
    return HookResult()
```

### Command Pipeline

```python
@command("process")
def process_cmd(self, param, account, *items: str):
    """Process multiple items"""
    results = []
    
    for item in items:
        # Process each item
        processed = self.process_item(item)
        results.append(processed)
    
    # Show results
    result_text = "\\n".join(f"• {r}" for r in results)
    self.show_bulletin(f"Processed:\\n{result_text}", "success")
    return HookResult()
```

---

## Best Practices

### ✅ DO

1. **Use type hints** for automatic conversion
```python
@command("good")
def good_cmd(self, param, account, num: int, text: str):
    pass
```

2. **Add docstrings** for auto-generated help
```python
@command("documented")
def documented_cmd(self, param, account):
    """Clear description of what command does"""
    pass
```

3. **Handle errors gracefully**
```python
@command("safe")
def safe_cmd(self, param, account):
    pass

@safe_cmd.register_error_handler
def handle_error(param, account, error):
    return HookResult.from_string(f"❌ {error}")
```

4. **Use aliases for convenience**
```python
@command("calculator", aliases=["calc", "c"])
def calc_cmd(self, param, account):
    pass
```

5. **Return HookResult**
```python
@command("cmd")
def cmd(self, param, account):
    return HookResult()  # Always return
```

### ❌ DON'T

1. **Don't forget param and account**
```python
# ❌ Wrong
@command("bad")
def bad_cmd(self):
    pass

# ✅ Correct
@command("good")
def good_cmd(self, param, account):
    pass
```

2. **Don't use unsupported types**
```python
# ❌ Wrong
@command("bad")
def bad_cmd(self, param, account, data: dict):
    pass

# ✅ Correct
@command("good")
def good_cmd(self, param, account, data: str):
    data_dict = json.loads(data)
```

3. **Don't forget to return**
```python
# ❌ Wrong
@command("bad")
def bad_cmd(self, param, account):
    print("No return!")

# ✅ Correct
@command("good")
def good_cmd(self, param, account):
    return HookResult()
```

4. **Don't use mutable defaults**
```python
# ❌ Wrong
@command("bad")
def bad_cmd(self, param, account, items: list = []):
    items.append("new")

# ✅ Correct
@command("good")
def good_cmd(self, param, account, items: Optional[str] = None):
    items_list = items.split(",") if items else []
```

---

## Complete Example

```python
from MSLib import MSPlugin, command, Dispatcher, CommandContext
from base_plugin import BasePlugin, HookResult
from typing import Optional

class AdvancedCommandPlugin(MSPlugin, BasePlugin):
    """Plugin with advanced command features"""
    
    def __init__(self):
        super().__init__()
        self.dp = Dispatcher(self.id, prefix=".")
    
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Setup middleware
        self.dp.add_before_hook(self.log_command)
        self.dp.add_after_hook(self.track_usage)
        
        # Register help command
        self.dp.register_help_command(self.lstrings)
        
        self.log("Advanced command system loaded")
    
    def log_command(self, context: CommandContext):
        """Log all command executions"""
        self.log(f"CMD: {context.command_name} by {context.account.id}")
        return None  # Continue execution
    
    def track_usage(self, context: CommandContext, result):
        """Track command usage"""
        key = f"usage_{context.command_name}"
        count = self.db.get(key, 0)
        self.db.set(key, count + 1)
    
    # Simple command
    @command("hello")
    def hello_cmd(self, param, account):
        """Say hello"""
        self.show_bulletin("👋 Hello!", "success")
        return HookResult()
    
    # Command with arguments and aliases
    @command("calc", aliases=["c", "calculate"])
    def calc_cmd(self, param, account, a: int, b: int, op: str = "+"):
        """Calculate: .calc 5 10 +"""
        operations = {
            "+": a + b,
            "-": a - b,
            "*": a * b,
            "/": a / b if b != 0 else None
        }
        
        result = operations.get(op)
        if result is None:
            return HookResult.from_string("❌ Invalid operation or division by zero")
        
        self.show_bulletin(f"{a} {op} {b} = {result}", "info")
        return HookResult()
    
    # Command with error handling
    @command("divide")
    def divide_cmd(self, param, account, a: float, b: float):
        """Divide two numbers"""
        result = a / b
        self.show_bulletin(f"{a} / {b} = {result}", "success")
        return HookResult()
    
    @divide_cmd.register_error_handler
    def handle_divide_error(self, param, account, error):
        if isinstance(error, ZeroDivisionError):
            return HookResult.from_string("❌ Cannot divide by zero!")
        return HookResult.from_string(f"❌ Error: {error}")
    
    # Command with subcommands
    @command("user")
    def user_cmd(self, param, account):
        """User management"""
        self.show_bulletin("Use: .user info|list|stats", "info")
        return HookResult()
    
    @user_cmd.subcommand("info")
    def user_info(self, param, account, user_id: Optional[int] = None):
        """Show user info"""
        uid = user_id or account.id
        usage = self.db.get(f"usage_total_{uid}", 0)
        self.show_bulletin(f"User {uid}\\nCommands: {usage}", "info")
        return HookResult()
    
    @user_cmd.subcommand("stats")
    def user_stats(self, param, account):
        """Show usage statistics"""
        stats = []
        for key in self.db.keys():
            if key.startswith("usage_"):
                cmd = key.replace("usage_", "")
                count = self.db.get(key)
                stats.append(f"• {cmd}: {count}")
        
        self.show_bulletin("📊 Statistics:\\n" + "\\n".join(stats), "info")
        return HookResult()
    
    # Variadic command
    @command("echo")
    def echo_cmd(self, param, account, *words: str):
        """Echo multiple words"""
        text = " ".join(words)
        self.show_bulletin(f"🔊 {text}", "info")
        return HookResult()
    
    # Command with quoted arguments
    @command("notify")
    def notify_cmd(self, param, account, title: str, message: str):
        """Send notification: .notify "Title" "Message text"
        """
        self.show_bulletin(f"**{title}**\\n{message}", "info")
        return HookResult()
```

---

**Next:** [Auto-Updater](auto-updater.md) | **Previous:** [Quick Start](quick-start.md)
