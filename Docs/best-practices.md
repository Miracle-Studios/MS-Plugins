# ✨ Best Practices

**Guidelines for writing high-quality MSLib plugins**

---

## Code Organization

### ✅ DO

**Separate concerns:**
```python
class WellOrganizedPlugin(MSPlugin, BasePlugin):
    
    # Commands
    @command("start")
    def start_cmd(self, param, account):
        return self.handle_start(account)
    
    # Business logic
    def handle_start(self, account):
        user_data = self.get_user_data(account.id)
        self.update_stats()
        return HookResult()
    
    # Data access
    def get_user_data(self, user_id: int):
        return self.db.get(f"user_{user_id}", {})
    
    # Helpers
    def update_stats(self):
        count = self.db.get("total_starts", 0)
        self.db.set("total_starts", count + 1)
```

### ❌ DON'T

**Mix everything:**
```python
@command("start")
def start_cmd(self, param, account):
    # DON'T: All logic in one place
    user = self.db.get(f"user_{account.id}", {})
    count = self.db.get("total_starts", 0)
    self.db.set("total_starts", count + 1)
    self.show_bulletin("Started", "info")
    return HookResult()
```

---

## Error Handling

### ✅ DO

**Handle all errors gracefully:**
```python
@command("divide")
def divide_cmd(self, param, account, a: float, b: float):
    """Divide numbers"""
    try:
        if b == 0:
            return HookResult.from_string("❌ Cannot divide by zero")
        
        result = a / b
        self.show_bulletin(f"Result: {result}", "success")
    except Exception as e:
        self.log(f"Error in divide: {e}", "error")
        return HookResult.from_string(f"❌ Error: {e}")
    
    return HookResult()
```

### ❌ DON'T

**Ignore errors:**
```python
@command("divide")
def divide_cmd(self, param, account, a: float, b: float):
    # DON'T: No error handling
    result = a / b  # Crashes on b=0
    self.show_bulletin(f"Result: {result}", "success")
    return HookResult()
```

---

## Data Management

### ✅ DO

**Use structured data:**
```python
def save_user(self, user_id: int, name: str, settings: dict):
    """Save user with structured data"""
    user_data = {
        "id": user_id,
        "name": name,
        "settings": settings,
        "created_at": time.time(),
        "version": 1
    }
    self.db.set(f"user_{user_id}", user_data)

def get_user(self, user_id: int) -> dict:
    """Get user with defaults"""
    default = {
        "id": user_id,
        "name": "Unknown",
        "settings": {},
        "created_at": 0,
        "version": 1
    }
    return self.db.get(f"user_{user_id}", default)
```

### ❌ DON'T

**Use unstructured data:**
```python
# DON'T: No structure, no defaults
def save_user(self, user_id, name):
    self.db.set(f"user_{user_id}_name", name)
    self.db.set(f"user_{user_id}_time", time.time())

def get_user(self, user_id):
    # No defaults, may return None
    return self.db.get(f"user_{user_id}_name")
```

---

## Command Design

### ✅ DO

**Clear, documented commands:**
```python
@command("search", aliases=["s", "find"])
def search_cmd(self, param, account, *query: str):
    """
    Search for items
    
    Usage:
        .search <query>
        .s <query>
        .find <query>
    
    Examples:
        .search hello world
        .s "exact phrase"
    """
    if not query:
        return HookResult.from_string("❌ Provide search query")
    
    query_str = " ".join(query)
    results = self.search_items(query_str)
    
    if not results:
        return HookResult.from_string(f"❓ No results for: {query_str}")
    
    self.show_results(results)
    return HookResult()
```

### ❌ DON'T

**Unclear commands:**
```python
@command("s")
def s(self, p, a, *q):
    # DON'T: No docs, unclear names
    r = self.x(" ".join(q))
    self.y(r)
    return HookResult()
```

---

## Performance

### ✅ DO

**Cache expensive operations:**
```python
def get_data_cached(self, key: str, ttl: int = 300):
    """Get data with caching"""
    cache_key = f"cache_{key}"
    cache_time_key = f"cache_{key}_time"
    
    # Check cache
    cached = self.db.get(cache_key)
    cached_time = self.db.get(cache_time_key, 0)
    
    if cached and (time.time() - cached_time) < ttl:
        return cached
    
    # Fetch fresh data
    data = self.fetch_data(key)
    
    # Update cache
    self.db.set(cache_key, data)
    self.db.set(cache_time_key, time.time())
    
    return data
```

### ❌ DON'T

**Repeat expensive operations:**
```python
@command("show")
def show_cmd(self, param, account):
    # DON'T: Fetches every time
    data = self.fetch_expensive_data()  # Slow!
    self.show_bulletin(str(data), "info")
    return HookResult()
```

---

## User Experience

### ✅ DO

**Provide feedback:**
```python
@command("process")
def process_cmd(self, param, account, *items: str):
    """Process items with progress feedback"""
    if not items:
        return HookResult.from_string("❌ Provide items to process")
    
    total = len(items)
    self.show_bulletin(f"⏳ Processing {total} items...", "info")
    
    for i, item in enumerate(items, 1):
        self.process_item(item)
        
        if i % 5 == 0:  # Update every 5 items
            progress = int((i / total) * 100)
            self.show_bulletin(f"Processing... {progress}%", "info")
    
    self.show_bulletin(f"✅ Processed {total} items", "success")
    return HookResult()
```

### ❌ DON'T

**Leave users waiting:**
```python
@command("process")
def process_cmd(self, param, account, *items: str):
    # DON'T: No feedback during long operation
    for item in items:
        self.process_item(item)  # Silent...
    # User doesn't know what's happening!
    return HookResult()
```

---

## Security

### ✅ DO

**Validate input:**
```python
@command("setage")
def setage_cmd(self, param, account, age: int):
    """Set age with validation"""
    if not 1 <= age <= 150:
        return HookResult.from_string("❌ Age must be 1-150")
    
    self.db.set(f"user_{account.id}_age", age)
    self.show_bulletin(f"✅ Age set to {age}", "success")
    return HookResult()
```

### ❌ DON'T

**Accept anything:**
```python
@command("setage")
def setage_cmd(self, param, account, age: int):
    # DON'T: No validation
    self.db.set(f"user_{account.id}_age", age)
    return HookResult()
```

---

## Testing

### ✅ DO

**Add test commands:**
```python
@command("test")
def test_cmd(self, param, account):
    """Test plugin functionality"""
    tests = [
        ("Database", self.test_database),
        ("Storage", self.test_storage),
        ("Commands", self.test_commands)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append(f"✅ {name}: OK")
        except Exception as e:
            results.append(f"❌ {name}: {e}")
    
    self.show_bulletin("\\n".join(results), "info")
    return HookResult()

def test_database(self):
    """Test database operations"""
    # Write
    self.db.set("test_key", "test_value")
    # Read
    value = self.db.get("test_key")
    assert value == "test_value"
    # Delete
    self.db.pop("test_key")
```

---

## Documentation

### ✅ DO

**Document everything:**
```python
class WellDocumentedPlugin(MSPlugin, BasePlugin):
    """
    Example plugin demonstrating best practices.
    
    Features:
    - User management
    - Statistics tracking
    - Data export/import
    
    Commands:
    - .register <name> - Register new user
    - .stats - Show statistics
    - .export - Export data
    """
    
    def __init__(self):
        """Initialize plugin with default settings"""
        super().__init__()
        self.max_users = 1000
    
    @command("register")
    def register_cmd(self, param, account, name: str):
        """
        Register a new user.
        
        Args:
            name: User's display name (2-50 chars)
        
        Example:
            .register John
        """
        pass
```

---

## Summary Checklist

### Before releasing:

- ✅ All commands have docstrings
- ✅ Error handling in place
- ✅ User feedback for long operations
- ✅ Input validation
- ✅ Structured data storage
- ✅ No hardcoded values
- ✅ Code is organized
- ✅ Performance optimized
- ✅ Tested thoroughly
- ✅ Documentation complete

---

**Next:** [Troubleshooting](troubleshooting.md) | **Previous:** [Utilities](utilities.md)
