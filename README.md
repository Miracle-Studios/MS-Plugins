# 🌟 MiracleS Library v2.0

> Мощная, многофункциональная библиотека утилит для разработки плагинов exteraGram

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)]()
[![Lines](https://img.shields.io/badge/lines-1292-green.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)]()
[![exteraGram](https://img.shields.io/badge/exteraGram-11.12.1+-red.svg)]()

---

## ✨ Возможности

### 🗄️ Система кеширования
- **CacheFile** - бинарные файлы с опциональным zlib сжатием
- **JsonCacheFile** - типизированный JSON с дефолтными значениями
- Автоматическое создание директорий
- Безопасная обработка ошибок

### 🎯 Продвинутая система команд
- **Dispatcher** - мощный диспетчер команд с приоритетами
- Автоматическая типизация аргументов (`str`, `int`, `float`, `bool`, `Optional`, `Union`)
- Поддержка подкоманд любой вложенности
- Кастомные префиксы и обработчики ошибок
- Вариативные аргументы (`*args`)

### 📝 HTML/Markdown парсеры
- **HTML** парсер для Telegram форматирования
- **Markdown** парсер с полной поддержкой TG синтаксиса
- Конвертация между форматами
- Поддержка всех Telegram сущностей (bold, italic, links, spoilers, emoji, и т.д.)

### 🔄 AutoUpdater
- Автоматическая проверка обновлений плагинов
- Загрузка из Telegram каналов
- Настраиваемый интервал проверки
- Принудительная проверка обновлений
- Кеширование состояния обновлений

### 📡 Telegram API Wrapper
- Удобные методы для работы с API
- `Requests.get_user()` - получение информации о пользователях
- `Requests.get_chat()` - получение информации о чатах
- `Requests.send()` - отправка произвольных запросов
- Автоматическая обработка ошибок

### 🎨 UI Компоненты
- **AlertDialogBuilder** - диалоговые окна
- **BulletinHelper** - красивые уведомления с префиксами
- Уведомления с копированием в буфер
- Уведомления с переходом к сообщениям
- Поддержка кастомных иконок

### 🔧 Утилиты
- **CustomLogger** - расширенное логирование с форматированием
- **Callback1/2/5** - обертки для Java callbacks
- Конвертеры Python ↔ Java коллекций
- Работа с буфером обмена
- Форматирование исключений
- Singleton паттерн
- Companion для персистентности данных

### 🌐 Локализация
- Поддержка английского и русского языков
- Автоматическое определение системной локали
- Легкое добавление новых языков
- Функция `localise()` для получения строк

---

## 📦 Установка

1. Скопируйте `src/MSLib.py` в директорию вашего проекта
2. В exteraGram установите плагин `MSLib.plugin`
3. Импортируйте необходимые компоненты в ваш плагин:

```python
from src.MSLib import (
    # Кеш
    CacheFile, JsonCacheFile,
    # Команды
    Dispatcher, create_command,
    # Парсеры
    HTML, Markdown, link,
    # Callback
    Callback1, Callback2,
    # Утилиты
    build_log, format_exc,
    # AutoUpdater
    AutoUpdater, UpdaterTask,
    # Requests
    Requests,
    # UI
    UI, build_bulletin_helper,
)
```

---

## 🚀 Быстрый старт

### Простой плагин с командами

```python
from base_plugin import BasePlugin, HookResult
from src.MSLib import Dispatcher, build_log, JsonCacheFile

class MyPlugin(BasePlugin):
    def on_plugin_load(self):
        self.logger = build_log("MyPlugin")
        self.cache = JsonCacheFile("my_data.json", default={"count": 0})
        self.dp = Dispatcher("my_plugin", prefix=".")
        
        @self.dp.register_command("count")
        def count_cmd(param, account: int):
            self.cache.content["count"] += 1
            self.cache.write()
            count = self.cache.content["count"]
            self.logger.info(f"Count: {count}")
            return HookResult.CONSUME
```

### Работа с кешем

```python
from src.MSLib import CacheFile, JsonCacheFile

# Бинарный кеш с сжатием
cache = CacheFile("data.bin", compress=True)
cache.content = b"Hello, World!"
cache.write()

# JSON кеш
settings = JsonCacheFile("settings.json", default={"enabled": True})
settings.content["enabled"] = False
settings.write()
```

### Уведомления

```python
from src.MSLib import build_bulletin_helper

bulletin = build_bulletin_helper("MyPlugin")
bulletin.show_success("Operation completed!")
bulletin.show_info_with_copy("Your token", "abc123xyz")
```

### HTML парсинг

```python
from src.MSLib import HTML, link

# Создание ссылки
url = link("Click here", "https://example.com")

# Парсинг HTML
text, entities = HTML.parse("<b>Bold</b> and <i>italic</i>")
```

---

## 📚 Документация

- **[API Reference](MSLIB_API_REFERENCE.md)** - полная документация по API
- **[Usage Examples](MSLIB_USAGE_EXAMPLES.py)** - примеры использования всех возможностей
- **[Migration Guide](QUICK_FIX_GUIDE.md)** - миграция на новую версию exteraGram

---

## 🎓 Примеры

### Команда с аргументами

```python
@dp.register_command("greet")
def greet_cmd(param, account: int, name: str, age: int = 0):
    """Поздороваться с пользователем"""
    if age:
        message = f"Hello, {name}! You are {age} years old."
    else:
        message = f"Hello, {name}!"
    return HookResult.CONSUME
```

Использование:
- `.greet Alice` → "Hello, Alice!"
- `.greet Bob 25` → "Hello, Bob! You are 25 years old."

### Подкоманды

```python
@dp.register_command("settings")
def settings_cmd(param, account: int):
    return HookResult.CONSUME

@settings_cmd.subcommand("show")
def settings_show(param, account: int):
    """Показать настройки"""
    return HookResult.CONSUME

@settings_cmd.subcommand("set")
def settings_set(param, account: int, key: str, value: str):
    """Установить значение"""
    return HookResult.CONSUME
```

Использование:
- `.settings show` → показать настройки
- `.settings set theme dark` → установить тему

### AutoUpdater

```python
from src.MSLib import autoupdater, UpdaterTask

def on_plugin_load(self):
    if autoupdater:
        task = UpdaterTask(
            plugin_id="my_plugin",
            channel_id=1234567890,
            message_id=100
        )
        autoupdater.add_task(task)
```

---

## 📊 Статистика

- **1292** строки кода
- **80+** функций и методов
- **20+** классов
- **2** языка локализации (EN, RU)
- **11** категорий функциональности

---

## 🏗️ Архитектура

```
MSLib v2.0
├── Кеширование
│   ├── CacheFile (binary + compression)
│   └── JsonCacheFile (typed JSON)
├── Команды
│   ├── Dispatcher
│   ├── Command
│   ├── ArgSpec
│   └── Type casting
├── Парсеры
│   ├── HTML
│   ├── Markdown
│   └── Entities
├── AutoUpdater
│   ├── UpdaterTask
│   └── Threading
├── API
│   └── Requests wrapper
├── UI
│   ├── AlertDialogBuilder
│   └── BulletinHelper
├── Утилиты
│   ├── Logging
│   ├── Callbacks
│   ├── Converters
│   └── Clipboard
└── Паттерны
    ├── Singleton
    └── Companion
```

---

## 🔧 Технические детали

### Требования
- **Python:** 3.8+
- **exteraGram:** 11.12.1+
- **Jython:** Bridge для Java/Android API

### Зависимости
- `base_plugin` - базовый класс плагинов
- `android_utils` - Android утилиты
- `client_utils` - Telegram клиент утилиты
- `ui.*` - UI компоненты
- `packaging` - версионирование
- `typing_extensions` - расширенная типизация

### Производительность
- ✅ Ленивая инициализация
- ✅ Кеширование результатов
- ✅ Опциональное сжатие данных (zlib)
- ✅ Эффективные Java ↔ Python конвертеры
- ✅ Thread-safe операции

---

## 🐛 Известные ограничения

1. **Импорты Java/Android** - показывают ошибки в IDE, но работают в runtime
2. **Companion** - требует перезагрузки плагина для импорта изменений
3. **AutoUpdater** - проверка обновлений требует активного интернет-соединения

---

## 🤝 Вклад в развитие

Используйте шаблоны `cactuslib.plugin.py` и `zwyLib.plugin.py` как примеры для расширения функциональности MSLib.

---

## 📝 История изменений

### v2.0.0 (30 ноября 2025)
- ✨ Полная переработка библиотеки
- ➕ Добавлена система команд с типизацией
- ➕ HTML/Markdown парсеры
- ➕ AutoUpdater
- ➕ Requests wrapper
- ➕ UI утилиты
- ➕ Расширенные Callbacks (1, 2, 5 аргументов)
- ➕ Локализация EN/RU
- ➕ Singleton и Companion паттерны
- 🔧 Улучшенное логирование
- 🔧 Оптимизация производительности

### v1.0.0
- 🎉 Первый релиз
- 📦 Базовое кеширование
- 📝 Простое логирование

---

## 👥 Авторы

**MiracleS Team**
- @Imrcle
- @MiracleS_Team

Вдохновлено и основано на лучших практиках из:
- `cactuslib` by @CactusPlugins
- `zwyLib` by @zwylair

---

## 📄 Лицензия

Этот проект разработан для использования с exteraGram.  
Смотрите официальную документацию exteraGram для деталей.

---

## 🔗 Ссылки

- **Документация API:** [MSLIB_API_REFERENCE.md](MSLIB_API_REFERENCE.md)
- **Примеры:** [MSLIB_USAGE_EXAMPLES.py](MSLIB_USAGE_EXAMPLES.py)
- **Исходный код:** [src/MSLib.py](src/MSLib.py)

---

<div align="center">

**Сделано с ❤️ командой MiracleS**

⭐ Если MSLib полезна для вас, поддержите проект!

</div>
