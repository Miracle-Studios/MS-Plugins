"""
>>==================================================================<<
||            ███╗   ███╗ ███████╗ ██╗      ██║ ██                  ||
||            ████╗ ████║ ██╔════╝ ██║          ██                  ||
||            ██╔████╔██║ ███████╗ ██║      ██║ ██████ ╗            ||
||            ██║╚██╔╝██║ ╚════██║ ██║      ██║ ██╔══██║            ||
||            ██║ ╚═╝ ██║ ███████║ ███████╗ ██║ ██████╔╝            ||
||            ╚═╝     ╚═╝ ╚══════╝ ╚══════╝ ╚═╝ ╚═════╝             ||
||                                                                  ||
||            MiracleS Library - Powerful Utility Library           ||
||                for exteraGram Plugin Development                 ||
||                                                                  ||
||                     Version 2.1.0 | @Imrcle                      ||
||                                                                  ||
||                    https://t.me/MSLib_Project                    ||
||                                                                  ||
||                                                                  ||
||        PLEASE DO NOT COPY THIS CODE WITHOUT NOTIFYING ME.        ||
>>==================================================================<<
"""
import copy
from email.mime import text
import json
import zlib
import inspect
import logging
import os
import os.path
import sys
import threading
import traceback
import re
from enum import Enum
from html.parser import HTMLParser
from struct import unpack
from contextlib import suppress
from typing import List, Callable, Optional, Any, Union, Dict, Tuple

# Импорт get_origin и get_args с фоллбэком для Chaquopy
try:
    from typing import get_origin, get_args
except ImportError:
    # Фоллбэк для старых версий Python или Chaquopy
    def get_origin(tp):
        return getattr(tp, '__origin__', None)
    
    def get_args(tp):
        return getattr(tp, '__args__', ())

from ui.bulletin import BulletinHelper as _BulletinHelper
from ui.settings import Header, Switch, Input, Text, Divider
from ui.alert import AlertDialogBuilder
from base_plugin import BasePlugin, HookResult, MethodHook
from android_utils import log as _log, run_on_ui_thread
from client_utils import (get_messages_controller, get_last_fragment,
                          send_request, get_account_instance, send_message)

from java import cast, dynamic_proxy, jint, jarray
from java.util import Locale, ArrayList
from java.lang import Long, Integer, String, Boolean
from java.io import File
from org.telegram.tgnet import TLRPC, TLObject
from org.telegram.ui import ChatActivity
from org.telegram.messenger import (R, Utilities, AndroidUtilities, ApplicationLoader,
                                    LocaleController, MessageObject, UserConfig, AccountInstance)
from org.telegram.ui.ActionBar import Theme
from android.text import SpannableStringBuilder, Spanned, InputType
from android.view import Gravity, View
from android.widget import LinearLayout, FrameLayout, TextView
from android.util import TypedValue
from hook_utils import get_private_field, set_private_field

from org.telegram.ui import ChatActivityContainer, ArticleViewer
from org.telegram.ui.Components.voip import VoIPHelper
from org.telegram.messenger import HashtagSearchController, MediaDataController
from android.view import MotionEvent
from android.app import Activity

__id__ = "miracles_library"
__name__ = "MSLib"
__description__ = " MSLib - powerful utility library for exteraGram plugins with integrated plugins"
__icon__ = "ByMiraclePersona/3"
__author__ = "@Imrcle"
__version__ = "2.1.1"
__min_version__ = "11.12.0"


# ==================== Константы ====================
# Отложенная инициализация - будет установлено при загрузке плагина
CACHE_DIRECTORY = None
PLUGINS_DIRECTORY = None
LOCALE = "en"

# Типы для команд
ALLOWED_ARG_TYPES = (str, int, float, bool, Any)
ALLOWED_ORIGIN = (Union, Optional)

# Premium типы
NOT_PREMIUM = 0
TELEGRAM_PREMIUM = 1
MSLIB_GLOBAL_PREMIUM = 2


def _init_constants():
    """Инициализация констант (вызывается при загрузке плагина)"""
    global CACHE_DIRECTORY, PLUGINS_DIRECTORY, LOCALE
    if CACHE_DIRECTORY is None:
        CACHE_DIRECTORY = os.path.join(AndroidUtilities.getCacheDir().getAbsolutePath(), "mslib_cache")
    if PLUGINS_DIRECTORY is None:
        PLUGINS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
    try:
        LOCALE = Locale.getDefault().getLanguage()
    except:
        LOCALE = "en"


# ==================== Утилиты логирования ====================
class CustomLogger(logging.Logger):
    """Расширенный логгер с поддержкой вывода в Telegram логи"""
    
    def _log(self, level: int, msg: Any, args: Tuple[Any, ...], exc_info=None, extra=None, stack_info=False, stacklevel=1):
        caller_frame = inspect.stack()[2]
        func_name = caller_frame.function
        
        level_name = logging.getLevelName(level).upper()
        
        prefix_items = [level_name, self.name, func_name]
        prefix_items = filter(lambda i: i, prefix_items)
        prefix_items = [f"[{i}]" for i in prefix_items]
        prefix = " ".join(prefix_items)
        
        try:
            formatted_msg = str(msg) % args if args else str(msg)
        except (TypeError, ValueError):
            formatted_msg = f"{msg} {args}"
        
        _log(f"{prefix} {formatted_msg}")


logging.setLoggerClass(CustomLogger)


def build_log(tag: str, level=logging.INFO) -> logging.Logger:
    """Создает логгер с указанным тегом и уровнем"""
    logger = logging.getLogger(tag)
    logger.setLevel(level)
    return logger


logger = build_log(__name__)


def format_exc() -> str:
    """Форматирует текущее исключение"""
    return traceback.format_exc().strip()


def format_exc_from(e: Exception) -> str:
    """Форматирует исключение из объекта"""
    return "".join(traceback.format_exception(type(e), e, e.__traceback__)).strip()


def format_exc_only(e: Exception) -> str:
    """Форматирует только сообщение исключения без стека"""
    return ''.join(traceback.format_exception_only(type(e), e)).strip()


# ==================== Markdown & HTML парсеры ====================
def add_surrogates(text: str) -> str:
    """Добавляет суррогатные пары для emoji"""
    return re.compile(r"[\U00010000-\U0010FFFF]").sub(
        lambda match: "".join(chr(i) for i in unpack("<HH", match.group().encode("utf-16le"))),
        text
    )


def remove_surrogates(text: str) -> str:
    """Удаляет суррогатные пары"""
    return text.encode("utf-16", "surrogatepass").decode("utf-16")


class TLEntityType(Enum):
    """Типы текстовых сущностей Telegram"""
    CODE = 'code'
    PRE = 'pre'
    STRIKETHROUGH = 'strikethrough'
    TEXT_LINK = 'text_link'
    BOLD = 'bold'
    ITALIC = 'italic'
    UNDERLINE = 'underline'
    SPOILER = 'spoiler'
    CUSTOM_EMOJI = 'custom_emoji'
    BLOCKQUOTE = 'blockquote'


class RawEntity:
    """Сырая текстовая сущность"""
    def __init__(self, type, offset, length, extra=None):
        self.type = type
        self.offset = offset
        self.length = length
        self.extra = extra


class HTMLParser_(HTMLParser):
    """HTML парсер для Telegram сообщений"""
    
    def __init__(self):
        super().__init__()
        self.text = ""
        self.entities = []
        self.tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        self.tag_stack.append((tag, dict(attrs), len(self.text)))
    
    def handle_data(self, data):
        self.text += data
    
    def handle_endtag(self, tag):
        if not self.tag_stack or self.tag_stack[-1][0] != tag:
            return
        
        tag_name, attrs, start_pos = self.tag_stack.pop()
        length = len(self.text) - start_pos
        
        if length <= 0:
            return
        
        entity_type = None
        extra = None
        
        if tag_name == 'b' or tag_name == 'strong':
            entity_type = TLEntityType.BOLD
        elif tag_name == 'i' or tag_name == 'em':
            entity_type = TLEntityType.ITALIC
        elif tag_name == 'u':
            entity_type = TLEntityType.UNDERLINE
        elif tag_name == 's' or tag_name == 'del' or tag_name == 'strike':
            entity_type = TLEntityType.STRIKETHROUGH
        elif tag_name == 'code':
            entity_type = TLEntityType.CODE
        elif tag_name == 'pre':
            entity_type = TLEntityType.PRE
        elif tag_name == 'a':
            entity_type = TLEntityType.TEXT_LINK
            extra = attrs.get('href', '')
        elif tag_name == 'emoji':
            entity_type = TLEntityType.CUSTOM_EMOJI
            extra = attrs.get('id', '')
        elif tag_name == 'blockquote':
            entity_type = TLEntityType.BLOCKQUOTE
        elif tag_name == 'spoiler':
            entity_type = TLEntityType.SPOILER
        
        if entity_type:
            self.entities.append(RawEntity(entity_type, start_pos, length, extra))


class HTML:
    """HTML утилиты для Telegram"""
    
    @staticmethod
    def parse(text: str) -> Tuple[str, List[RawEntity]]:
        """Парсит HTML текст в Telegram сущности"""
        parser = HTMLParser_()
        parser.feed(text)
        return add_surrogates(parser.text), parser.entities
    
    @staticmethod
    def unparse(text: str, entities: List[RawEntity]) -> str:
        """Конвертирует текст с сущностями обратно в HTML"""
        if not entities:
            return text
        
        result = []
        last_offset = 0
        
        for entity in sorted(entities, key=lambda e: e.offset):
            result.append(text[last_offset:entity.offset])
            
            content = text[entity.offset:entity.offset + entity.length]
            
            if entity.type == TLEntityType.BOLD:
                result.append(f"<b>{content}</b>")
            elif entity.type == TLEntityType.ITALIC:
                result.append(f"<i>{content}</i>")
            elif entity.type == TLEntityType.UNDERLINE:
                result.append(f"<u>{content}</u>")
            elif entity.type == TLEntityType.STRIKETHROUGH:
                result.append(f"<s>{content}</s>")
            elif entity.type == TLEntityType.CODE:
                result.append(f"<code>{content}</code>")
            elif entity.type == TLEntityType.PRE:
                result.append(f"<pre>{content}</pre>")
            elif entity.type == TLEntityType.TEXT_LINK:
                result.append(f'<a href="{entity.extra}">{content}</a>')
            elif entity.type == TLEntityType.CUSTOM_EMOJI:
                result.append(f'<emoji id="{entity.extra}">{content}</emoji>')
            elif entity.type == TLEntityType.BLOCKQUOTE:
                result.append(f"<blockquote>{content}</blockquote>")
            elif entity.type == TLEntityType.SPOILER:
                result.append(f"<spoiler>{content}</spoiler>")
            
            last_offset = entity.offset + entity.length
        
        result.append(text[last_offset:])
        return ''.join(result)


class Markdown:
    """Markdown утилиты для Telegram"""
    
    BOLD_DELIM = "*"
    ITALIC_DELIM = "_"
    UNDERLINE_DELIM = "__"
    STRIKE_DELIM = "~"
    SPOILER_DELIM = "||"
    CODE_DELIM = "`"
    PRE_DELIM = "```"
    
    @staticmethod
    def parse(text: str) -> Tuple[str, List[RawEntity]]:
        """Парсит Markdown текст в Telegram сущности"""
        # Упрощенная реализация - можно расширить
        entities = []
        clean_text = text
        
        # Здесь должна быть полная реализация Markdown парсера
        # Для краткости оставляем базовую версию
        
        return add_surrogates(clean_text), entities
    
    @staticmethod
    def unparse(text: str, entities: List[RawEntity]) -> str:
        """Конвертирует текст с сущностями обратно в Markdown"""
        if not entities:
            return text
        
        result = []
        last_offset = 0
        
        for entity in sorted(entities, key=lambda e: e.offset):
            result.append(text[last_offset:entity.offset])
            
            content = text[entity.offset:entity.offset + entity.length]
            
            if entity.type == TLEntityType.BOLD:
                result.append(f"**{content}**")
            elif entity.type == TLEntityType.ITALIC:
                result.append(f"_{content}_")
            elif entity.type == TLEntityType.UNDERLINE:
                result.append(f"__{content}__")
            elif entity.type == TLEntityType.STRIKETHROUGH:
                result.append(f"~~{content}~~")
            elif entity.type == TLEntityType.CODE:
                result.append(f"`{content}`")
            elif entity.type == TLEntityType.PRE:
                result.append(f"```{content}```")
            elif entity.type == TLEntityType.TEXT_LINK:
                result.append(f"[{content}]({entity.extra})")
            elif entity.type == TLEntityType.SPOILER:
                result.append(f"||{content}||")
            
            last_offset = entity.offset + entity.length
        
        result.append(text[last_offset:])
        return ''.join(result)


def link(text: str, url: str) -> str:
    """Создает HTML ссылку"""
    return f'<a href="{url}">{text}</a>'


# ==================== Работа с Java коллекциями ====================
def arraylist_to_list(jarray: Optional[ArrayList]) -> Optional[List[Any]]:
    """Конвертирует Java ArrayList в Python list"""
    return [jarray.get(i) for i in range(jarray.size())] if jarray else None


def list_to_arraylist(python_list: Optional[List[Any]], int_auto_convert: bool = True) -> Optional[ArrayList]:
    """Конвертирует Python list в Java ArrayList"""
    if not python_list:
        return None
    
    arraylist = ArrayList()
    for item in python_list:
        if int_auto_convert and isinstance(item, int):
            arraylist.add(Integer(item))
        else:
            arraylist.add(item)
    return arraylist


# ==================== Система команд ====================
class CannotCastError(Exception):
    """Невозможно преобразовать аргумент"""
    pass


class WrongArgumentAmountError(Exception):
    """Неверное количество аргументов"""
    pass


class MissingRequiredArguments(Exception):
    """Отсутствуют обязательные аргументы"""
    pass


class InvalidTypeError(Exception):
    """Неверный тип"""
    pass


class ArgSpec:
    """Спецификация аргумента команды"""
    def __init__(self, name, annotation, kind, default=None, is_optional=False):
        self.name = name
        self.annotation = annotation
        self.kind = kind
        self.default = default if default is not None else inspect.Parameter.empty
        self.is_optional = is_optional
    
    @classmethod
    def from_parameter(cls, param):
        """Создает ArgSpec из inspect.Parameter"""
        is_optional = False
        annotation = param.annotation
        
        # Упрощенная проверка Optional без typing_extensions
        if hasattr(annotation, '__origin__'):
            if annotation.__origin__ is Union:
                if type(None) in annotation.__args__:
                    is_optional = True
                    non_none_args = [arg for arg in annotation.__args__ if arg is not type(None)]
                    if len(non_none_args) == 1:
                        annotation = non_none_args[0]
        
        return cls(
            name=param.name,
            annotation=annotation if annotation != inspect.Parameter.empty else Any,
            kind=param.kind,
            default=param.default,
            is_optional=is_optional
        )


class Command:
    """Команда плагина"""
    def __init__(self, func, name, args=None, subcommands=None, error_handler=None):
        self.func = func
        self.name = name
        self.args = args if args is not None else []
        self.subcommands = subcommands if subcommands is not None else {}
        self.error_handler = error_handler
    
    def subcommand(self, name: str):
        """Декоратор для регистрации подкоманды"""
        def decorator(func: Callable):
            cmd = create_command(func, name)
            self.subcommands[name] = cmd
            return func
        return decorator
    
    def register_error_handler(self, func: Callable[[Any, int, Exception], HookResult]):
        """Регистрирует обработчик ошибок"""
        self.error_handler = func
        return func


def is_allowed_type(arg_type) -> bool:
    """Проверяет, поддерживается ли тип аргумента"""
    if arg_type in ALLOWED_ARG_TYPES:
        return True
    
    if arg_type is type(None):
        return True
    
    origin = get_origin(arg_type)
    if origin in ALLOWED_ORIGIN:
        return all(is_allowed_type(t) for t in get_args(arg_type))
    return False


def create_command(func: Callable, name: str) -> Command:
    """Создает команду из функции"""
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())
    return_type = signature.return_annotation
    
    if len(parameters) < 2:
        raise MissingRequiredArguments(
            "Command must have 'param' variable as first argument and 'account' variable as second argument"
        )
    
    args = [ArgSpec.from_parameter(param) for param in parameters]
    
    for index, arg in enumerate(args):
        if arg.kind == inspect.Parameter.VAR_POSITIONAL:
            if index != len(args) - 1:
                raise InvalidTypeError(f"VAR_POSITIONAL argument must be the last argument")
            if arg.annotation != str and arg.annotation != Any:
                raise InvalidTypeError(f"VAR_POSITIONAL argument must be str or Any, got {arg.annotation}")
        elif not is_allowed_type(arg.annotation):
            raise InvalidTypeError(f"Unsupported argument type: {arg.annotation}")
    
    if return_type != HookResult:
        return_type_name = "NoneType" if return_type == inspect.Parameter.empty else return_type
        raise InvalidTypeError(f"Command function must return {HookResult} object, got {return_type_name}")
    
    return Command(func=func, name=name, args=args)


def cast_arg(arg: str, target_type: type):
    """Преобразует строку в целевой тип"""
    if target_type == str or target_type == Any:
        return arg
    elif target_type == int:
        return int(arg)
    elif target_type == float:
        return float(arg)
    elif target_type == bool:
        lower = arg.lower()
        if lower in ('true', '1', 'yes', 'on'):
            return True
        elif lower in ('false', '0', 'no', 'off'):
            return False
        raise CannotCastError(f"Cannot cast '{arg}' to bool")
    else:
        raise CannotCastError(f"Unsupported type: {target_type}")


def smart_cast(arg, annotation):
    """Умное преобразование с поддержкой Optional и Union"""
    # Проверка на базовые типы
    if annotation in ALLOWED_ARG_TYPES:
        try:
            return cast_arg(arg, annotation)
        except Exception:
            raise CannotCastError("Cannot cast '{}' to {}".format(arg, annotation))
    
    # Проверка на Union через hasattr
    if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
        for arg_type in annotation.__args__:
            if arg_type is type(None):
                continue
            try:
                return cast_arg(arg, arg_type)
            except Exception:
                continue
        raise CannotCastError("Cannot cast '{}' to any of Union types".format(arg))
    
    raise CannotCastError("Unsupported annotation: {}".format(annotation))


def parse_args(raw_args: List[str], command_args: List[ArgSpec]) -> Tuple[Any, ...]:
    """Парсит аргументы команды"""
    out: List[Any] = []
    required_arg_count = sum(
        1 for arg in command_args
        if not arg.is_optional and arg.default == inspect.Parameter.empty and arg.kind != inspect.Parameter.VAR_POSITIONAL
    )
    is_variadic = any(arg.kind == inspect.Parameter.VAR_POSITIONAL for arg in command_args)
    
    if not is_variadic and len(raw_args) > len(command_args):
        raise WrongArgumentAmountError(f"Too many arguments: expected {len(command_args)}, got {len(raw_args)}")
    if len(raw_args) < required_arg_count:
        raise WrongArgumentAmountError(f"Not enough arguments: expected at least {required_arg_count}, got {len(raw_args)}")
    
    for i, cmd_arg in enumerate(command_args):
        if cmd_arg.kind == inspect.Parameter.VAR_POSITIONAL:
            out.extend(raw_args[i:])
            break
        elif i < len(raw_args):
            out.append(smart_cast(raw_args[i], cmd_arg.annotation))
        elif cmd_arg.default != inspect.Parameter.empty:
            out.append(cmd_arg.default)
        elif cmd_arg.is_optional:
            out.append(None)
        else:
            raise WrongArgumentAmountError(f"Missing required argument: {cmd_arg.name}")
    
    return tuple(out)


class Dispatcher:
    """Диспетчер команд плагина"""
    
    def __init__(self, plugin_id: str, prefix: str = ".", commands_priority: int = -1):
        self.plugin_id = plugin_id
        self.prefix = prefix
        self.commands_priority = commands_priority
        self.listeners: Dict[str, Command] = {}
    
    @staticmethod
    def validate_prefix(prefix: str) -> bool:
        """Проверяет корректность префикса"""
        return len(prefix) == 1 and not prefix.isalnum()
    
    def set_prefix(self, prefix: str):
        """Устанавливает новый префикс"""
        if not self.validate_prefix(prefix):
            logger.error(f"Invalid prefix: {prefix}")
            return
        
        logger.info(f"{self.plugin_id} dp: Set '{prefix}' prefix.")
        self.prefix = prefix
    
    def register_command(self, name: str):
        """Декоратор для регистрации команды"""
        def decorator(func: Callable):
            cmd = create_command(func, name)
            self.listeners[name] = cmd
            logger.info(f"{self.plugin_id} dp: Registered command {name}.")
            return func
        return decorator
    
    def unregister_command(self, name: str):
        """Удаляет команду"""
        logger.info(f"{self.plugin_id} dp: Unregistered command '{name}'.")
        self.listeners.pop(name, None)


# ==================== Локализация ====================
class Locales:
    """Строки локализации"""
    en = {
        "copy_button": "Copy",
        "loaded": "MSLib loaded successfully!",
        "unloaded": "MSLib unloaded.",
        "error": "Error",
        "success": "Success",
        "info": "Info",
        
        # AutoUpdater
        "autoupdater_header": "AutoUpdater",
        "enable_autoupdater": "Enable AutoUpdater",
        "autoupdater_hint": "Automatically check for plugin updates",
        "autoupdate_timeout": "Update check interval (seconds)",
        "autoupdate_timeout_hint": "Time between update checks",
        
        # Интегрированные плагины
        "plugins_header": "Integrated Plugins",
        "hashtags_fix": "HashTags Fix",
        "hashtags_fix_hint": "Open \"This chat\" instead of \"Public Posts\" on hashtag click",
        "article_viewer_fix": "Article Viewer Fix",
        "article_viewer_fix_hint": "Disable swipe-to-close gesture in browser",
        "no_call_confirmation": "No Call Confirmation",
        "no_call_confirmation_hint": "Skip call confirmation dialog",
    }
    ru = {
        "copy_button": "Копировать",
        "loaded": "MSLib успешно загружена!",
        "unloaded": "MSLib выгружена.",
        "error": "Ошибка",
        "success": "Успешно",
        "info": "Информация",
        
        # AutoUpdater
        "autoupdater_header": "Автообновление",
        "enable_autoupdater": "Включить автообновление",
        "autoupdater_hint": "Автоматически проверять обновления плагинов",
        "autoupdate_timeout": "Интервал проверки обновлений (секунды)",
        "autoupdate_timeout_hint": "Время между проверками обновлений",
        
        # Интегрированные плагины
        "plugins_header": "Интегрированные плагины",
        "hashtags_fix": "Исправление хештегов",
        "hashtags_fix_hint": "Открывать \"Этот чат\" вместо \"Публичные посты\" при клике на хештег",
        "article_viewer_fix": "Исправление просмотра статей",
        "article_viewer_fix_hint": "Отключить свайп закрытия (слева направо) в браузере",
        "no_call_confirmation": "Без подтверждения звонка",
        "no_call_confirmation_hint": "Убрать диалог подтверждения при звонке",
    }
    default = en


def localise(key: str) -> str:
    """Получает локализованную строку"""
    try:
        locale = LOCALE if LOCALE else "en"
        locale_dict = getattr(Locales, locale, Locales.default)
        return locale_dict.get(key, key)
    except:
        return key
class CacheFile:
    """Класс для работы с файлами кеша"""
    
    def __init__(self, filename: str, read_on_init: bool = True, compress: bool = False):
        self.filename = filename
        # Отложенная инициализация пути
        self.path = None
        self._content: Optional[bytes] = None
        self.compress = compress
        self.logger = build_log(f"{__name__}.{self.filename}")
        self.read_on_init = read_on_init
    
    def _ensure_path(self):
        """Обеспечивает инициализацию пути"""
        if self.path is None and CACHE_DIRECTORY:
            self.path = os.path.join(CACHE_DIRECTORY, self.filename)
            os.makedirs(CACHE_DIRECTORY, exist_ok=True)
            if self.read_on_init:
                self.read()
    
    def read(self):
        """Читает содержимое файла"""
        self._ensure_path()
        if not self.path or not os.path.exists(self.path):
            if self.path:
                self.logger.warning(f"{self.path} не существует, установлено значение None.")
            self._content = None
            return
        
        try:
            with open(self.path, "rb") as file:
                file_content = file.read()
            
            if self.compress and file_content.startswith(b"\x78\x9c"):
                file_content = zlib.decompress(file_content)
            
            self._content = file_content
        except Exception as e:
            self.logger.error(f"Не удалось загрузить данные из {self.path}: {format_exc_only(e)}")
            self._content = None
    
    def write(self):
        """Записывает содержимое в файл"""
        self._ensure_path()
        if not self.path:
            return
        try:
            save_data = self._content
            if self.compress and save_data:
                save_data = zlib.compress(save_data, level=6)
            
            with open(self.path, "wb") as file:
                file.write(save_data)
        except PermissionError as e:
            self.logger.error(f"Нет прав для редактирования {self.path}: {format_exc_only(e)}")
        except Exception as e:
            self.logger.error(f"Ошибка записи в {self.path}: {format_exc_only(e)}")
    
    def delete(self):
        """Удаляет файл кеша"""
        self._ensure_path()
        if not self.path or not os.path.exists(self.path):
            if self.path:
                self.logger.warning(f"Файл {self.path} не существует.")
            return
        
        try:
            os.remove(self.path)
            self.logger.info(f"Файл {self.path} удален.")
        except Exception as e:
            self.logger.error(f"Не удалось удалить {self.path}: {format_exc_only(e)}")
    
    @property
    def content(self) -> Optional[bytes]:
        return self._content
    
    @content.setter
    def content(self, value: Optional[bytes]):
        self._content = value


class JsonCacheFile(CacheFile):
    """Класс для работы с JSON файлами кеша"""
    
    def __init__(self, filename: str, default: Any, read_on_init: bool = True, compress: bool = False):
        self._default = copy.deepcopy(default)
        self.json_content = self._get_copy_of_default()
        super().__init__(filename, read_on_init, compress)
    
    def _get_copy_of_default(self) -> Any:
        return copy.deepcopy(self._default)
    
    def read(self):
        """Читает и парсит JSON"""
        super().read()
        
        if not self._content:
            self.json_content = self._get_copy_of_default()
            self._content = json.dumps(self.json_content).encode()
            return
        
        try:
            self.json_content = json.loads(self._content.decode("utf-8", errors="replace"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            self.logger.error(f"Не удалось загрузить JSON из {self.path}: {format_exc_only(e)}")
            self.json_content = self._get_copy_of_default()
    
    def write(self):
        """Записывает JSON в файл"""
        self._content = json.dumps(self.json_content, ensure_ascii=False, indent=2).encode("utf-8")
        super().write()
    
    def wipe(self):
        """Очищает содержимое до значения по умолчанию"""
        self.json_content = self._get_copy_of_default()
        self._content = json.dumps(self.json_content).encode()
        self.write()
    
    @property
    def content(self) -> Any:
        if self._content is None:
            return self._get_copy_of_default()
        return self.json_content
    
    @content.setter
    def content(self, value: Any):
        self.json_content = value


# ==================== Callback обертки ====================
class Callback1(dynamic_proxy(Utilities.Callback)):
    """Обертка для Utilities.Callback с одним аргументом"""
    
    def __init__(self, fn: Callable[[Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg):
        try:
            self._fn(arg)
        except Exception as e:
            logger.error(f"Ошибка в Callback1: {format_exc()}")


class Callback2(dynamic_proxy(Utilities.Callback2)):
    """Обертка для Utilities.Callback2 с двумя аргументами"""
    
    def __init__(self, fn: Callable[[Any, Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg1, arg2):
        try:
            self._fn(arg1, arg2)
        except Exception as e:
            logger.error(f"Ошибка в Callback2: {format_exc()}")


class Callback5(dynamic_proxy(Utilities.Callback5)):
    """Обертка для Utilities.Callback5 с пятью аргументами"""
    
    def __init__(self, fn: Callable[[Any, Any, Any, Any, Any], None]):
        super().__init__()
        self._fn = fn
    
    def run(self, arg1, arg2, arg3, arg4, arg5):
        try:
            self._fn(arg1, arg2, arg3, arg4, arg5)
        except Exception as e:
            logger.error(f"Ошибка в Callback5: {format_exc()}")


# ==================== Работа с буфером обмена ====================
def copy_to_clipboard(text: str, show_bulletin: bool = True) -> bool:
    """Копирует текст в буфер обмена"""
    success = AndroidUtilities.addToClipboard(text)
    if success and show_bulletin:
        BulletinHelper.show_copied_to_clipboard()
    return success


# ==================== Bulletin Helper ====================
class InnerBulletinHelper(_BulletinHelper):
    """Расширенный BulletinHelper с префиксом и дополнительными методами"""
    
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = "" if not prefix or not prefix.strip() else f"{prefix}:"
    
    def show_info(self, message: str, fragment: Optional[Any] = None):
        _BulletinHelper.show_info(f"{self.prefix} {message}", fragment)
    
    def show_error(self, message: str, fragment: Optional[Any] = None):
        _BulletinHelper.show_error(f"{self.prefix} {message}", fragment)
    
    def show_success(self, message: str, fragment: Optional[Any] = None):
        _BulletinHelper.show_success(f"{self.prefix} {message}", fragment)
    
    def show_with_copy(self, message: str, text_to_copy: str, icon_res_id: int):
        _BulletinHelper.show_with_button(
            f"{self.prefix} {message}" if not message.startswith(f"{self.prefix} ") else message,
            icon_res_id,
            localise("copy_button"),
            on_click=lambda: copy_to_clipboard(text_to_copy, show_bulletin=False),
        )
    
    def show_info_with_copy(self, message: str, copy_text: str):
        self.show_with_copy(f"{self.prefix} {message}", str(copy_text), R.raw.info)
    
    def show_error_with_copy(self, message: str, copy_text: str):
        self.show_with_copy(f"{self.prefix} {message}", str(copy_text), R.raw.error)
    
    def show_success_with_copy(self, message: str, copy_text: str):
        self.show_with_copy(f"{self.prefix} {message}", str(copy_text), R.raw.contact_check)
    
    def show_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int, icon_res_id: int = 0):
        _BulletinHelper.show_with_button(
            f"{self.prefix} {message}",
            icon_res_id,
            button_text,
            on_click=lambda: get_last_fragment().presentFragment(ChatActivity.of(peer_id, message_id)),
        )
    
    def show_info_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.info)
    
    def show_error_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.error)
    
    def show_success_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.contact_check)


def build_bulletin_helper(prefix: Optional[str] = None) -> InnerBulletinHelper:
    """Создает BulletinHelper с префиксом"""
    return InnerBulletinHelper(prefix)


BulletinHelper = build_bulletin_helper(__name__)


# ==================== AutoUpdater ====================
class UpdaterTask:
    """Задача автообновления"""
    def __init__(self, plugin_id, channel_id, message_id):
        self.plugin_id = plugin_id
        self.channel_id = channel_id
        self.message_id = message_id


class AutoUpdater:
    """Автоматическое обновление плагинов"""
    
    def __init__(self):
        self.thread: Optional[threading.Thread] = None
        self.forced_stop = False
        self.forced_update_check = False
        self.tasks: List[UpdaterTask] = []
        self.msg_edited_ts_cache = JsonCacheFile("mslib_au__msg_edited_ts", {})
        self.hash = str(zlib.adler32(id(self).to_bytes(8, "little")))
        self.logger = build_log(f"{__name__} AU {self.hash}")
    
    def run(self):
        """Запускает поток автообновления"""
        self.forced_stop = False
        
        if self.thread is None:
            self.thread = threading.Thread(target=self.cycle, daemon=True)
        
        if self.thread.is_alive():
            self.logger.warning("Thread is already running.")
            return
        
        self.thread.start()
        self.logger.info("Thread was started.")
    
    def force_stop(self):
        """Принудительно останавливает автообновление"""
        if self.thread is None:
            self.logger.warning("Thread is not running.")
            return
        self.forced_stop = True
    
    def cycle(self):
        """Цикл проверки обновлений"""
        event = threading.Event()
        event.wait(5)
        
        while not self.forced_stop:
            try:
                if self.forced_update_check:
                    self.check_for_updates()
                    self.forced_update_check = False
                else:
                    timeout = self.get_timeout_time()
                    event.wait(timeout)
                    if not self.forced_stop:
                        self.check_for_updates()
            except Exception as e:
                self.logger.error(f"Error in update cycle: {format_exc()}")
                event.wait(60)
        
        self.thread = None
        self.logger.info("Force stopped.")
    
    def check_for_updates(self):
        """Проверяет обновления для всех зарегистрированных задач"""
        self.logger.info("Checking for updates...")
        
        for task in self.tasks:
            try:
                self._check_task_for_update(task)
            except Exception as e:
                self.logger.error(f"Error checking update for {task.plugin_id}: {format_exc()}")
    
    def _check_task_for_update(self, task: UpdaterTask):
        """Проверяет обновление для конкретной задачи"""
        def get_message_callback(msg):
            if not msg:
                self.logger.warning(f"Failed to get message for {task.plugin_id}")
                return
            
            # Проверяем, изменилось ли сообщение
            cache_key = f"{task.channel_id}_{task.message_id}"
            cached_edit_date = self.msg_edited_ts_cache.content.get(cache_key, 0)
            current_edit_date = msg.edit_date if msg.edit_date != 0 else msg.date
            
            if current_edit_date <= cached_edit_date:
                self.logger.info(f"No updates for {task.plugin_id}")
                return
            
            # Обновление доступно
            self.logger.info(f"Update available for {task.plugin_id}: {cached_edit_date} -> {current_edit_date}")
            
            # Скачиваем и устанавливаем
            download_and_install_plugin(msg, task)
            
            # Обновляем кеш
            self.msg_edited_ts_cache.content[cache_key] = current_edit_date
            self.msg_edited_ts_cache.write()
        
        # Получаем сообщение через Requests
        Requests.get_message(
            task.channel_id,
            task.message_id,
            callback=lambda msg, error: get_message_callback(msg) if not error else None
        )
    
    def is_task_already_present(self, task: UpdaterTask) -> bool:
        """Проверяет, есть ли уже такая задача"""
        for t in self.tasks:
            if t.plugin_id == task.plugin_id:
                return True
        return False
    
    def add_task(self, task: UpdaterTask):
        """Добавляет задачу автообновления"""
        if self.is_task_already_present(task):
            self.logger.warning(f"Task {task.plugin_id} already exists.")
            return
        
        self.tasks.append(task)
        self.logger.info(f"Added task {task.plugin_id}.")
    
    def remove_task(self, task: UpdaterTask):
        """Удаляет задачу автообновления"""
        if task not in self.tasks:
            self.logger.warning(f"Task {task.plugin_id} not found.")
            return
        
        self.tasks.remove(task)
        self.logger.info(f"Removed task {task.plugin_id}")
    
    def remove_task_by_id(self, plugin_id: str):
        """Удаляет задачу по ID плагина"""
        filtered_tasks = [t for t in self.tasks if t.plugin_id != plugin_id]
        if len(filtered_tasks) < len(self.tasks):
            self.tasks = filtered_tasks
            self.logger.info(f"Removed task {plugin_id}")
        else:
            self.logger.warning(f"Task {plugin_id} not found.")
    
    def get_timeout_time(self) -> int:
        """Получает таймаут между проверками"""
        try:
            # Можно добавить получение из настроек
            return 600  # 10 минут по умолчанию
        except (ValueError, TypeError):
            return 600
    
    def force_update_check(self):
        """Принудительно запускает проверку обновлений"""
        self.logger.info("Forced update check was requested.")
        self.forced_update_check = True


# ==================== Вспомогательные функции AutoUpdater ====================
def download_and_install_plugin(message, plugin_task: UpdaterTask, max_retries: int = 3):
    """Скачивает и устанавливает плагин из сообщения"""
    if not message or not hasattr(message, 'media'):
        logger.error(f"Invalid message for plugin {plugin_task.plugin_id}")
        return
    
    media = message.media
    if not hasattr(media, 'document'):
        logger.error(f"No document in message for {plugin_task.plugin_id}")
        return
    
    document = media.document
    
    # Получаем имя файла
    filename = None
    for attr in arraylist_to_list(document.attributes):
        if isinstance(attr, TLRPC.TL_documentAttributeFilename):
            filename = attr.file_name
            break
    
    if not filename:
        logger.error(f"No filename in document for {plugin_task.plugin_id}")
        return
    
    logger.info(f"Downloading plugin update: {filename}")
    
    # Путь для сохранения
    if not PLUGINS_DIRECTORY:
        logger.error("PLUGINS_DIRECTORY not initialized")
        return
    
    plugin_path = os.path.join(PLUGINS_DIRECTORY, filename)
    
    # Функция скачивания
    def download_with_retry(retry_count=0):
        def on_download_complete(file_path):
            if file_path and os.path.exists(file_path):
                try:
                    # Копируем в папку плагинов
                    import shutil
                    shutil.copy2(file_path, plugin_path)
                    logger.info(f"Plugin {plugin_task.plugin_id} updated successfully: {plugin_path}")
                    
                    # Показываем уведомление
                    BulletinHelper.show_success(
                        f"Plugin {plugin_task.plugin_id} updated to version from {filename}"
                    )
                except Exception as e:
                    logger.error(f"Failed to install plugin {plugin_task.plugin_id}: {format_exc()}")
                    if retry_count < max_retries:
                        logger.info(f"Retrying download ({retry_count + 1}/{max_retries})...")
                        download_with_retry(retry_count + 1)
            else:
                logger.error(f"Download failed for {plugin_task.plugin_id}")
                if retry_count < max_retries:
                    logger.info(f"Retrying download ({retry_count + 1}/{max_retries})...")
                    download_with_retry(retry_count + 1)
        
        # Используем FileLoader для скачивания
        try:
            from client_utils import get_file_loader
            file_loader = get_file_loader(UserConfig.selectedAccount)
            
            # Загружаем файл
            file_loader.loadFile(
                document,
                None,  # parentObject
                0,     # priority
                0      # cacheType
            )
            
            # Получаем путь к файлу через FileLoader.getPathToAttach
            file_path = file_loader.getPathToAttach(document, False).getAbsolutePath()
            on_download_complete(file_path)
        except Exception as e:
            logger.error(f"Download error for {plugin_task.plugin_id}: {format_exc()}")
            if retry_count < max_retries:
                logger.info(f"Retrying download ({retry_count + 1}/{max_retries})...")
                download_with_retry(retry_count + 1)
    
    download_with_retry()


def get_plugin(plugin_id: str):
    """Получает экземпляр плагина по ID"""
    try:
        from plugin_manager import PluginManager
        return PluginManager.get_instance().get_plugin(plugin_id)
    except Exception as e:
        logger.error(f"Failed to get plugin {plugin_id}: {format_exc()}")
        return None


def add_autoupdater_task(plugin_id: str, channel_id: int, message_id: int):
    """Добавляет задачу автообновления для плагина"""
    global autoupdater
    if not autoupdater:
        logger.warning("AutoUpdater is not initialized")
        return
    
    task = UpdaterTask(plugin_id, channel_id, message_id)
    autoupdater.add_task(task)
    logger.info(f"Added autoupdate task for {plugin_id}: channel={channel_id}, message={message_id}")


def remove_autoupdater_task(plugin_id: str):
    """Удаляет задачу автообновления для плагина"""
    global autoupdater
    if not autoupdater:
        logger.warning("AutoUpdater is not initialized")
        return
    
    autoupdater.remove_task_by_id(plugin_id)
    logger.info(f"Removed autoupdate task for {plugin_id}")


# ==================== Requests утилиты ====================
def request_callback_factory(custom_callback: Optional[Callable]):
    """Фабрика callback'ов для запросов"""
    def default_callback(response, error):
        if custom_callback:
            custom_callback(response, error)
        else:
            if error:
                logger.error(f"Request error: {error}")
    return default_callback


class Requests:
    """Утилиты для работы с Telegram API запросами"""
    
    @staticmethod
    def send(request: TLObject, callback: Optional[Callable] = None, account: int = 0):
        """Отправляет запрос к Telegram API"""
        send_request(request, request_callback_factory(callback), account)
    
    @staticmethod
    def get_user(user_id: int, callback: Callable, account: int = 0):
        """Получает информацию о пользователе"""
        request = TLRPC.TL_users_getUsers()
        input_user = TLRPC.TL_inputUser()
        input_user.user_id = user_id
        request.id = ArrayList()
        request.id.add(input_user)
        
        def user_callback(response, error):
            if error or not response:
                callback(None, error)
            else:
                users = arraylist_to_list(response)
                callback(users[0] if users else None, error)
        
        Requests.send(request, user_callback, account)
    
    @staticmethod
    def get_chat(chat_id: int, callback: Callable, account: int = 0):
        """Получает информацию о чате"""
        request = TLRPC.TL_messages_getChats()
        request.id = ArrayList()
        request.id.add(Long(abs(chat_id)))
        
        def chat_callback(response, error):
            if error or not response:
                callback(None, error)
            else:
                chats = arraylist_to_list(response.chats)
                callback(chats[0] if chats else None, error)
        
        Requests.send(request, chat_callback, account)
    
    @staticmethod
    def get_message(channel_id: int, message_id: int, callback: Callable, account: int = 0):
        """Получает сообщение из канала"""
        request = TLRPC.TL_channels_getMessages()
        
        # Создаем InputChannel
        input_channel = TLRPC.TL_inputChannel()
        input_channel.channel_id = abs(channel_id)
        input_channel.access_hash = 0  # Нужен для приватных каналов
        request.channel = input_channel
        
        # Создаем список ID сообщений
        request.id = ArrayList()
        input_message = TLRPC.TL_inputMessageID()
        input_message.id = message_id
        request.id.add(input_message)
        
        def message_callback(response, error):
            if error or not response:
                callback(None, error)
            else:
                messages = arraylist_to_list(response.messages) if hasattr(response, 'messages') else []
                callback(messages[0] if messages else None, error)
        
        Requests.send(request, message_callback, account)


# ==================== Утилиты для UI ====================
class UI:
    """UI утилиты"""
    
    @staticmethod
    @run_on_ui_thread
    def show_alert(title: str, message: str, positive_button: str = "OK", on_click: Optional[Callable] = None):
        """Показывает диалог с сообщением"""
        builder = AlertDialogBuilder(ApplicationLoader.applicationContext)
        builder.set_title(title)
        builder.set_message(message)
        builder.set_positive_button(positive_button, on_click)
        builder.show()
    
    @staticmethod
    @run_on_ui_thread
    def show_confirm(title: str, message: str, on_confirm: Callable, on_cancel: Optional[Callable] = None):
        """Показывает диалог подтверждения"""
        builder = AlertDialogBuilder(ApplicationLoader.applicationContext)
        builder.set_title(title)
        builder.set_message(message)
        builder.set_positive_button("OK", on_confirm)
        builder.set_negative_button("Cancel", on_cancel)
        builder.show()


# ==================== Интегрированные плагины ====================

# 1. HashTagsFix - открытие "Этот чат" вместо "Публичные посты" в хештегах
class HashTagsFixHook(MethodHook):
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
    
    def replace_hooked_method(self, param):
        try:
            if not self.plugin.get_setting("enable_hashtags_fix", False):
                return
            
            chatActivity = param.thisObject
            hashtag = param.args[0]
            forcePublic = param.args[1]
            
            savedMessagesHint = get_private_field(chatActivity, "savedMessagesHint")
            savedMessagesSearchHint = get_private_field(chatActivity, "savedMessagesSearchHint")
            
            if (len(hashtag) == 0 or (not hashtag.startswith("#") and not hashtag.startswith("$"))):
                return
            
            delay = False
            if (savedMessagesHint is not None and savedMessagesHint.shown()):
                savedMessagesHint.hide()
                delay = True
            
            if (savedMessagesSearchHint is not None and savedMessagesSearchHint.shown()):
                savedMessagesSearchHint.hide()
                delay = True
            
            if (delay):
                def delayed_open():
                    chatActivity.openHashtagSearch(hashtag, False)
                AndroidUtilities.runOnUIThread(delayed_open, 200)
                return
            
            set_private_field(chatActivity, "searchingHashtag", hashtag)
            set_private_field(chatActivity, "searchingQuery", hashtag)
            
            channelHashtags = hashtag.count("@") > 0
            
            method = ChatActivity.getClass().getDeclaredMethod("checkHashtagStories", Boolean.TYPE)
            method.setAccessible(True)
            method.invoke(chatActivity, True)
            
            if (not chatActivity.actionBar.isSearchFieldVisible()):
                avatarContainer = get_private_field(chatActivity, "avatarContainer")
                AndroidUtilities.updateViewVisibilityAnimated(avatarContainer, False, 0.95, True)
                
                headerItem = get_private_field(chatActivity, "headerItem")
                if (headerItem):
                    headerItem.setVisibility(View.GONE)
                
                attachItem = get_private_field(chatActivity, "attachItem")
                if (attachItem):
                    attachItem.setVisibility(View.GONE)
                
                editTextItem = get_private_field(chatActivity, "editTextItem")
                if (editTextItem):
                    editTextItem.setVisibility(View.GONE)
                
                threadMessageId = get_private_field(chatActivity, "threadMessageId")
                chatMode = get_private_field(chatActivity, "chatMode")
                searchItem = get_private_field(chatActivity, "searchItem")
                
                if ((threadMessageId == 0 or chatMode == ChatActivity.MODE_SAVED) and searchItem):
                    searchItem.setVisibility(View.VISIBLE)
                
                searchIconItem = get_private_field(chatActivity, "searchIconItem")
                showSearchAsIcon = get_private_field(chatActivity, "showSearchAsIcon")
                
                if (searchIconItem and showSearchAsIcon):
                    searchIconItem.setVisibility(View.GONE)
                
                audioCallIconItem = get_private_field(chatActivity, "audioCallIconItem")
                showAudioCallAsIcon = get_private_field(chatActivity, "showAudioCallAsIcon")
                
                if (audioCallIconItem and showAudioCallAsIcon):
                    audioCallIconItem.setVisibility(View.GONE)
                
                set_private_field(chatActivity, "searchItemVisible", True)
                
                method = ChatActivity.getClass().getDeclaredMethod("updateSearchButtons", Integer.TYPE, Integer.TYPE, Integer.TYPE)
                method.setAccessible(True)
                method.invoke(chatActivity, Integer(0), Integer(0), Integer(-1))
                
                method = ChatActivity.getClass().getDeclaredMethod("updateBottomOverlay")
                method.setAccessible(True)
                method.invoke(chatActivity)
            
            if (get_private_field(chatActivity, "actionBarSearchTags") and get_private_field(chatActivity, "actionBarSearchTags").shown()):
                get_private_field(chatActivity, "actionBarSearchTags").show(False)
            
            if (get_private_field(chatActivity, "searchUserButton")):
                get_private_field(chatActivity, "searchUserButton").setVisibility(View.GONE)
            
            set_private_field(chatActivity, "defaultSearchPage", Integer(0))
            set_private_field(chatActivity, "openSearchKeyboard", Boolean(False))
            
            if (get_private_field(chatActivity, "searchType") == 3):
                HashtagSearchController.getInstance(UserConfig.selectedAccount).clearSearchResults(3)
            else:
                HashtagSearchController.getInstance(UserConfig.selectedAccount).clearSearchResults()
            
            if (get_private_field(chatActivity, "searchViewPager")):
                get_private_field(chatActivity, "searchViewPager").clearViews()
            
            if (get_private_field(chatActivity, "searchItem")):
                set_private_field(chatActivity, "preventReopenSearchWithText", True)
                get_private_field(chatActivity, "searchItem").openSearch(False)
                set_private_field(chatActivity, "preventReopenSearchWithText", False)
            
            if (get_private_field(chatActivity, "searchItem")):
                get_private_field(chatActivity, "searchItem").setSearchFieldCaption(None)
                get_private_field(chatActivity, "searchItem").setSearchFieldText(hashtag, False)
                get_private_field(chatActivity, "searchItem").setSearchFieldHint(LocaleController.getString(R.string.SearchHashtagsHint))
            
            MediaDataController.getInstance(UserConfig.selectedAccount).searchMessagesInChat(
                get_private_field(chatActivity, "searchingQuery"), 
                get_private_field(chatActivity, "dialog_id"), 
                get_private_field(chatActivity, "mergeDialogId"),
                get_private_field(chatActivity, "classGuid"), 
                0, 
                get_private_field(chatActivity, "threadMessageId"),
                False, 
                get_private_field(chatActivity, "searchingUserMessages"), 
                get_private_field(chatActivity, "searchingChatMessages"),
                False, 
                get_private_field(chatActivity, "searchingReaction")
            )
            
            method = ChatActivity.getClass().getDeclaredMethod("updatePinnedMessageView", Boolean.TYPE)
            method.setAccessible(True)
            method.invoke(chatActivity, True)
            
            get_private_field(chatActivity, "hashtagSearchEmptyView").showProgress(True)
            
            method = ChatActivity.getClass().getDeclaredMethod("showMessagesSearchListView", Boolean.TYPE)
            method.setAccessible(True)
            method.invoke(chatActivity, True)
            
            if (get_private_field(chatActivity, "hashtagSearchTabs")):
                get_private_field(chatActivity, "hashtagSearchTabs").show(not channelHashtags)
                get_private_field(chatActivity, "messagesSearchListContainer").setPadding(0, 0, 0, chatActivity.getHashtagTabsHeight())
                
                method = ChatActivity.getClass().getDeclaredMethod("updateSearchListEmptyView")
                method.setAccessible(True)
                method.invoke(chatActivity)
            
            if ((channelHashtags or forcePublic) and get_private_field(chatActivity, "searchingHashtag") and 
                get_private_field(chatActivity, "hashtagSearchTabs") and 
                get_private_field(chatActivity, "hashtagSearchTabs").tabs.getCurrentPosition() != get_private_field(chatActivity, "defaultSearchPage")):
                get_private_field(chatActivity, "hashtagSearchTabs").tabs.scrollToTab(
                    get_private_field(chatActivity, "defaultSearchPage"), 
                    get_private_field(chatActivity, "defaultSearchPage")
                )
            
            HashtagSearchController.getInstance(UserConfig.selectedAccount).putToHistory(get_private_field(chatActivity, "searchingHashtag"))
            get_private_field(chatActivity, "hashtagHistoryView").update()
            
            view = get_private_field(chatActivity, "searchViewPager").getCurrentView()
            if (isinstance(view, ChatActivityContainer)):
                method = ChatActivity.getClass().getDeclaredMethod("updateSearchingHashtag", String)
                method.invoke(chatActivity, get_private_field(chatActivity, "searchingHashtag"))
        
        except Exception as e:
            logger.error(f"HashTagsFix error: {format_exc()}")


# 2. ArticleViewerFix - отключение свайпа закрытия в браузере
class ArticleViewerFixHook(MethodHook):
    def before_hooked_method(self, param):
        param.setResult(False)


# 3. NoCallConfirmation - убирает подтверждение звонка
class NoCallConfirmationHook(MethodHook):
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
    
    def before_hooked_method(self, param):
        if self.plugin.get_setting("enable_no_call_confirmation", False):
            param.args[6] = True


# ==================== Singleton metaclass ====================
class SingletonMeta(type):
    """Метакласс для создания Singleton"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# Глобальные экземпляры
autoupdater: Optional[AutoUpdater] = None


class MSLib(BasePlugin):
    strings = {
        "en": {
            "__doc__": " MSLib - powerful utility library for exteraGram plugins",
            "settings_header": "MSLib Settings",
            "autoupdater_header": "AutoUpdater",
            "enable_autoupdater": "Enable AutoUpdater",
            "autoupdater_hint": "Automatically check for plugin updates",
            "autoupdate_timeout": "Update check interval (seconds)",
            "autoupdate_timeout_hint": "Time between update checks",
            "debug_mode": "Debug mode",
            "debug_mode_hint": "Enable detailed logging",
            "loaded": "MSLib loaded successfully!",
            "unloaded": "MSLib unloaded.",
            
            # Интегрированные плагины
            "plugins_header": "Integrated Plugins",
            "hashtags_fix": "HashTags Fix",
            "hashtags_fix_hint": "Open \"This chat\" instead of \"Public Posts\" on hashtag click",
            "article_viewer_fix": "Article Viewer Fix",
            "article_viewer_fix_hint": "Disable swipe-to-close gesture in browser",
            "no_call_confirmation": "No Call Confirmation",
            "no_call_confirmation_hint": "Skip call confirmation dialog",
        },
        "ru": {
            "__doc__": "MSLib - мощная библиотека утилит для плагинов exteraGram",
            "settings_header": "Настройки MSLib",
            "autoupdater_header": "Автообновление",
            "enable_autoupdater": "Включить автообновление",
            "autoupdater_hint": "Автоматически проверять обновления плагинов",
            "autoupdate_timeout": "Интервал проверки обновлений (секунды)",
            "autoupdate_timeout_hint": "Время между проверками обновлений",
            "debug_mode": "Режим отладки",
            "debug_mode_hint": "Включить детальное логирование",
            "loaded": "MSLib успешно загружена!",
            "unloaded": "MSLib выгружена.",
            
            # Интегрированные плагины
            "plugins_header": "Интегрированные плагины",
            "hashtags_fix": "Исправление хештегов",
            "hashtags_fix_hint": "Открывать \"Этот чат\" вместо \"Публичные посты\" при клике на хештег",
            "article_viewer_fix": "Исправление просмотра статей",
            "article_viewer_fix_hint": "Отключить свайп закрытия (слева направо) в браузере",
            "no_call_confirmation": "Без подтверждения звонка",
            "no_call_confirmation_hint": "Убрать диалог подтверждения при звонке",
        }
    }
    
    def on_plugin_load(self):
        """Вызывается при загрузке плагина"""
        global autoupdater
        
        # Инициализация констант
        _init_constants()
        
        logger.info(localise("loaded"))
        self.log("MSLib initialized")
        
        # Инициализация автообновления
        if self.get_setting("enable_autoupdater", False):
            autoupdater = AutoUpdater()
            autoupdater.run()
            logger.info("AutoUpdater started")

            MSLIB_UPDATE_CHANNEL_ID = 1001234567890
            MSLIB_UPDATE_MESSAGE_ID = 63
            
            add_autoupdater_task(__id__, MSLIB_UPDATE_CHANNEL_ID, MSLIB_UPDATE_MESSAGE_ID)
            logger.info(f"MSLib self-update enabled: channel={MSLIB_UPDATE_CHANNEL_ID}, message={MSLIB_UPDATE_MESSAGE_ID}")
        
        # Инициализация интегрированных плагинов
        self._setup_integrated_plugins()
    
    def _setup_integrated_plugins(self):
        """Настройка интегрированных плагинов"""
        try:
            # 1. HashTags Fix
            if self.get_setting("enable_hashtags_fix", False):
                try:
                    from java.lang import Class as JavaClass
                    chat_activity_class = ChatActivity.getClass()
                    method = chat_activity_class.getDeclaredMethod(
                        "openHashtagSearch", 
                        String.getClass(), Boolean.TYPE
                    )
                    self.hook_method(method, HashTagsFixHook(self))
                    logger.info("HashTags Fix enabled")
                except Exception as e:
                    logger.error(f"Failed to enable HashTags Fix: {e}")
            
            # 2. Article Viewer Fix
            if self.get_setting("enable_article_viewer_fix", False):
                try:
                    from java import jclass
                    clazz = jclass("org.telegram.ui.ArticleViewer$WindowView")
                    method = clazz.getClass().getDeclaredMethod("handleTouchEvent", MotionEvent)
                    self.hook_method(method, ArticleViewerFixHook())
                    logger.info("Article Viewer Fix enabled")
                except Exception as e:
                    logger.error(f"Failed to enable Article Viewer Fix: {e}")
            
            # 3. No Call Confirmation
            if self.get_setting("enable_no_call_confirmation", False):
                try:
                    voip_class = VoIPHelper.getClass()
                    method = voip_class.getDeclaredMethod(
                        "startCall",
                        TLRPC.User.getClass(),
                        Boolean.TYPE,
                        Boolean.TYPE,
                        Activity.getClass(),
                        TLRPC.UserFull.getClass(),
                        AccountInstance.getClass(),
                        Boolean.TYPE
                    )
                    self.hook_method(method, NoCallConfirmationHook(self))
                    logger.info("No Call Confirmation enabled")
                except Exception as e:
                    logger.error(f"Failed to enable No Call Confirmation: {e}")
        
        except Exception as e:
            logger.error(f"Failed to setup integrated plugins: {e}")
    
    def on_plugin_unload(self):
        """Вызывается при выгрузке плагина"""
        global autoupdater
        
        logger.info(localise("unloaded"))
        self.log("MSLib unloaded")
        
        # Остановка автообновления
        if autoupdater:
            autoupdater.force_stop()
            autoupdater = None
            logger.info("AutoUpdater stopped")
    
    def _on_integrated_plugin_toggle(self, value):
        """Callback при изменении настройки интегрированного плагина"""
        from ui.alert import AlertDialogBuilder
        alert = AlertDialogBuilder(ApplicationLoader.applicationContext)
        if LOCALE == "ru":
            alert.set_title("Требуется перезапуск")
            alert.set_message("Для применения изменений необходимо перезапустить приложение")
            alert.set_positive_button("OK", None)
        else:
            alert.set_title("Restart Required")
            alert.set_message("Please restart the app to apply changes")
            alert.set_positive_button("OK", None)
        alert.show()
    

    def create_settings(self):
        return [
            Header(text=localise("autoupdater_header")),
            Switch(
                key="enable_autoupdater",
                text=localise("enable_autoupdater"),
                subtext=localise("autoupdater_hint"),
                default=False,
                icon="msg_autodownload"
            ),

            Divider(),
            Header(text=localise("plugins_header")),
            Switch(
                key="enable_hashtags_fix",
                text=localise("hashtags_fix"),
                subtext=localise("hashtags_fix_hint"),
                default=False,
                icon="msg_link",
                on_change=self._on_integrated_plugin_toggle
            ),
            Switch(
                key="enable_article_viewer_fix",
                text=localise("article_viewer_fix"),
                subtext=localise("article_viewer_fix_hint"),
                default=False,
                icon="msg_instant",
                on_change=self._on_integrated_plugin_toggle
            ),
            Switch(
                key="enable_no_call_confirmation",
                text=localise("no_call_confirmation"),
                subtext=localise("no_call_confirmation_hint"),
                default=False,
                icon="msg_calls",
                on_change=self._on_integrated_plugin_toggle
            ),
        ]


__all__ = [
    # Основной класс
    'MSLib',
    
    # Классы для работы с кешем
    'CacheFile',
    'JsonCacheFile',
    
    # Callback обертки
    'Callback1',
    'Callback2',
    'Callback5',
    
    # Парсеры
    'HTML',
    'Markdown',
    'TLEntityType',
    'RawEntity',
    
    # Bulletin Helper
    'InnerBulletinHelper',
    'build_bulletin_helper',
    'BulletinHelper',
    
    # Система команд
    'Dispatcher',
    'Command',
    'ArgSpec',
    'create_command',
    'parse_args',
    'cast_arg',
    'smart_cast',
    
    # Исключения
    'CannotCastError',
    'WrongArgumentAmountError',
    'MissingRequiredArguments',
    'InvalidTypeError',
    
    # AutoUpdater
    'AutoUpdater',
    'UpdaterTask',
    'autoupdater',
    'download_and_install_plugin',
    'get_plugin',
    'add_autoupdater_task',
    'remove_autoupdater_task',
    
    # Requests
    'Requests',
    
    # UI утилиты
    'UI',
    
    # Интегрированные плагины (хуки)
    'HashTagsFixHook',
    'ArticleViewerFixHook',
    'NoCallConfirmationHook',
    
    # Утилиты
    'build_log',
    'format_exc',
    'format_exc_from',
    'format_exc_only',
    'copy_to_clipboard',
    'arraylist_to_list',
    'list_to_arraylist',
    'link',
    'add_surrogates',
    'remove_surrogates',
    'localise',
    
    # Singleton
    'SingletonMeta',
    
    # Локализация
    'Locales',
    
    # Константы
    'CACHE_DIRECTORY',
    'PLUGINS_DIRECTORY',
    'LOCALE',
    'NOT_PREMIUM',
    'TELEGRAM_PREMIUM',
    'MSLIB_GLOBAL_PREMIUM',
    'logger',
]
