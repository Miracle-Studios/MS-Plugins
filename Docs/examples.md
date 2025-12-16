# 📚 Examples Gallery

**Complete working examples for common use cases**

---

## 1. Todo List Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult
import time

class TodoPlugin(MSPlugin, BasePlugin):
    """Simple todo list plugin"""
    
    @command("todo", aliases=["t"])
    def todo_cmd(self, param, account):
        """Show todo list"""
        todos = self.db.get("todos", [])
        
        if not todos:
            self.show_bulletin("📝 No todos yet!\\nUse: .add <task>", "info")
            return HookResult()
        
        lines = ["📝 **Todo List:**\\n"]
        for i, todo in enumerate(todos, 1):
            status = "✅" if todo["done"] else "⬜"
            lines.append(f"{status} {i}. {todo['text']}")
        
        self.show_bulletin("\\n".join(lines), "info")
        return HookResult()
    
    @command("add", aliases=["a"])
    def add_cmd(self, param, account, *text: str):
        """Add todo: .add Buy milk"""
        if not text:
            return HookResult.from_string("❌ Provide task text")
        
        task_text = " ".join(text)
        todos = self.db.get("todos", [])
        
        todos.append({
            "text": task_text,
            "done": False,
            "created": time.time()
        })
        
        self.db.set("todos", todos)
        self.show_bulletin(f"✅ Added: {task_text}", "success")
        return HookResult()
    
    @command("done", aliases=["d"])
    def done_cmd(self, param, account, index: int):
        """Mark done: .done 1"""
        todos = self.db.get("todos", [])
        
        if not 1 <= index <= len(todos):
            return HookResult.from_string("❌ Invalid index")
        
        todos[index - 1]["done"] = True
        self.db.set("todos", todos)
        
        task = todos[index - 1]["text"]
        self.show_bulletin(f"✅ Completed: {task}", "success")
        return HookResult()
    
    @command("clear")
    def clear_cmd(self, param, account):
        """Clear completed tasks"""
        todos = self.db.get("todos", [])
        remaining = [t for t in todos if not t["done"]]
        removed = len(todos) - len(remaining)
        
        self.db.set("todos", remaining)
        self.show_bulletin(f"🗑️ Removed {removed} tasks", "success")
        return HookResult()
```

---

## 2. Note Taking Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class NotesPlugin(MSPlugin, BasePlugin):
    """Note taking plugin"""
    
    @command("note", aliases=["n"])
    def note_cmd(self, param, account, name: str, *content: str):
        """Save note: .note myNote Some text here"""
        if not content:
            # Show note
            note = self.db.get(f"note_{name}")
            if note:
                self.show_bulletin(f"📝 **{name}**\\n{note}", "info")
            else:
                self.show_bulletin(f"❌ Note '{name}' not found", "error")
        else:
            # Save note
            text = " ".join(content)
            self.db.set(f"note_{name}", text)
            self.show_bulletin(f"✅ Saved note: {name}", "success")
        
        return HookResult()
    
    @command("notes")
    def notes_cmd(self, param, account):
        """List all notes"""
        notes = []
        for key in self.db.keys():
            if key.startswith("note_"):
                name = key.replace("note_", "")
                notes.append(name)
        
        if not notes:
            self.show_bulletin("📝 No notes yet", "info")
        else:
            text = "📝 **Notes:**\\n• " + "\\n• ".join(notes)
            self.show_bulletin(text, "info")
        
        return HookResult()
    
    @command("delnote")
    def delnote_cmd(self, param, account, name: str):
        """Delete note: .delnote myNote"""
        key = f"note_{name}"
        if key in self.db:
            self.db.pop(key)
            self.show_bulletin(f"🗑️ Deleted: {name}", "success")
        else:
            self.show_bulletin(f"❌ Note '{name}' not found", "error")
        
        return HookResult()
```

---

## 3. Reminder Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult
import time
import threading

class ReminderPlugin(MSPlugin, BasePlugin):
    """Simple reminder plugin"""
    
    def __init__(self):
        super().__init__()
        self.timer_thread = None
    
    @command("remind", aliases=["r"])
    def remind_cmd(self, param, account, seconds: int, *message: str):
        """Set reminder: .remind 60 Check oven"""
        if seconds < 1 or seconds > 86400:
            return HookResult.from_string("❌ Time must be 1-86400 seconds")
        
        msg = " ".join(message) if message else "Reminder!"
        
        def reminder_task():
            time.sleep(seconds)
            self.run_on_ui_thread(
                lambda: self.show_bulletin(f"⏰ {msg}", "info")
            )
        
        self.run_on_queue(reminder_task)
        
        duration = self.format_duration(seconds)
        self.show_bulletin(f"⏰ Reminder set for {duration}", "success")
        return HookResult()
```

---

## 4. Statistics Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult
import time

class StatsPlugin(MSPlugin, BasePlugin):
    """Track usage statistics"""
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
    
    def on_plugin_load(self):
        super().on_plugin_load()
        
        # Increment load counter
        loads = self.db.get("load_count", 0)
        self.db.set("load_count", loads + 1)
    
    @command("stats", aliases=["s"])
    def stats_cmd(self, param, account):
        """Show plugin statistics"""
        
        # Uptime
        uptime = self.format_duration(int(time.time() - self.start_time))
        
        # Load count
        loads = self.db.get("load_count", 0)
        
        # Command usage
        total_cmds = self.db.get("total_commands", 0)
        user_cmds = self.db.get(f"user_{account.id}_cmds", 0)
        
        # Database size
        db_size = len(self.db)
        
        stats = (
            f"📊 **Statistics**\\n"
            f"⏱️ Uptime: {uptime}\\n"
            f"🔄 Loads: {loads}\\n"
            f"📝 Total Commands: {total_cmds}\\n"
            f"👤 Your Commands: {user_cmds}\\n"
            f"💾 DB Size: {db_size} keys"
        )
        
        self.show_bulletin(stats, "info")
        return HookResult()
    
    def track_command(self, account):
        """Track command usage (call from commands)"""
        # Total
        total = self.db.get("total_commands", 0)
        self.db.set("total_commands", total + 1)
        
        # Per user
        key = f"user_{account.id}_cmds"
        user_total = self.db.get(key, 0)
        self.db.set(key, user_total + 1)
```

---

## 5. Calculator Plugin

```python
from MSLib import MSPlugin, command
from base_plugin import BasePlugin, HookResult

class CalcPlugin(MSPlugin, BasePlugin):
    """Advanced calculator"""
    
    @command("calc", aliases=["c", "="])
    def calc_cmd(self, param, account, *expression: str):
        """Calculate: .calc 2 + 2 * 2"""
        if not expression:
            return HookResult.from_string("❌ Provide expression")
        
        expr = " ".join(expression)
        
        try:
            # Safe eval (be careful!)
            allowed = {
                'abs': abs, 'round': round,
                'min': min, 'max': max,
                'pow': pow, 'sum': sum
            }
            result = eval(expr, {"__builtins__": {}}, allowed)
            
            self.show_bulletin(f"🔢 {expr} = **{result}**", "success")
            
            # Save to history
            history = self.db.get("calc_history", [])
            history.append({"expr": expr, "result": result})
            self.db.set("calc_history", history[-10:])  # Keep last 10
            
        except Exception as e:
            self.show_bulletin(f"❌ Error: {e}", "error")
        
        return HookResult()
    
    @command("history", aliases=["h"])
    def history_cmd(self, param, account):
        """Show calculation history"""
        history = self.db.get("calc_history", [])
        
        if not history:
            self.show_bulletin("📜 No history", "info")
            return HookResult()
        
        lines = ["📜 **History:**\\n"]
        for item in history[-5:]:  # Last 5
            lines.append(f"• {item['expr']} = {item['result']}")
        
        self.show_bulletin("\\n".join(lines), "info")
        return HookResult()
```

---

**More examples coming soon!**

**Next:** [Coding Standards](coding-standards.md) | **Previous:** [API Reference](api-reference.md)
