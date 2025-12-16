# 💾 Storage & Caching

**Data persistence and caching solutions in MSLib**

---

## Overview

MSLib provides three storage solutions:
1. **JsonDB** - Simple JSON key-value database
2. **JsonCacheFile** - JSON file with caching
3. **CacheFile** - Binary file with compression
4. **MSPlugin.db** - Built-in database (recommended)

---

## JsonDB

### Basic Usage

```python
from MSLib import JsonDB

# Create database
db = JsonDB("/path/to/data.json")

# Store data
db.set("username", "John")
db.set("age", 25)
db.set("settings", {"theme": "dark", "lang": "en"})

# Retrieve data
username = db.get("username")  # "John"
age = db.get("age", 0)  # 25, default 0 if not found

# Delete data
db.pop("old_key")

# Check existence
if "username" in db:
    print("User exists")

# Iterate
for key in db.keys():
    value = db.get(key)
    print(f"{key}: {value}")

# Clear all
db.clear()
```

### Dict-like Interface

```python
# JsonDB behaves like a dict
db["key"] = "value"
value = db["key"]
del db["key"]

# Get all items
all_data = dict(db)
```

---

## MSPlugin Built-in Database

**Recommended approach** - automatic setup:

```python
class MyPlugin(MSPlugin, BasePlugin):
    
    @command("save")
    def save_cmd(self, param, account, data: str):
        """Save data"""
        # self.db is automatically initialized!
        self.db.set("data", data)
        self.show_bulletin("Saved!", "success")
        return HookResult()
    
    @command("load")
    def load_cmd(self, param, account):
        """Load data"""
        data = self.db.get("data", "No data")
        self.show_bulletin(f"Data: {data}", "info")
        return HookResult()
```

---

## CacheFile

### With Compression

```python
from MSLib import CacheFile

# Create cache file with compression
cache = CacheFile("cache.bin", compress=True, read_on_init=True)

# Write binary data
cache.write(b"Binary data here")

# Read data
data = cache.get_content()  # bytes

# Clear cache
cache.clear()
```

### Without Compression

```python
cache = CacheFile("cache.bin", compress=False)
cache.write(b"Raw binary data")
```

---

## JsonCacheFile

### JSON with Caching

```python
from MSLib import JsonCacheFile

# Create JSON cache with default value
cache = JsonCacheFile(
    "config.json",
    default={"version": 1, "enabled": True},
    read_on_init=True
)

# Write JSON data
cache.write({"version": 2, "enabled": False})

# Read JSON data
config = cache.get_content()  # dict

# Reset to default
cache.reset()
```

---

## Advanced Patterns

### User Data Management

```python
class UserManager(MSPlugin, BasePlugin):
    
    def save_user(self, user_id: int, data: dict):
        """Save user data"""
        key = f"user_{user_id}"
        self.db.set(key, data)
    
    def get_user(self, user_id: int) -> dict:
        """Get user data"""
        key = f"user_{user_id}"
        return self.db.get(key, {})
    
    def delete_user(self, user_id: int):
        """Delete user"""
        key = f"user_{user_id}"
        self.db.pop(key)
    
    def get_all_users(self) -> list:
        """Get all user IDs"""
        users = []
        for key in self.db.keys():
            if key.startswith("user_"):
                uid = int(key.replace("user_", ""))
                users.append(uid)
        return users
    
    @command("register")
    def register_cmd(self, param, account, name: str):
        """Register user"""
        user_data = {
            "name": name,
            "registered_at": time.time(),
            "commands_used": 0
        }
        self.save_user(account.id, user_data)
        self.show_bulletin(f"Registered: {name}", "success")
        return HookResult()
```

### Statistics Tracking

```python
def increment_stat(self, stat_name: str) -> int:
    """Increment and return statistic"""
    count = self.db.get(stat_name, 0)
    count += 1
    self.db.set(stat_name, count)
    return count

@command("track")
def track_cmd(self, param, account):
    """Track command usage"""
    count = self.increment_stat("total_commands")
    user_count = self.increment_stat(f"user_{account.id}_commands")
    
    self.show_bulletin(
        f"Total: {count}\\nYou: {user_count}",
        "info"
    )
    return HookResult()
```

### Cached API Responses

```python
def get_cached_or_fetch(self, key: str, fetch_func, ttl: int = 3600):
    """Get cached data or fetch if expired"""
    import time
    
    cache_key = f"cache_{key}"
    timestamp_key = f"cache_{key}_time"
    
    # Check cache
    cached_data = self.db.get(cache_key)
    cached_time = self.db.get(timestamp_key, 0)
    
    # Return cached if fresh
    if cached_data and (time.time() - cached_time) < ttl:
        return cached_data
    
    # Fetch new data
    new_data = fetch_func()
    
    # Cache it
    self.db.set(cache_key, new_data)
    self.db.set(timestamp_key, time.time())
    
    return new_data
```

---

## Best Practices

### ✅ DO

1. **Use MSPlugin.db** for most cases
2. **Use prefixes** for organizing keys
3. **Set defaults** when getting data
4. **Handle missing data** gracefully
5. **Use compression** for large data

### ❌ DON'T

1. **Don't store passwords** in plain text
2. **Don't store huge objects** (use files instead)
3. **Don't forget to handle** None values
4. **Don't mix** different data types per key

---

**Next:** [Telegram API](telegram-api.md) | **Previous:** [MSPlugin Overview](msplugin-overview.md)
