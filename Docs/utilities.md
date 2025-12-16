# 🛠️ Utilities Reference

**Complete reference for MSLib utility functions**

---

## Text Processing

### pluralization_string

Format plural forms:

```python
from MSLib import pluralization_string

# English-style (1 item, 2 items)
text = pluralization_string(5, "apple", "apples")
# Result: "5 apples"

# Russian-style (1 яблоко, 2 яблока, 5 яблок)
text = pluralization_string(5, "яблоко", "яблока", "яблок")
# Result: "5 яблок"
```

### replace_multiple_spaces

Remove extra spaces:

```python
from MSLib import replace_multiple_spaces

text = replace_multiple_spaces("Hello    World   !")
# Result: "Hello World !"
```

### split_list

Split list into chunks:

```python
from MSLib import split_list

items = [1, 2, 3, 4, 5, 6, 7, 8, 9]
chunks = split_list(items, 3)
# Result: [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
```

---

## Formatting

### format_size

Format byte size:

```python
from MSLib import format_size

size = format_size(1536)
# Result: "1.5 KB"

size = format_size(5242880)
# Result: "5 MB"
```

### format_duration

Format time duration:

```python
from MSLib import format_duration

duration = format_duration(90)
# Result: "1m 30s"

duration = format_duration(3665)
# Result: "1h 1m 5s"
```

---

## Compression

### compress_and_encode

Compress and encode data:

```python
from MSLib import compress_and_encode

# Compress string
compressed = compress_and_encode("Hello, World!" * 100)
print(f"Compressed: {len(compressed)} bytes")
```

### decode_and_decompress

Decode and decompress:

```python
from MSLib import decode_and_decompress

# Decompress
original = decode_and_decompress(compressed)
print(original)  # "Hello, World!" * 100
```

---

## Type Conversion

### smart_cast

Smart type conversion with Union/Optional support:

```python
from MSLib import smart_cast

# Basic types
result = smart_cast("42", int)  # 42
result = smart_cast("3.14", float)  # 3.14
result = smart_cast("true", bool)  # True

# Union types
from typing import Union
result = smart_cast("42", Union[int, str])  # 42 (int)
result = smart_cast("hello", Union[int, str])  # "hello" (str)

# Optional types
from typing import Optional
result = smart_cast("42", Optional[int])  # 42
result = smart_cast(None, Optional[int])  # None
```

### cast_arg

Cast argument with error handling:

```python
from MSLib import cast_arg, CannotCastError

try:
    value = cast_arg("not_a_number", int)
except CannotCastError as e:
    print(f"Cannot cast: {e}")
```

---

## Clipboard

### copy_to_clipboard

Copy text to clipboard:

```python
from MSLib import copy_to_clipboard

copy_to_clipboard("Hello, World!")
```

---

## Async Operations

### run_on_ui_thread

Run function on UI thread:

```python
def update_ui():
    self.show_bulletin("Updated!", "success")

self.run_on_ui_thread(update_ui)
```

### run_on_queue

Run function on background queue:

```python
def background_task():
    time.sleep(5)
    print("Task completed")

self.run_on_queue(background_task)
```

---

## Entity Parsing

### parse_html

Parse HTML entities:

```python
from MSLib import parse_html

text = "<b>Bold</b> and <i>italic</i>"
message_entities = parse_html(text, "entity_message")
```

### parse_markdown

Parse Markdown entities:

```python
from MSLib import parse_markdown

text = "**Bold** and *italic*"
message_entities = parse_markdown(text, "entity_message")
```

---

## Complete Example

```python
from MSLib import MSPlugin, command
from MSLib import format_size, format_duration, pluralization_string
from MSLib import compress_and_encode, decode_and_decompress
from MSLib import copy_to_clipboard, split_list
from base_plugin import BasePlugin, HookResult

class UtilitiesPlugin(MSPlugin, BasePlugin):
    """Demonstrate utility functions"""
    
    @command("format")
    def format_cmd(self, param, account):
        """Show formatting examples"""
        
        examples = [
            f"Size: {format_size(1536)} = 1.5 KB",
            f"Duration: {format_duration(3665)} = 1h 1m 5s",
            f"Plural: {pluralization_string(5, 'file', 'files')} = 5 files"
        ]
        
        self.show_bulletin("\\n".join(examples), "info")
        return HookResult()
    
    @command("compress")
    def compress_cmd(self, param, account, *text: str):
        """Compress text: .compress Hello World"""
        original = " ".join(text)
        compressed = compress_and_encode(original)
        
        ratio = (1 - len(compressed) / len(original)) * 100
        
        info = (
            f"📦 **Compression**\\n"
            f"Original: {len(original)} bytes\\n"
            f"Compressed: {len(compressed)} bytes\\n"
            f"Ratio: {ratio:.1f}%"
        )
        
        self.show_bulletin(info, "success")
        copy_to_clipboard(compressed)
        
        return HookResult()
    
    @command("decompress")
    def decompress_cmd(self, param, account, data: str):
        """Decompress data"""
        try:
            original = decode_and_decompress(data)
            self.show_bulletin(f"📦 Decompressed:\\n{original}", "success")
        except Exception as e:
            self.show_bulletin(f"❌ Error: {e}", "error")
        
        return HookResult()
    
    @command("split")
    def split_cmd(self, param, account, chunk_size: int, *items: str):
        """Split items into chunks: .split 3 a b c d e f g"""
        items_list = list(items)
        chunks = split_list(items_list, chunk_size)
        
        result = ["📦 **Chunks:**\\n"]
        for i, chunk in enumerate(chunks, 1):
            result.append(f"Chunk {i}: {', '.join(chunk)}")
        
        self.show_bulletin("\\n".join(result), "info")
        return HookResult()
    
    @command("copy")
    def copy_cmd(self, param, account, *text: str):
        """Copy to clipboard: .copy Hello World"""
        text_str = " ".join(text)
        copy_to_clipboard(text_str)
        
        self.show_bulletin(f"📋 Copied: {text_str}", "success")
        return HookResult()
```

---

## Advanced Patterns

### Batch Processing

```python
def process_batch(self, items: list, batch_size: int = 10):
    """Process items in batches"""
    chunks = split_list(items, batch_size)
    
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        # Process chunk
        self.process_items(chunk)
        
        # Show progress
        progress = int((i / total) * 100)
        self.show_bulletin(f"Processing... {progress}%", "info")
```

### Async Data Fetching

```python
@command("fetch")
def fetch_cmd(self, param, account, url: str):
    """Fetch data asynchronously"""
    
    def fetch_task():
        import requests
        response = requests.get(url)
        
        # Update UI on main thread
        def update_ui():
            size = format_size(len(response.content))
            self.show_bulletin(f"✅ Fetched: {size}", "success")
        
        self.run_on_ui_thread(update_ui)
    
    self.run_on_queue(fetch_task)
    self.show_bulletin("⏳ Fetching...", "info")
    
    return HookResult()
```

### Smart Input Parsing

```python
from MSLib import smart_cast
from typing import Union

def parse_user_input(self, value: str) -> Union[int, float, str, bool]:
    """Parse user input to appropriate type"""
    
    # Try int
    try:
        return smart_cast(value, int)
    except:
        pass
    
    # Try float
    try:
        return smart_cast(value, float)
    except:
        pass
    
    # Try bool
    if value.lower() in ["true", "false", "yes", "no"]:
        return smart_cast(value, bool)
    
    # Default to string
    return value

@command("set")
def set_cmd(self, param, account, key: str, value: str):
    """Set value with smart parsing: .set age 25"""
    parsed = self.parse_user_input(value)
    self.db.set(key, parsed)
    
    type_name = type(parsed).__name__
    self.show_bulletin(f"✅ Set {key} = {parsed} ({type_name})", "success")
    
    return HookResult()
```

---

## Best Practices

### ✅ DO

1. **Use format functions** for consistent output
2. **Compress large data** before storage
3. **Handle type conversion errors**
4. **Use async for long operations**
5. **Parse entities** for rich text

### ❌ DON'T

1. **Don't compress small data** (overhead)
2. **Don't block UI thread** with long tasks
3. **Don't forget error handling**
4. **Don't hardcode formats** (use utilities)

---

**Next:** [Best Practices](best-practices.md) | **Previous:** [Inline Buttons](inline-buttons.md)
