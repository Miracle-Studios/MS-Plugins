# 🔘 Inline Buttons Guide

**Create interactive inline button keyboards**

---

## Overview

MSLib provides `Inline` class for creating inline button keyboards with callbacks.

```python
from MSLib import Inline
```

---

## Creating Buttons

### Single Button

```python
button = Inline.Button(
    text="Click Me!",
    data="button_clicked"
)
```

### Button with Callback

```python
button = Inline.Button(
    text="Action",
    data="action_1",
    callback=self.on_button_click
)
```

---

## Creating Markup

### Single Row

```python
markup = Inline.Markup([
    Inline.Button("Button 1", "data_1"),
    Inline.Button("Button 2", "data_2"),
    Inline.Button("Button 3", "data_3")
])
```

### Multiple Rows

```python
markup = Inline.Markup([
    [Inline.Button("Row 1 Button 1", "r1b1"), Inline.Button("Row 1 Button 2", "r1b2")],
    [Inline.Button("Row 2 Button 1", "r2b1")],
    [Inline.Button("Row 3 Button 1", "r3b1"), Inline.Button("Row 3 Button 2", "r3b2")]
])
```

---

## Handling Callbacks

### Setup Callback Handler

```python
from MSLib import MSPlugin, inline_handler, Inline
from base_plugin import BasePlugin

class ButtonPlugin(MSPlugin, BasePlugin):
    
    @inline_handler
    def handle_inline(self, params: Inline.CallbackParams):
        """Handle inline button callbacks"""
        
        data = params.data  # Button data
        message = params.message  # Message object
        account = params.account  # Account object
        
        if data == "action_1":
            self.show_bulletin("Action 1 clicked!", "success")
        elif data == "action_2":
            self.show_bulletin("Action 2 clicked!", "success")
```

---

## Complete Example

```python
from MSLib import MSPlugin, command, inline_handler, Inline
from base_plugin import BasePlugin, HookResult

class MenuPlugin(MSPlugin, BasePlugin):
    """Interactive menu with buttons"""
    
    @command("menu")
    def menu_cmd(self, param, account):
        """Show interactive menu"""
        
        # Create buttons
        markup = Inline.Markup([
            [
                Inline.Button("📊 Statistics", "show_stats"),
                Inline.Button("⚙️ Settings", "show_settings")
            ],
            [
                Inline.Button("📝 About", "show_about"),
                Inline.Button("❌ Close", "close_menu")
            ]
        ])
        
        # Send message with buttons
        message_text = "**Main Menu**\\n\\nSelect an option:"
        
        # Use send_message with inline markup
        # (Implementation depends on your messaging system)
        
        return HookResult()
    
    @inline_handler
    def handle_menu_buttons(self, params: Inline.CallbackParams):
        """Handle menu button clicks"""
        
        data = params.data
        
        if data == "show_stats":
            self.show_statistics(params)
        elif data == "show_settings":
            self.show_settings(params)
        elif data == "show_about":
            self.show_about(params)
        elif data == "close_menu":
            self.close_menu(params)
    
    def show_statistics(self, params):
        """Show statistics"""
        total_cmds = self.db.get("total_commands", 0)
        self.show_bulletin(f"📊 Total commands: {total_cmds}", "info")
    
    def show_settings(self, params):
        """Show settings menu"""
        markup = Inline.Markup([
            [
                Inline.Button("🔔 Notifications", "toggle_notif"),
                Inline.Button("🌙 Dark Mode", "toggle_theme")
            ],
            [
                Inline.Button("🔙 Back", "back_to_menu")
            ]
        ])
        
        self.show_bulletin("⚙️ **Settings**", "info")
    
    def show_about(self, params):
        """Show about info"""
        about = (
            "**MenuPlugin v1.0**\\n"
            "Interactive menu demonstration\\n"
            "Made with MSLib"
        )
        self.show_bulletin(about, "info")
    
    def close_menu(self, params):
        """Close menu"""
        # Delete the message or just notify
        self.show_bulletin("Menu closed", "info")
```

---

## Advanced Patterns

### Pagination

```python
class PaginatedList(MSPlugin, BasePlugin):
    
    def __init__(self):
        super().__init__()
        self.items_per_page = 5
    
    @command("list")
    def list_cmd(self, param, account, page: int = 1):
        """Show paginated list"""
        items = self.get_all_items()
        total_pages = (len(items) + self.items_per_page - 1) // self.items_per_page
        
        # Get items for current page
        start = (page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = items[start:end]
        
        # Create pagination buttons
        buttons = []
        if page > 1:
            buttons.append(Inline.Button("⬅️ Previous", f"page_{page-1}"))
        if page < total_pages:
            buttons.append(Inline.Button("➡️ Next", f"page_{page+1}"))
        
        markup = Inline.Markup([buttons]) if buttons else None
        
        # Show items
        text = f"**Items (Page {page}/{total_pages})**\\n"
        for item in page_items:
            text += f"• {item}\\n"
        
        self.show_bulletin(text, "info")
        return HookResult()
    
    @inline_handler
    def handle_pagination(self, params: Inline.CallbackParams):
        """Handle pagination buttons"""
        if params.data.startswith("page_"):
            page = int(params.data.replace("page_", ""))
            # Re-show with new page
            # self.list_cmd(params.param, params.account, page)
```

### Confirmation Dialog

```python
@command("delete_all")
def delete_all_cmd(self, param, account):
    """Delete all data with confirmation"""
    
    markup = Inline.Markup([
        [
            Inline.Button("✅ Confirm", "confirm_delete"),
            Inline.Button("❌ Cancel", "cancel_delete")
        ]
    ])
    
    self.show_bulletin(
        "⚠️ **Delete All Data?**\\nThis cannot be undone!",
        "warn"
    )
    
    return HookResult()

@inline_handler
def handle_delete_confirm(self, params: Inline.CallbackParams):
    """Handle delete confirmation"""
    if params.data == "confirm_delete":
        self.db.clear()
        self.show_bulletin("🗑️ All data deleted", "success")
    elif params.data == "cancel_delete":
        self.show_bulletin("❌ Cancelled", "info")
```

### Interactive Poll

```python
@command("poll")
def poll_cmd(self, param, account, *question: str):
    """Create interactive poll"""
    
    question_text = " ".join(question) if question else "Sample Poll"
    poll_id = f"poll_{time.time()}"
    
    # Save poll
    self.db.set(poll_id, {
        "question": question_text,
        "votes": {"yes": 0, "no": 0, "maybe": 0}
    })
    
    # Create voting buttons
    markup = Inline.Markup([
        [
            Inline.Button("👍 Yes", f"{poll_id}_yes"),
            Inline.Button("👎 No", f"{poll_id}_no"),
            Inline.Button("🤔 Maybe", f"{poll_id}_maybe")
        ],
        [
            Inline.Button("📊 Results", f"{poll_id}_results")
        ]
    ])
    
    self.show_bulletin(f"📊 **{question_text}**", "info")
    return HookResult()

@inline_handler
def handle_poll_vote(self, params: Inline.CallbackParams):
    """Handle poll votes"""
    if "_yes" in params.data:
        poll_id = params.data.replace("_yes", "")
        self.vote_poll(poll_id, "yes")
    elif "_no" in params.data:
        poll_id = params.data.replace("_no", "")
        self.vote_poll(poll_id, "no")
    elif "_maybe" in params.data:
        poll_id = params.data.replace("_maybe", "")
        self.vote_poll(poll_id, "maybe")
    elif "_results" in params.data:
        poll_id = params.data.replace("_results", "")
        self.show_poll_results(poll_id)

def vote_poll(self, poll_id: str, option: str):
    """Record vote"""
    poll = self.db.get(poll_id)
    if poll:
        poll["votes"][option] += 1
        self.db.set(poll_id, poll)
        self.show_bulletin(f"✅ Voted: {option}", "success")

def show_poll_results(self, poll_id: str):
    """Show poll results"""
    poll = self.db.get(poll_id)
    if poll:
        results = (
            f"📊 **Poll Results**\\n"
            f"{poll['question']}\\n\\n"
            f"👍 Yes: {poll['votes']['yes']}\\n"
            f"👎 No: {poll['votes']['no']}\\n"
            f"🤔 Maybe: {poll['votes']['maybe']}"
        )
        self.show_bulletin(results, "info")
```

---

## Best Practices

### ✅ DO

1. **Use clear button text** (2-3 words max)
2. **Group related buttons** in rows
3. **Use emojis** for visual clarity
4. **Provide back/cancel** options
5. **Handle all callbacks** properly

### ❌ DON'T

1. **Don't create too many buttons** (max 8-10)
2. **Don't use long text** in buttons
3. **Don't forget error handling** in callbacks
4. **Don't nest too many levels** (max 2-3)

---

**Next:** [Utilities Reference](utilities.md) | **Previous:** [File System](file-system.md)
