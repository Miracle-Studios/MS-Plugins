# 🎨 UI Components

**User interface helpers and notification system**

---

## BulletinHelper

### Overview

Display notifications to users:

```python
from MSLib import BulletinHelper

# Show notification
BulletinHelper.show_bulletin(
    plugin_class=YourPlugin,
    title="Hello!",
    message="This is a notification",
    type="info"
)
```

### Types

```python
# Info (blue)
self.show_bulletin("Information message", "info")

# Success (green)
self.show_bulletin("Operation successful!", "success")

# Warning (yellow)
self.show_bulletin("Warning message", "warn")

# Error (red)
self.show_bulletin("Error occurred", "error")
```

### MSPlugin Shortcut

```python
class MyPlugin(MSPlugin, BasePlugin):
    
    @command("test")
    def test_cmd(self, param, account):
        # Direct method
        self.show_bulletin("Test message", "info")
        return HookResult()
```

---

## AlertDialogBuilder

### Basic Dialog

```python
from MSLib import AlertDialogBuilder

# Create alert dialog
dialog = (
    AlertDialogBuilder()
    .setTitle("Confirm Action")
    .setMessage("Are you sure?")
    .setPositiveButton("Yes", lambda d, w: self.on_yes())
    .setNegativeButton("No", lambda d, w: self.on_no())
    .create()
)

dialog.show()
```

### Complete Example

```python
@command("delete")
def delete_cmd(self, param, account, item: str):
    """Delete item with confirmation"""
    
    def on_confirmed(dialog, which):
        # Delete the item
        self.db.pop(f"item_{item}")
        self.show_bulletin(f"🗑️ Deleted: {item}", "success")
    
    def on_cancelled(dialog, which):
        self.show_bulletin("❌ Cancelled", "info")
    
    # Show confirmation dialog
    dialog = (
        AlertDialogBuilder()
        .setTitle("Delete Item")
        .setMessage(f"Delete '{item}'?")
        .setPositiveButton("Delete", on_confirmed)
        .setNegativeButton("Cancel", on_cancelled)
        .create()
    )
    
    dialog.show()
    return HookResult()
```

---

## Spinner

### Loading Indicator

```python
from MSLib import Spinner

# Create spinner
spinner = Spinner(context, text="Loading...")

# Show spinner
spinner.show()

# Hide when done
def on_complete():
    spinner.dismiss()
    self.show_bulletin("Done!", "success")
```

---

## Advanced Patterns

### Progress Notifications

```python
def process_items(self, items: list):
    """Process items with progress updates"""
    total = len(items)
    
    for i, item in enumerate(items, 1):
        # Process item
        self.process_item(item)
        
        # Show progress
        progress = int((i / total) * 100)
        self.show_bulletin(
            f"Processing... {progress}%\\n{i}/{total} items",
            "info"
        )
```

### Multi-step Wizard

```python
@command("wizard")
def wizard_cmd(self, param, account):
    """Start configuration wizard"""
    self.wizard_step = 1
    self.show_step_1()
    return HookResult()

def show_step_1(self):
    dialog = (
        AlertDialogBuilder()
        .setTitle("Step 1: Choose Mode")
        .setMessage("Select operation mode")
        .setPositiveButton("Advanced", lambda d, w: self.show_step_2("advanced"))
        .setNegativeButton("Simple", lambda d, w: self.show_step_2("simple"))
        .create()
    )
    dialog.show()

def show_step_2(self, mode: str):
    self.db.set("mode", mode)
    
    dialog = (
        AlertDialogBuilder()
        .setTitle("Step 2: Confirm")
        .setMessage(f"Mode: {mode}\\n\\nProceed?")
        .setPositiveButton("Finish", lambda d, w: self.finish_wizard())
        .setNegativeButton("Back", lambda d, w: self.show_step_1())
        .create()
    )
    dialog.show()

def finish_wizard(self):
    mode = self.db.get("mode")
    self.show_bulletin(f"✅ Configured: {mode}", "success")
```

### Notification Queue

```python
class NotificationQueue:
    """Queue notifications to avoid spam"""
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.queue = []
        self.is_showing = False
    
    def add(self, message: str, type: str = "info"):
        """Add notification to queue"""
        self.queue.append((message, type))
        self.show_next()
    
    def show_next(self):
        """Show next notification"""
        if self.is_showing or not self.queue:
            return
        
        self.is_showing = True
        message, type = self.queue.pop(0)
        
        self.plugin.show_bulletin(message, type)
        
        # Wait 2 seconds before next
        def continue_queue():
            time.sleep(2)
            self.is_showing = False
            self.show_next()
        
        self.plugin.run_on_queue(continue_queue)

# Usage:
class MyPlugin(MSPlugin, BasePlugin):
    def __init__(self):
        super().__init__()
        self.notifications = NotificationQueue(self)
    
    @command("bulk")
    def bulk_cmd(self, param, account):
        for i in range(5):
            self.notifications.add(f"Processing {i+1}/5", "info")
        return HookResult()
```

---

## Best Practices

### ✅ DO

1. **Use appropriate types** (info/success/warn/error)
2. **Keep messages short** (2-3 lines max)
3. **Use emojis** for visual clarity
4. **Show progress** for long operations
5. **Confirm destructive actions** with dialogs

### ❌ DON'T

1. **Don't spam** notifications
2. **Don't use long text** in bulletins
3. **Don't forget to dismiss** spinners
4. **Don't use dialogs** for simple info

---

**Next:** [File System](file-system.md) | **Previous:** [Telegram API](telegram-api.md)
