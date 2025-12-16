# 📡 Telegram API

**Extended Telegram API helpers and utilities**

---

## TelegramAPI Class

### Overview

```python
from MSLib import TelegramAPI

api = TelegramAPI()
```

### Result Wrapper

```python
result = TelegramAPI.Result()

# After request completes:
if result.error:
    print(f"Error: {result.error}")
else:
    print(f"Success: {result.response}")
```

### Exception Handling

```python
try:
    api.send(request, account, callback)
except TelegramAPI.TLRPCException as e:
    print(f"Code: {e.code}")
    print(f"Text: {e.text}")
    print(f"Request ID: {e.req_id}")
```

---

## Requests Helper

### Get User

```python
from MSLib import Requests, Callback1

def on_user_received(user):
    """Handle user data"""
    print(f"User: {user.first_name}")

def on_error(error):
    """Handle error"""
    print(f"Error: {error}")

# Get user
Requests.get_user(
    user_id=123456789,
    callback=Callback1(on_user_received),
    account=account
)
```

### Get Chat

```python
def on_chat_received(chat):
    print(f"Chat: {chat.title}")

Requests.get_chat(
    chat_id=-1001234567890,
    callback=Callback1(on_chat_received),
    account=account
)
```

### Get Full User

```python
def on_full_user(full_user):
    print(f"About: {full_user.about}")
    print(f"Common chats: {full_user.common_chats_count}")

Requests.get_full_user(
    user_id=123456789,
    callback=Callback1(on_full_user),
    account=account
)
```

### Search Messages

```python
from MSLib import TelegramAPI

def on_messages(messages):
    for msg in messages:
        print(f"Message: {msg.message}")

Requests.search_messages(
    peer=peer,
    query="search text",
    filter=TelegramAPI.SearchFilter.PHOTOS,
    callback=Callback1(on_messages),
    account=account
)
```

---

## Search Filters

```python
from MSLib import TelegramAPI

# Available filters:
TelegramAPI.SearchFilter.PHOTOS
TelegramAPI.SearchFilter.VIDEO
TelegramAPI.SearchFilter.DOCUMENTS
TelegramAPI.SearchFilter.MUSIC
TelegramAPI.SearchFilter.GIF
TelegramAPI.SearchFilter.VOICE
TelegramAPI.SearchFilter.URL
# And more...
```

---

## Complete Example

```python
from MSLib import MSPlugin, command, Requests, Callback1
from base_plugin import BasePlugin, HookResult

class TelegramAPIPlugin(MSPlugin, BasePlugin):
    
    @command("userinfo")
    def userinfo_cmd(self, param, account, user_id: int):
        """Get user info: .userinfo 123456789"""
        
        def on_user(user):
            info = (
                f"👤 **User Info**\\n"
                f"ID: `{user.id}`\\n"
                f"Name: {user.first_name}\\n"
                f"Username: @{user.username or 'None'}"
            )
            self.show_bulletin(info, "info")
        
        def on_error(error):
            self.show_bulletin(f"❌ Error: {error}", "error")
        
        Requests.get_user(
            user_id,
            Callback1(on_user),
            account
        )
        
        self.show_bulletin("⏳ Loading user info...", "info")
        return HookResult()
    
    @command("searchphotos")
    def searchphotos_cmd(self, param, account, query: str):
        """Search photos: .searchphotos cat"""
        
        def on_messages(messages):
            count = len(messages) if messages else 0
            self.show_bulletin(f"📸 Found {count} photos", "success")
        
        Requests.search_messages(
            peer=param.peer,
            query=query,
            filter=TelegramAPI.SearchFilter.PHOTOS,
            callback=Callback1(on_messages),
            account=account
        )
        
        return HookResult()
```

---

**Next:** [Inline Buttons](inline-buttons.md) | **Previous:** [Storage](storage-caching.md)
