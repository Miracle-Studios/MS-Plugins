# MSLib v2.3.6 - Instant Plugin Activation

**Release Date**: December 4, 2025  
**Author**: @Imrcle  
**Channel**: https://t.me/MSLib_Project

---

## 🎯 Main Feature: No Restart Required!

### Instant Plugin Activation
Integrated plugins now activate/deactivate **instantly** without requiring app restart. Toggle any plugin in settings and it works immediately with visual feedback.

---

## ✨ New Features

### 🔌 Smart Hook Management
- **Automatic Hook Registration**: All integrated plugin hooks are registered on plugin load
- **Setting-Based Activation**: Each hook checks its setting every time it's called
- **Zero Restart Requirement**: Toggle plugins on/off instantly - no app restart needed
- **Visual Feedback**: Success/info notifications when enabling/disabling plugins

### 📢 Localized Notifications
Added 8 new notification strings (English + Russian):
- `hashtags_fix_enabled` / `hashtags_fix_disabled`
- `article_viewer_fix_enabled` / `article_viewer_fix_disabled`  
- `no_call_confirmation_enabled` / `no_call_confirmation_disabled`
- `old_bottom_forward_enabled` / `old_bottom_forward_disabled`

### 🎨 Enhanced User Experience
- **Green notification** (✅) when enabling a plugin
- **Blue notification** (ℹ️) when disabling a plugin
- Instant visual confirmation of settings changes
- No confusing "Restart Required" dialogs

---

## 🔧 Technical Improvements

### Refactored Hook System
**Before (v2.3.5)**:
```python
# Hooks registered conditionally
if self.get_setting("enable_hashtags_fix", False):
    # Register hook
# User had to restart app to apply changes
```

**After (v2.3.6)**:
```python
# All hooks registered at startup
self.hook_method(method, HashTagsFixHook(self))

# Hook checks setting on every call
def replace_hooked_method(self, param):
    if not self.plugin.get_setting("enable_hashtags_fix", False):
        return  # Disabled - do nothing
    # ... hook logic
```

### Updated Hook Classes
All integrated plugin hooks now include setting checks:

1. **HashTagsFixHook** - Already had check ✅
2. **ArticleViewerFixHook** - Added setting check ✨ NEW
3. **NoCallConfirmationHook** - Already had check ✅
4. **OldBottomForwardHook** - Added setting check ✨ NEW

### Simplified Callback
```python
def _on_integrated_plugin_toggle(self, key: str, value: bool):
    """Instant activation with user feedback"""
    plugin_name = key.replace("enable_", "")
    status = "enabled" if value else "disabled"
    level = "success" if value else "info"
    
    _bulletin(level, localise(f"{plugin_name}_{status}"))
```

---

## 🗑️ Removed Features

### Eliminated Complex Hook Management
- ❌ Removed `self.active_hooks` dictionary (no longer needed)
- ❌ Removed `unhook_method()` calls (hooks stay registered)
- ❌ Removed "Restart Required" dialog (instant activation)
- ❌ Removed 4 toggle methods (`_toggle_hashtags_fix`, etc.)
- **Result**: ~140 lines of complex code eliminated

---

## 📊 Code Optimization

### Statistics
- **Lines Removed**: 143 lines (complex toggle logic)
- **Lines Added**: 25 lines (simple setting checks)
- **Net Change**: -118 lines
- **Complexity**: Significantly reduced
- **Reliability**: Improved (no hook removal errors possible)

### Performance
- **Startup**: Same (all hooks registered once)
- **Runtime**: Minimal overhead (single boolean check per hook call)
- **Memory**: Reduced (no hook tracking dictionary)

---

## 🐛 Bug Fixes

### Fixed: Restart Requirement
**Issue**: Users had to restart exteraGram app after enabling/disabling integrated plugins  
**Cause**: Hooks were only registered at plugin load time  
**Solution**: Register all hooks at startup, let them check settings dynamically  
**Status**: ✅ **RESOLVED**

### Fixed: No User Feedback
**Issue**: No confirmation when toggling plugin settings  
**Cause**: Missing notification system  
**Solution**: Added localized success/info notifications  
**Status**: ✅ **RESOLVED**

---

## 🔄 Upgrade Path

### From v2.3.5 → v2.3.6
1. **Automatic**: Just install the update
2. **No migration needed**: Settings preserved
3. **Immediate benefit**: Toggle plugins work instantly

### Breaking Changes
- ⚠️ **None** - Fully backward compatible

---

## 📝 Integrated Plugins

All 4 integrated plugins now support instant activation:

| Plugin | Description | Setting Check Added |
|--------|-------------|---------------------|
| **HashTags Fix** | Opens "This chat" instead of "Public Posts" on hashtag click | Already had ✅ |
| **Article Viewer Fix** | Disables swipe-to-close gesture in browser | v2.3.6 ✨ |
| **No Call Confirmation** | Skips call confirmation dialog | Already had ✅ |
| **Old Bottom Forward** | Restores classic forward dialog for bottom button | v2.3.6 ✨ |

---

## 🎓 For Developers

### How It Works
```python
# 1. All hooks registered on plugin load (once)
def _setup_integrated_plugins(self):
    self.hook_method(method, HashTagsFixHook(self))
    self.hook_method(method, ArticleViewerFixHook(self))
    # ... all 4 plugins

# 2. Each hook checks setting before executing
class HashTagsFixHook(MethodHook):
    def replace_hooked_method(self, param):
        if not self.plugin.get_setting("enable_hashtags_fix", False):
            return  # Setting disabled - hook does nothing
        
        # Setting enabled - hook executes
        # ... hook logic here

# 3. User toggles setting → next hook call sees new value → instant effect!
```

### Key Insight
Instead of adding/removing hooks dynamically (complex, error-prone), we:
1. Register hooks once
2. Make them check settings
3. Settings change → next call sees new value

**Result**: Simple, reliable, instant activation!

---

## 🔮 Future Plans

### Planned for v2.4.0
- [ ] More integrated plugins
- [ ] Plugin marketplace integration
- [ ] Advanced command permissions
- [ ] Multi-account support

---

## 📚 Full Feature List (v2.3.6)

### Core Features
✅ **Command System** - Decorator-based command registration with prefix caching  
✅ **CommandManager** - Temporal/non-temporal command management  
✅ **Companion** - Persistent state storage between plugin reloads  
✅ **JsonDB** - Simple JSON-based database  
✅ **AutoUpdater** - Automatic plugin updates with force check  
✅ **Update Notifications** - Complete localized update status messages  
✅ **Integrated Plugins** - 4 built-in plugins with instant activation  
✅ **HTML/Markdown Parser** - Telegram entity support  
✅ **Pluralization** - Russian language number forms  
✅ **FileSystem** - File operations helper  
✅ **SpinnerAlertDialog** - Loading dialogs  
✅ **Extended API** - Premium detection, localization, utilities

---

## 📄 License

MSLib is proprietary software by @Imrcle.  
**Please do not copy this code without notifying the author.**

---

## 🙏 Credits

**Developer**: @Imrcle  
**Project**: MiracleS Library  
**Platform**: exteraGram (Chaquopy Python 3.11)  
**Community**: https://t.me/MSLib_Project

---

## 📞 Support

- **Telegram Channel**: https://t.me/MSLib_Project
- **Developer**: @Imrcle
- **Issues**: Report in channel or DM

---

**Thank you for using MSLib! 🚀**

*Version 2.3.6 - Making plugin development easier, one update at a time.*
