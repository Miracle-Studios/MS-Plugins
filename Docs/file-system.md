# 📂 File System Utilities

**File operations and utilities in MSLib**

---

## FileSystem Class

### Overview

```python
from MSLib import FileSystem

# All methods are static
FileSystem.read_file(path)
FileSystem.write_file(path, content)
```

---

## Reading Files

### Read Text File

```python
content = FileSystem.read_file("/path/to/file.txt")
print(content)  # str
```

### Read Binary File

```python
data = FileSystem.read_file_bytes("/path/to/file.bin")
print(data)  # bytes
```

### Read JSON

```python
data = FileSystem.read_json("/path/to/data.json")
print(data)  # dict/list
```

---

## Writing Files

### Write Text

```python
FileSystem.write_file("/path/to/file.txt", "Hello, World!")
```

### Write Binary

```python
FileSystem.write_file_bytes("/path/to/file.bin", b"Binary data")
```

### Write JSON

```python
data = {"name": "John", "age": 30}
FileSystem.write_json("/path/to/data.json", data)
```

---

## File Operations

### Check Existence

```python
if FileSystem.exists("/path/to/file.txt"):
    print("File exists")
```

### Get File Size

```python
size = FileSystem.get_size("/path/to/file.txt")
print(f"Size: {size} bytes")
```

### Delete File

```python
FileSystem.delete("/path/to/file.txt")
```

### Copy File

```python
FileSystem.copy("/source/file.txt", "/dest/file.txt")
```

### Move File

```python
FileSystem.move("/old/path.txt", "/new/path.txt")
```

---

## Directory Operations

### Create Directory

```python
FileSystem.mkdir("/path/to/directory")
```

### List Directory

```python
files = FileSystem.listdir("/path/to/directory")
for file in files:
    print(file)
```

### Delete Directory

```python
FileSystem.rmdir("/path/to/directory")
```

---

## Complete Example

```python
from MSLib import MSPlugin, command, FileSystem
from base_plugin import BasePlugin, HookResult

class FileManagerPlugin(MSPlugin, BasePlugin):
    """File management plugin"""
    
    @command("save")
    def save_cmd(self, param, account, filename: str, *content: str):
        """Save text to file: .save test.txt Hello World"""
        if not content:
            return HookResult.from_string("❌ Provide content")
        
        text = " ".join(content)
        path = f"/data/{filename}"
        
        try:
            FileSystem.write_file(path, text)
            size = FileSystem.get_size(path)
            
            self.show_bulletin(
                f"✅ Saved: {filename}\\nSize: {size} bytes",
                "success"
            )
        except Exception as e:
            self.show_bulletin(f"❌ Error: {e}", "error")
        
        return HookResult()
    
    @command("load")
    def load_cmd(self, param, account, filename: str):
        """Load file: .load test.txt"""
        path = f"/data/{filename}"
        
        try:
            if not FileSystem.exists(path):
                return HookResult.from_string(f"❌ File not found: {filename}")
            
            content = FileSystem.read_file(path)
            size = FileSystem.get_size(path)
            
            # Show preview (first 200 chars)
            preview = content[:200]
            if len(content) > 200:
                preview += "..."
            
            self.show_bulletin(
                f"📄 **{filename}** ({size} bytes)\\n{preview}",
                "info"
            )
        except Exception as e:
            self.show_bulletin(f"❌ Error: {e}", "error")
        
        return HookResult()
    
    @command("files")
    def files_cmd(self, param, account):
        """List files"""
        try:
            files = FileSystem.listdir("/data")
            
            if not files:
                return HookResult.from_string("📂 No files")
            
            lines = ["📂 **Files:**\\n"]
            for file in files:
                path = f"/data/{file}"
                size = FileSystem.get_size(path)
                lines.append(f"• {file} ({size} bytes)")
            
            self.show_bulletin("\\n".join(lines), "info")
        except Exception as e:
            self.show_bulletin(f"❌ Error: {e}", "error")
        
        return HookResult()
    
    @command("delete")
    def delete_cmd(self, param, account, filename: str):
        """Delete file: .delete test.txt"""
        path = f"/data/{filename}"
        
        try:
            if not FileSystem.exists(path):
                return HookResult.from_string(f"❌ File not found: {filename}")
            
            FileSystem.delete(path)
            self.show_bulletin(f"🗑️ Deleted: {filename}", "success")
        except Exception as e:
            self.show_bulletin(f"❌ Error: {e}", "error")
        
        return HookResult()
```

---

## Advanced Patterns

### Backup System

```python
import time

def backup_database(self):
    """Create database backup"""
    timestamp = int(time.time())
    backup_name = f"backup_{timestamp}.json"
    
    # Read current database
    db_data = dict(self.db)
    
    # Save to backup file
    FileSystem.write_json(f"/backups/{backup_name}", db_data)
    
    return backup_name

@command("backup")
def backup_cmd(self, param, account):
    """Create database backup"""
    try:
        name = self.backup_database()
        self.show_bulletin(f"💾 Backup created: {name}", "success")
    except Exception as e:
        self.show_bulletin(f"❌ Backup failed: {e}", "error")
    
    return HookResult()

@command("restore")
def restore_cmd(self, param, account, backup_name: str):
    """Restore from backup"""
    try:
        path = f"/backups/{backup_name}"
        
        if not FileSystem.exists(path):
            return HookResult.from_string("❌ Backup not found")
        
        # Load backup
        backup_data = FileSystem.read_json(path)
        
        # Restore to database
        self.db.clear()
        for key, value in backup_data.items():
            self.db.set(key, value)
        
        self.show_bulletin(f"✅ Restored from: {backup_name}", "success")
    except Exception as e:
        self.show_bulletin(f"❌ Restore failed: {e}", "error")
    
    return HookResult()
```

### Export/Import

```python
@command("export")
def export_cmd(self, param, account, filename: str):
    """Export data: .export mydata.json"""
    try:
        # Get all data
        data = {
            "version": "1.0",
            "exported_at": time.time(),
            "data": dict(self.db)
        }
        
        # Save
        FileSystem.write_json(f"/exports/{filename}", data)
        
        size = FileSystem.get_size(f"/exports/{filename}")
        self.show_bulletin(f"📤 Exported: {filename} ({size} bytes)", "success")
    except Exception as e:
        self.show_bulletin(f"❌ Export failed: {e}", "error")
    
    return HookResult()

@command("import")
def import_cmd(self, param, account, filename: str):
    """Import data: .import mydata.json"""
    try:
        path = f"/exports/{filename}"
        
        if not FileSystem.exists(path):
            return HookResult.from_string("❌ File not found")
        
        # Load
        imported = FileSystem.read_json(path)
        
        # Merge with current data
        for key, value in imported["data"].items():
            self.db.set(key, value)
        
        count = len(imported["data"])
        self.show_bulletin(f"📥 Imported {count} items", "success")
    except Exception as e:
        self.show_bulletin(f"❌ Import failed: {e}", "error")
    
    return HookResult()
```

---

## Best Practices

### ✅ DO

1. **Always use try-except** for file operations
2. **Check file existence** before operations
3. **Use appropriate paths** (absolute when possible)
4. **Handle encoding** properly for text files
5. **Clean up** temporary files

### ❌ DON'T

1. **Don't hardcode paths** (use configuration)
2. **Don't forget error handling**
3. **Don't leave files open** (use context managers when available)
4. **Don't store sensitive data** in plain files

---

**Next:** [Inline Buttons](inline-buttons.md) | **Previous:** [UI Components](ui-components.md)
