# 🔧 Troubleshooting Guide

**Common issues and solutions**

---

## Installation Issues

### Problem: Module not found

**Error:**
```
ModuleNotFoundError: No module named 'MSLib'
```

**Solution:**
- Ensure `MSLib.py` is in your plugin directory
- Check file name is exactly `MSLib.py` (case-sensitive)
- Verify file is not corrupted

---

## Command Issues

### Problem: Command not recognized

**Symptoms:**
- `.mycommand` does nothing
- No error message shown

**Solutions:**

1. **Check command registration:**
```python
# Make sure decorator is used
@command("mycommand")  # ✅ Correct
def mycommand_cmd(self, param, account):
    pass

# NOT like this:
def mycommand_cmd(self, param, account):  # ❌ Missing decorator
    pass
```

2. **Check dispatcher setup:**
```python
def on_plugin_load(self):
    super().on_plugin_load()
    # Ensure dispatcher is initialized
    if not hasattr(self, 'dispatcher'):
        self.dispatcher = Dispatcher()
```

3. **Verify command name:**
```python
# Command names must be lowercase, alphanumeric
@command("mycommand")  # ✅ OK
@command("my-command")  # ❌ Hyphens not allowed
@command("MyCommand")  # ❌ Uppercase not recommended
```

---

### Problem: Wrong number of arguments

**Error:**
```
WrongArgumentAmountError: Expected 2 arguments, got 1
```

**Solution:**

1. **Check function signature:**
```python
@command("greet")
def greet_cmd(self, param, account, name: str):  # Requires 1 arg
    pass

# Usage: .greet John  ✅
# Usage: .greet       ❌ Missing argument
```

2. **Use optional arguments:**
```python
@command("greet")
def greet_cmd(self, param, account, name: str = "World"):
    # Now optional!
    pass

# Usage: .greet John  ✅
# Usage: .greet       ✅ Uses default
```

3. **Use variadic arguments:**
```python
@command("greet")
def greet_cmd(self, param, account, *names: str):
    # Accepts any number
    pass

# Usage: .greet       ✅ Empty list
# Usage: .greet John  ✅ ["John"]
# Usage: .greet A B C ✅ ["A", "B", "C"]
```

---

## Database Issues

### Problem: Data not persisting

**Symptoms:**
- Data lost after restart
- `.get()` returns None

**Solutions:**

1. **Check database initialization:**
```python
class MyPlugin(MSPlugin, BasePlugin):
    def __init__(self):
        super().__init__()
        # self.db should be auto-initialized
        # Verify it exists:
        if not hasattr(self, 'db'):
            self.log("ERROR: Database not initialized!", "error")
```

2. **Verify data is saved:**
```python
# Always use .set() to save
self.db.set("key", "value")  # ✅ Saved

# NOT like this:
self.db["key"] = "value"  # May not persist
```

3. **Check file permissions:**
- Database file should be writable
- Check plugin directory permissions

---

### Problem: Cannot cast error

**Error:**
```
CannotCastError: Cannot cast 'abc' to <class 'int'>
```

**Solutions:**

1. **Use correct types:**
```python
@command("setage")
def setage_cmd(self, param, account, age: int):  # Expects int
    pass

# Usage: .setage 25    ✅ OK
# Usage: .setage abc   ❌ Cannot cast
```

2. **Add validation:**
```python
@command("setage")
def setage_cmd(self, param, account, age: str):  # Accept as string first
    try:
        age_int = int(age)
        if not 1 <= age_int <= 150:
            return HookResult.from_string("❌ Age must be 1-150")
        self.db.set("age", age_int)
    except ValueError:
        return HookResult.from_string("❌ Age must be a number")
    
    return HookResult()
```

---

## UI Issues

### Problem: Bulletin not showing

**Symptoms:**
- `show_bulletin()` called but nothing appears

**Solutions:**

1. **Check bulletin type:**
```python
# Valid types: "info", "success", "warn", "error"
self.show_bulletin("Message", "info")      # ✅
self.show_bulletin("Message", "invalid")   # ❌
```

2. **Check message length:**
```python
# Keep messages short
self.show_bulletin("Short message", "info")  # ✅

# Long messages may not display properly
long_msg = "x" * 1000
self.show_bulletin(long_msg, "info")  # ❌ Too long
```

3. **Use markdown formatting:**
```python
# Formatting helps readability
self.show_bulletin(
    "**Title**\\n"
    "• Item 1\\n"
    "• Item 2",
    "info"
)
```

---

## Performance Issues

### Problem: Plugin slow/laggy

**Symptoms:**
- Commands take long to execute
- UI freezes

**Solutions:**

1. **Use async for long operations:**
```python
@command("fetch")
def fetch_cmd(self, param, account):
    # DON'T: Blocks UI
    time.sleep(10)  # ❌
    
    # DO: Run in background
    def fetch_task():
        time.sleep(10)
        self.run_on_ui_thread(lambda: self.show_bulletin("Done!", "success"))
    
    self.run_on_queue(fetch_task)  # ✅
    return HookResult()
```

2. **Cache expensive operations:**
```python
# DON'T: Recalculate every time
@command("stats")
def stats_cmd(self, param, account):
    stats = self.calculate_expensive_stats()  # ❌ Slow!
    pass

# DO: Cache results
def get_stats_cached(self):
    cached = self.db.get("stats_cache")
    cache_time = self.db.get("stats_cache_time", 0)
    
    if cached and (time.time() - cache_time) < 300:  # 5 min cache
        return cached
    
    # Calculate fresh
    stats = self.calculate_expensive_stats()
    self.db.set("stats_cache", stats)
    self.db.set("stats_cache_time", time.time())
    return stats
```

3. **Optimize database queries:**
```python
# DON'T: Multiple queries in loop
for user_id in range(100):
    user = self.db.get(f"user_{user_id}")  # ❌ 100 queries!

# DO: Fetch once
all_users = {}
for key in self.db.keys():
    if key.startswith("user_"):
        all_users[key] = self.db.get(key)  # ✅ Better
```

---

## Import Issues

### Problem: Import errors

**Error:**
```
ImportError: cannot import name 'X' from 'MSLib'
```

**Solutions:**

1. **Check import names:**
```python
# Correct imports:
from MSLib import MSPlugin, command, HookResult  # ✅
from MSLib import Dispatcher, Command  # ✅
from MSLib import JsonDB, CacheFile  # ✅

# Wrong imports:
from MSLib import NonExistent  # ❌
```

2. **Use correct base class:**
```python
# Correct:
from MSLib import MSPlugin
from base_plugin import BasePlugin

class MyPlugin(MSPlugin, BasePlugin):  # ✅
    pass

# Wrong:
class MyPlugin(BasePlugin):  # ❌ Missing MSPlugin
    pass
```

---

## Debugging Tips

### Enable debug logging

```python
class MyPlugin(MSPlugin, BasePlugin):
    
    def __init__(self):
        super().__init__()
        self.debug_mode = True
    
    def debug(self, message: str):
        """Debug helper"""
        if self.debug_mode:
            self.log(f"[DEBUG] {message}", "debug")
    
    @command("test")
    def test_cmd(self, param, account):
        self.debug("test_cmd called")
        self.debug(f"Account: {account.id}")
        return HookResult()
```

### Test command pattern

```python
@command("testall")
def testall_cmd(self, param, account):
    """Test all functionality"""
    tests = {
        "Database": self.test_database,
        "Commands": self.test_commands,
        "UI": self.test_ui
    }
    
    results = []
    for name, test_func in tests.items():
        try:
            test_func()
            results.append(f"✅ {name}")
        except Exception as e:
            results.append(f"❌ {name}: {e}")
            self.log(f"Test failed: {name}", "error")
    
    self.show_bulletin("\\n".join(results), "info")
    return HookResult()
```

---

## Getting Help

1. **Check documentation** - Read relevant guide
2. **Check examples** - Look at example plugins
3. **Enable logging** - Use `self.log()` extensively
4. **Test incrementally** - Add features one at a time
5. **Ask for help** - Provide error messages and code

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | MSLib not found | Check file location |
| `WrongArgumentAmountError` | Wrong number of args | Check function signature |
| `CannotCastError` | Type conversion failed | Validate input types |
| `KeyError` | Key not in database | Use `.get()` with default |
| `AttributeError` | Missing attribute | Check initialization |

---

**Previous:** [Best Practices](best-practices.md)
