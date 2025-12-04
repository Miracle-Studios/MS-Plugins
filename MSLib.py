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
||                    https://t.me/MSTeamGlobal                     ||
||                                                                  ||
||                                                                  ||
||        PLEASE DO NOT COPY THIS CODE WITHOUT NOTIFYING ME.        ||
>>==================================================================<<
"""
import copy
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
from typing import List, Callable, Optional, Any, Union, Dict, Tuple, get_origin, get_args

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
from android.app import Activity
from hook_utils import get_private_field, set_private_field

from org.telegram.ui import ChatActivityContainer, ArticleViewer
from org.telegram.messenger import HashtagSearchController, MediaDataController

__id__ = "miracles_library"
__name__ = "MSLib"
__description__ = "MSLib v2.3.5 - Complete update notifications: shows 'no updates', 'up to date', 'update found' messages with localization | Commands, CommandManager, Companion, JsonDB, Extended API"
__icon__ = "ByMiraclePersona/3"
__author__ = "@Imrcle"
__version__ = "2.3.6"
__min_version__ = "12.0.0"


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

# Настройки по умолчанию
DEFAULT_AUTOUPDATE_TIMEOUT = "600"  # 10 минут
DEFAULT_DISABLE_TIMESTAMP_CHECK = False
DEFAULT_DEBUG_MODE = False
DEFAULT_SPINNER_TEXT = "Loading..."


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


# ==================== Глобальные переменные ====================
logger = build_log(__name__)
command_manager = None  # CommandManager - будет инициализирован при загрузке плагина
companion = None  # Companion - будет инициализирован при загрузке плагина
autoupdater = None  # AutoUpdater - будет инициализирован при загрузке плагина


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


# ==================== Helpers ====================
def _bulletin(level: str, message: str):
    """Helper для показа уведомлений через InnerBulletinHelper"""
    helper = InnerBulletinHelper("MSLib")
    getattr(helper, f"show_{level}")(message)


# ==================== Pluralization ====================
def pluralization_string(number: int, words: List[str]) -> str:
    """
    Возвращает правильную форму слова в зависимости от числа.
    
    Args:
        number (int): Число
        words (List[str]): Список из 3 форм слова [1, 2-4, 5+]
    
    Returns:
        str: Форматированная строка с числом и правильным словом
    
    Examples:
        pluralization_string(1, ["file", "files", "files"]) -> "1 file"
        pluralization_string(3, ["file", "files", "files"]) -> "3 files"
        pluralization_string(1, ["плагин", "плагина", "плагинов"]) -> "1 плагин"
        pluralization_string(3, ["плагин", "плагина", "плагинов"]) -> "3 плагина"
        pluralization_string(5, ["плагин", "плагина", "плагинов"]) -> "5 плагинов"
    """
    if number % 10 == 1 and number % 100 != 11:
        return f"{number} {words[0]}"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return f"{number} {words[1]}"
    else:
        return f"{number} {words[2]}"


# ==================== Runtime Execution ====================
def runtime_exec(cmd: List[str], return_list_lines: bool = False, raise_errors: bool = True) -> Union[List[str], str]:
    """
    Выполняет shell команду через Java Runtime.
    
    Args:
        cmd (List[str]): Команда и аргументы
        return_list_lines (bool): Вернуть список строк или объединенную строку
        raise_errors (bool): Выбрасывать исключения при ошибках
    
    Returns:
        Union[List[str], str]: Вывод команды
    """
    from java.lang import Runtime
    from java.io import BufferedReader, InputStreamReader, IOException
    
    result = []
    process = None
    reader = None
    try:
        process = Runtime.getRuntime().exec(list_to_arraylist(cmd, int_auto_convert=False))
        reader = BufferedReader(InputStreamReader(process.getInputStream()))
        line = reader.readLine()
        while line is not None:
            result.append(str(line))
            line = reader.readLine()
        process.waitFor()
    except IOException as e:
        if raise_errors:
            raise RuntimeError(f"IO Error: {e}")
        logger.error(f"runtime_exec IO error: {format_exc()}")
    except Exception as e:
        if raise_errors:
            raise RuntimeError(f"Execution error: {e}")
        logger.error(f"runtime_exec error: {format_exc()}")
    finally:
        if reader:
            try:
                reader.close()
            except:
                pass
        if process:
            try:
                process.destroy()
            except:
                pass
    
    return result if return_list_lines else "\n".join(result)


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
        return prefix and " " not in prefix
    
    def set_prefix(self, prefix: str):
        """Устанавливает новый префикс"""
        if not self.validate_prefix(prefix):
            logger.error(f"Invalid prefix: {prefix}")
            return
        
        logger.info(f"{self.plugin_id} dp: Set '{prefix}' prefix.")
        self.prefix = prefix
        # Обновляем кеш префиксов если CommandManager доступен
        if 'command_manager' in globals() and command_manager:
            command_manager.update_dispatcher_prefix_cache(self.plugin_id)
    
    def register_command(self, name: str):
        """Декоратор для регистрации команды"""
        def decorator(func: Callable):
            cmd = create_command(func, name)
            self.listeners[name] = cmd
            logger.info(f"{self.plugin_id} dp: Registered command {name}.")
            return cmd
        return decorator
    
    def unregister_command(self, name: str):
        """Удаляет команду"""
        logger.info(f"{self.plugin_id} dp: Unregistered command '{name}'.")
        self.listeners.pop(name, None)


class CommandManager:
    """Менеджер команд с поддержкой приоритетов и кеширования префиксов"""
    
    def __init__(self):
        self.dispatchers: Dict[str, Dispatcher] = {}  # plugin_id -> Dispatcher
        self.temporal = True
        self.prefixes_cache = None  # JsonCacheFile будет создан при инициализации
        self.pending_commands: Dict[str, List[Command]] = {}
    
    def initialize_cache(self):
        """Инициализирует кеш префиксов"""
        if self.prefixes_cache is None and CACHE_DIRECTORY:
            self.prefixes_cache = JsonCacheFile("mslib__cmd_prefixes.json", {})
    
    def get_dispatcher(self, plugin_id: str, prefix: str = ".", commands_priority: int = -1) -> Dispatcher:
        """Получает или создает диспетчер для плагина"""
        self.initialize_cache()
        
        # Проверяем кеш префиксов
        if self.prefixes_cache and plugin_id in self.prefixes_cache.content:
            prefix = self.prefixes_cache.content[plugin_id]
        
        if plugin_id not in self.dispatchers:
            self.dispatchers[plugin_id] = Dispatcher(
                plugin_id=plugin_id,
                prefix=prefix,
                commands_priority=commands_priority,
            )
        
        logger.info(f"Got dispatcher for '{plugin_id}' with prefix '{prefix}'.")
        return self.dispatchers[plugin_id]
    
    def remove_dispatcher(self, plugin_id: str):
        """Удаляет диспетчер"""
        self.dispatchers.pop(plugin_id, None)
        logger.info(f"Removed dispatcher for '{plugin_id}'.")
    
    def sort_dispatchers(self):
        """Сортирует диспетчеры по приоритету (большой приоритет = первым обрабатывается)"""
        self.dispatchers = dict(sorted(
            self.dispatchers.items(),
            key=lambda i: i[1].commands_priority,
            reverse=True
        ))
        logger.debug("Dispatchers sorted by commands priority.")
    
    def mark_not_temporal(self):
        """Помечает менеджер как инициализированный"""
        self.temporal = False
    
    def load_pending_commands(self):
        """Загружает отложенные команды"""
        logger.info(f"Loading pending commands: {list(self.pending_commands.keys())}")
        
        for plugin_id, commands in list(self.pending_commands.items()):
            if not commands:
                continue
            
            logger.info(f"Loading pending commands for '{plugin_id}'...")
            dispatcher = self.get_dispatcher(plugin_id)
            
            for command in commands:
                logger.info(f"Registered pending command '{command.name}' for '{plugin_id}'.")
                dispatcher.listeners[command.name] = command
        
        self.pending_commands.clear()
    
    def save_commands_as_pending(self):
        """Сохраняет все команды как отложенные"""
        logger.info("Saving all commands to pending list...")
        
        for plugin_id, dp in self.dispatchers.items():
            self.pending_commands[plugin_id] = list(dp.listeners.values())
    
    def unregister_all(self):
        """Удаляет все диспетчеры"""
        logger.info("Unregistering all dispatchers...")
        self.dispatchers.clear()
    
    def update_dispatcher_prefix_cache(self, plugin_id: str):
        """Обновляет кеш префиксов для диспетчера"""
        if not self.prefixes_cache:
            self.initialize_cache()
        
        if plugin_id not in self.dispatchers:
            logger.warning(f"Cannot update prefix cache for unknown plugin '{plugin_id}'")
            return
        
        dp = self.dispatchers[plugin_id]
        logger.info(f"Updating prefix cache for '{plugin_id}': '{dp.prefix}'")
        
        if dp.prefix == ".":  # Дефолтный префикс
            self.prefixes_cache.content.pop(plugin_id, None)
        else:
            self.prefixes_cache.content[plugin_id] = dp.prefix
        
        self.prefixes_cache.write()


# ==================== Singleton metaclass ====================
class SingletonMeta(type):
    """Метакласс для создания Singleton"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Companion(metaclass=SingletonMeta):
    """Компаньон для хранения данных между перезагрузками плагина"""
    
    defaults = {
        "autoupdates_tasks": [],
        "pending_commands": {},
    }
    
    def __init__(self):
        self.module = None
        self.companion_path = None
    
    def initialize(self):
        """Инициализирует пути и создает файл компаньона"""
        if PLUGINS_DIRECTORY:
            companion_dir = os.path.join(PLUGINS_DIRECTORY, "mslib_companion")
            self.companion_path = os.path.join(companion_dir, "__init__.py")
            self.create()
            self.import_it()
    
    def create(self):
        """Создает файл компаньона если его нет"""
        if not self.companion_path or os.path.exists(self.companion_path):
            return
        
        lines = ["# Auto-generated MSLib companion file\n"]
        for key, default in Companion.defaults.items():
            lines.append(f"\n{key} = {repr(default)}")
        
        os.makedirs(os.path.dirname(self.companion_path), exist_ok=True)
        with open(self.companion_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        logger.info(f"Created companion file at {self.companion_path}")
    
    def import_it(self):
        """Импортирует модуль компаньона"""
        if not self.companion_path:
            return
        
        try:
            # Добавляем путь к модулю в sys.path если его там нет
            companion_parent = os.path.dirname(self.companion_path)
            if companion_parent not in sys.path:
                sys.path.insert(0, os.path.dirname(companion_parent))
            
            import mslib_companion
            self.module = mslib_companion
            logger.info("Imported companion module")
        except ImportError as e:
            logger.error(f"Failed to import companion: {format_exc_only(e)}")
            self.module = None


# ==================== Декораторы ====================
def command(cmd: Optional[str] = None, *, aliases: Optional[List[str]] = None, doc: Optional[str] = None, enabled: Optional[Union[str, bool]] = None):
    """
    Декоратор для регистрации команд
    
    Args:
        cmd: Название команды
        aliases: Список алиасов
        doc: Ключ локализации для описания
        enabled: Ключ настройки или bool для включения команды
    """
    def decorator(func):
        func.__is_command__ = True
        func.__aliases__ = aliases or []
        func.__cdoc__ = doc
        func.__enabled__ = enabled
        func.__cmd__ = cmd or func.__name__
        return func
    return decorator


def uri(uri_path: str):
    """Декоратор для URI обработчиков"""
    def decorator(func):
        func.__is_uri_handler__ = True
        func.__uri__ = uri_path
        return func
    return decorator


def message_uri(uri_path: str, support_long_click: bool = False):
    """Декоратор для URI в сообщениях"""
    def decorator(func):
        func.__is_uri_message_handler__ = True
        func.__uri__ = uri_path
        func.__support_long__ = support_long_click
        return func
    return decorator


def watcher():
    """Декоратор для наблюдателей за сообщениями"""
    def decorator(func):
        func.__is_watcher__ = True
        return func
    return decorator


# ==================== JsonDB - база данных на JSON ====================
class JsonDB(dict):
    """База данных на основе JSON файла"""
    
    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        self._load()
    
    def _load(self):
        """Загружает данные из файла"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.update(data)
            except Exception as e:
                logger.error(f"Failed to load JsonDB from {self.filepath}: {format_exc_only(e)}")
    
    def save(self):
        """Сохраняет данные в файл"""
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(dict(self), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JsonDB to {self.filepath}: {format_exc_only(e)}")
    
    def set(self, key: str, value: Any):
        """Устанавливает значение и сохраняет"""
        self[key] = value
        self.save()
    
    def reset(self):
        """Очищает базу данных"""
        self.clear()
        self.save()


# ==================== Inline кнопки ====================
class Inline:
    """Система inline кнопок для сообщений"""
    
    callbacks: Dict[str, Callable] = {}
    
    class Markup:
        """Построитель inline разметки"""
        
        def __init__(self):
            self.rows = []
        
        def add_row(self, *buttons):
            """Добавляет ряд кнопок"""
            if buttons and buttons[0] is not None:
                self.rows.append(list(buttons))
            return self
        
        def to_tlrpc(self) -> TLRPC.TL_replyInlineMarkup:
            """Конвертирует в TLRPC объект"""
            markup = TLRPC.TL_replyInlineMarkup()
            markup.rows = ArrayList()
            
            for row in self.rows:
                tlrpc_row = TLRPC.TL_keyboardButtonRow()
                tlrpc_row.buttons = ArrayList()
                
                for btn in row:
                    if isinstance(btn, dict):
                        button = TLRPC.TL_keyboardButtonUrl()
                        button.text = btn.get('text', '')
                        button.url = btn.get('url', '')
                        tlrpc_row.buttons.add(button)
                
                markup.rows.add(tlrpc_row)
            
            return markup
    
    @staticmethod
    def button(text: str, *, url: Optional[str] = None, callback_data: Optional[str] = None, **kwargs):
        """Создаёт inline кнопку"""
        if url:
            return {'text': text, 'url': url, 'type': 'url'}
        elif callback_data:
            return {'text': text, 'callback_data': callback_data, 'type': 'callback'}
        return {'text': text}
    
    @classmethod
    def on_click(cls, method: str, support_long_click: bool = False):
        """Декоратор для обработчиков нажатий кнопок"""
        def decorator(func):
            cls.callbacks[method] = func
            func.__is_inline_handler__ = True
            func.__method__ = method
            func.__support_long__ = support_long_click
            return func
        return decorator


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
        "autoupdater_header": "AutoUpdater",
        "enable_autoupdater": "Enable AutoUpdater",
        "autoupdater_hint": "Automatically check for plugin updates",
        "force_update_check": "Force update check",
        "autoupdate_timeout": "Update check interval (seconds)",
        "autoupdate_timeout_title": "Update check interval",
        "autoupdate_timeout_hint": "Time between update checks",
        "disable_timestamp_check_title": "Disable message edit check",
        "disable_timestamp_check_hint": "Plugin will be updated even if the file has not been modified",
        "plugins_header": "Integrated Plugins",
        "hashtags_fix": "HashTags Fix",
        "hashtags_fix_hint": "Open \"This chat\" instead of \"Public Posts\" on hashtag click",
        "article_viewer_fix": "Article Viewer Fix",
        "article_viewer_fix_hint": "Disable swipe-to-close gesture in browser",
        "no_call_confirmation": "No Call Confirmation",
        "no_call_confirmation_hint": "Skip call confirmation dialog",
        "old_bottom_forward": "Old Bottom Forward",
        "old_bottom_forward_hint": "Brings back old forward dialog for the bottom button",
        "dev_header": "Developer",
        "debug_mode_title": "Debug mode",
        "debug_mode_hint": "Enables detailed logging for troubleshooting",
        "commands_header": "Commands",
        "command_prefix_label": "Command prefix",
        "command_prefix_hint": "Prefix for plugin commands",
        "update_check_started": "Update check started!",
        "autoupdater_not_initialized": "AutoUpdater is not initialized",
        "update_check_failed": "Update check failed for {}",
        "already_up_to_date": "{}: Already up to date",
        "update_found": "Update found for {}",
        "forcing_update": "Forcing update for {}",
        "no_updates_found": "No updates found",
        "all_plugins_up_to_date": "All plugins are up to date!",
        "hashtags_fix_enabled": "HashTags Fix enabled",
        "hashtags_fix_disabled": "HashTags Fix disabled",
        "article_viewer_fix_enabled": "Article Viewer Fix enabled",
        "article_viewer_fix_disabled": "Article Viewer Fix disabled",
        "no_call_confirmation_enabled": "No Call Confirmation enabled",
        "no_call_confirmation_disabled": "No Call Confirmation disabled",
        "old_bottom_forward_enabled": "Old Bottom Forward enabled",
        "old_bottom_forward_disabled": "Old Bottom Forward disabled",
    }
    ru = {
        "copy_button": "Копировать",
        "loaded": "MSLib успешно загружена!",
        "unloaded": "MSLib выгружена.",
        "error": "Ошибка",
        "success": "Успешно",
        "info": "Информация",
        "autoupdater_header": "Автообновление",
        "enable_autoupdater": "Включить автообновление",
        "autoupdater_hint": "Автоматически проверять обновления плагинов",
        "force_update_check": "Принудительная проверка",
        "autoupdate_timeout": "Интервал проверки обновлений (секунды)",
        "autoupdate_timeout_title": "Интервал проверки обновлений",
        "autoupdate_timeout_hint": "Время между проверками обновлений",
        "disable_timestamp_check_title": "Отключить проверку редактирования",
        "disable_timestamp_check_hint": "Плагин будет обновлен, даже если файл не был изменен",
        "plugins_header": "Интегрированные плагины",
        "hashtags_fix": "Исправление хештегов",
        "hashtags_fix_hint": "Открывать \"Этот чат\" вместо \"Публичные посты\" при клике на хештег",
        "article_viewer_fix": "Исправление просмотра статей",
        "article_viewer_fix_hint": "Отключить свайп закрытия (слева направо) в браузере",
        "no_call_confirmation": "Без подтверждения звонка",
        "no_call_confirmation_hint": "Убрать диалог подтверждения при звонке",
        "old_bottom_forward": "Старая пересылка",
        "old_bottom_forward_hint": "Возвращает привычное открытие диалогов при нажатии на нижнюю кнопку \"Переслать\"",
        "dev_header": "Разработчик",
        "debug_mode_title": "Режим отладки",
        "debug_mode_hint": "Включает подробное логирование для диагностики",
        "commands_header": "Команды",
        "command_prefix_label": "Префикс команд",
        "command_prefix_hint": "Префикс для команд плагинов",
        "update_check_started": "Проверка обновлений запущена!",
        "autoupdater_not_initialized": "AutoUpdater не инициализирован",
        "update_check_failed": "Не удалось проверить обновления для {}",
        "already_up_to_date": "{}: Уже актуальная версия",
        "update_found": "Найдено обновление для {}",
        "forcing_update": "Принудительное обновление для {}",
        "no_updates_found": "Обновления не найдены",
        "all_plugins_up_to_date": "Все плагины актуальны!",
        "hashtags_fix_enabled": "HashTags Fix включён",
        "hashtags_fix_disabled": "HashTags Fix выключен",
        "article_viewer_fix_enabled": "Article Viewer Fix включён",
        "article_viewer_fix_disabled": "Article Viewer Fix выключен",
        "no_call_confirmation_enabled": "No Call Confirmation включён",
        "no_call_confirmation_disabled": "No Call Confirmation выключен",
        "old_bottom_forward_enabled": "Old Bottom Forward включён",
        "old_bottom_forward_disabled": "Old Bottom Forward выключен",
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


def get_command_prefix() -> str:
    """Получает текущий префикс команд из настроек MSLib"""
    global MSLib_instance
    if MSLib_instance is not None:
        return MSLib_instance.get_setting("command_prefix", ".")
    return "."


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
        self.update_event = threading.Event()  # Для пробуждения потока
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
        # Начальная задержка
        self.update_event.wait(5)
        
        while not self.forced_stop:
            try:
                # Проверяем флаг принудительного обновления
                if self.forced_update_check:
                    self.logger.info("Processing forced update check")
                    self.check_for_updates(show_notifications=True)
                    self.forced_update_check = False
                    self.update_event.clear()  # Сбрасываем событие
                    continue  # Сразу переходим к следующей итерации
                
                # Обычная проверка по таймауту
                timeout = self.get_timeout_time()
                self.logger.debug(f"Waiting {timeout}s for next update check")
                
                # Ждём таймаут или пробуждение через update_event
                self.update_event.wait(timeout)
                
                if not self.forced_stop and not self.forced_update_check:
                    self.check_for_updates(show_notifications=False)
                
                self.update_event.clear()  # Сбрасываем событие после обработки
                
            except Exception as e:
                self.logger.error(f"Error in update cycle: {format_exc()}")
                self.update_event.wait(60)
        
        self.thread = None
        self.logger.info("Force stopped.")
    
    def check_for_updates(self, show_notifications: bool = False):
        """Проверяет обновления для всех зарегистрированных задач"""
        self.logger.info("Checking for updates...")
        
        if not self.tasks:
            self.logger.info("No tasks to check")
            if show_notifications:
                _bulletin("info", localise("no_updates_found"))
            return
        
        for task in self.tasks:
            try:
                self._check_task_for_update(task, show_notifications)
            except Exception as e:
                self.logger.error(f"Error checking update for {task.plugin_id}: {format_exc()}")
                if show_notifications:
                    _bulletin("error", localise("update_check_failed").format(task.plugin_id))
    
    def _check_task_for_update(self, task: UpdaterTask, show_notifications: bool = False):
        """Проверяет обновление для конкретной задачи"""
        def get_message_callback(msg, error):
            if error or not msg:
                self.logger.warning(f"Failed to get message for {task.plugin_id}: {error}")
                if show_notifications:
                    _bulletin("error", localise("update_check_failed").format(task.plugin_id))
                return
            
            # Проверяем настройку disable_timestamp_check
            disable_ts_check = MSLib_instance.get_setting("disable_timestamp_check", DEFAULT_DISABLE_TIMESTAMP_CHECK) if MSLib_instance else DEFAULT_DISABLE_TIMESTAMP_CHECK
            
            if not disable_ts_check:
                # Проверяем, изменилось ли сообщение
                cache_key = f"{task.channel_id}_{task.message_id}"
                cached_edit_date = self.msg_edited_ts_cache.content.get(cache_key, 0)
                current_edit_date = msg.edit_date if msg.edit_date != 0 else msg.date
                
                if current_edit_date <= cached_edit_date:
                    self.logger.info(f"No updates for {task.plugin_id}")
                    if show_notifications:
                        _bulletin("info", localise("already_up_to_date").format(task.plugin_id))
                    return
                
                # Обновление доступно
                self.logger.info(f"Update available for {task.plugin_id}: {cached_edit_date} -> {current_edit_date}")
                if show_notifications:
                    _bulletin("success", localise("update_found").format(task.plugin_id))
                
                # Обновляем кеш
                self.msg_edited_ts_cache.content[cache_key] = current_edit_date
                self.msg_edited_ts_cache.write()
            else:
                self.logger.info(f"Timestamp check disabled, forcing update for {task.plugin_id}")
                if show_notifications:
                    _bulletin("info", localise("forcing_update").format(task.plugin_id))
            
            # Скачиваем и устанавливаем
            download_and_install_plugin(msg, task, show_notifications)
        
        # Получаем сообщение через Requests
        Requests.get_message(
            task.channel_id,
            task.message_id,
            callback=get_message_callback
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
        """Получает таймаут между проверками из настроек"""
        try:
            # Пытаемся получить из настроек MSLib
            timeout_str = MSLib_instance.get_setting("autoupdate_timeout", DEFAULT_AUTOUPDATE_TIMEOUT) if MSLib_instance else DEFAULT_AUTOUPDATE_TIMEOUT
            return int(timeout_str)
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to get timeout: {format_exc_only(e)}")
            return int(DEFAULT_AUTOUPDATE_TIMEOUT)
    
    def force_update_check(self):
        """Принудительно запускает проверку обновлений"""
        self.logger.info("Forced update check was requested.")
        self.forced_update_check = True
        self.update_event.set()  # Пробуждаем поток немедленно


# ==================== Вспомогательные функции AutoUpdater ====================
def download_and_install_plugin(message, plugin_task: UpdaterTask, max_retries: int = 3, show_notifications: bool = False):
    """Скачивает и устанавливает плагин из сообщения"""
    if not message or not hasattr(message, 'media'):
        logger.error(f"Invalid message for plugin {plugin_task.plugin_id}")
        if show_notifications:
            _bulletin("error", f"Invalid message for {plugin_task.plugin_id}")
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
    
    @staticmethod
    def search_messages(
        peer_id: int,
        query: str,
        callback: Callable,
        limit: int = 100,
        offset_id: int = 0,
        filter_type: Optional[Any] = None,
        account: int = 0
    ):
        """Ищет сообщения в чате"""
        request = TLRPC.TL_messages_search()
        request.peer = Requests._get_input_peer(peer_id)
        request.q = query
        request.filter = filter_type or TLRPC.TL_inputMessagesFilterEmpty()
        request.limit = limit
        request.offset_id = offset_id
        request.min_date = 0
        request.max_date = 0
        request.add_offset = 0
        request.max_id = 0
        request.min_id = 0
        request.hash = 0
        
        def search_callback(response, error):
            if error or not response:
                callback([], error)
            else:
                messages = arraylist_to_list(response.messages) if hasattr(response, 'messages') else []
                callback(messages, error)
        
        Requests.send(request, search_callback, account)
    
    @staticmethod
    def _get_input_peer(peer_id: int):
        """Создаёт InputPeer из peer_id"""
        if peer_id > 0:
            # User
            input_peer = TLRPC.TL_inputPeerUser()
            input_peer.user_id = peer_id
            input_peer.access_hash = 0
        elif peer_id < -1000000000000:
            # Channel
            input_peer = TLRPC.TL_inputPeerChannel()
            input_peer.channel_id = abs(peer_id + 1000000000000)
            input_peer.access_hash = 0
        else:
            # Chat
            input_peer = TLRPC.TL_inputPeerChat()
            input_peer.chat_id = abs(peer_id)
        
        return input_peer
    
    @staticmethod
    def delete_messages(message_ids: List[int], peer_id: int, callback: Optional[Callable] = None, revoke: bool = True, account: int = 0):
        """Удаляет сообщения"""
        if peer_id < -1000000000000:
            # Channel
            request = TLRPC.TL_channels_deleteMessages()
            request.channel = Requests._get_input_peer(peer_id)
            request.id = list_to_arraylist(message_ids)
        else:
            # Chat or User
            request = TLRPC.TL_messages_deleteMessages()
            request.id = list_to_arraylist(message_ids)
            request.revoke = revoke
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def ban(chat_id: int, peer_id: int, until_date: Optional[int] = None, callback: Optional[Callable] = None, account: int = 0):
        """Банит пользователя в чате/канале"""
        msg_controller = get_messages_controller()
        
        # Создаём права бана со всеми ограничениями
        banned_rights = TLRPC.TL_chatBannedRights()
        banned_rights.view_messages = True
        banned_rights.send_messages = True
        banned_rights.send_media = True
        banned_rights.send_stickers = True
        banned_rights.send_gifs = True
        banned_rights.send_games = True
        banned_rights.send_inline = True
        banned_rights.embed_links = True
        banned_rights.send_polls = True
        banned_rights.change_info = True
        banned_rights.invite_users = True
        banned_rights.pin_messages = True
        banned_rights.until_date = until_date or 0
        
        request = TLRPC.TL_channels_editBanned()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.participant = msg_controller.getInputPeer(peer_id)
        request.banned_rights = banned_rights
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def unban(chat_id: int, target_peer_id: int, callback: Optional[Callable] = None, account: int = 0):
        """Разбанивает пользователя"""
        msg_controller = get_messages_controller()
        
        # Пустые права = разбан
        banned_rights = TLRPC.TL_chatBannedRights()
        banned_rights.until_date = 0
        
        request = TLRPC.TL_channels_editBanned()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.participant = msg_controller.getInputPeer(target_peer_id)
        request.banned_rights = banned_rights
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def change_slowmode(chat_id: int, seconds: int = 0, callback: Optional[Callable] = None, account: int = 0):
        """Изменяет slowmode в канале"""
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_channels_toggleSlowMode()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.seconds = seconds
        
        Requests.send(request, callback, account)
    
    @staticmethod
    def reload_admins(chat_id: int, account: int = 0):
        """Перезагружает список администраторов канала"""
        get_messages_controller().loadChannelAdmins(chat_id, False)
    
    @staticmethod
    def get_chat_participant(chat_id: int, target_peer_id: int, callback: Callable, account: int = 0):
        """Получает информацию об участнике чата"""
        msg_controller = get_messages_controller()
        
        request = TLRPC.TL_channels_getParticipant()
        request.channel = msg_controller.getInputChannel(chat_id)
        request.participant = msg_controller.getInputPeer(target_peer_id)
        
        Requests.send(request, callback, account)


# ==================== Утилиты для UI ====================

def copy_to_clipboard(text_to_copy: str) -> bool:
    """Копирует текст в буфер обмена"""
    return AndroidUtilities.addToClipboard(text_to_copy)


class InnerBulletinHelper(_BulletinHelper):
    """Расширенный BulletinHelper с префиксами и дополнительными методами"""
    
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = "" if not prefix or not prefix.strip() else f"{prefix}:"
    
    def show_info(self, message: str, fragment: Optional[Any] = None):
        """Показывает информационное сообщение с префиксом"""
        _BulletinHelper.show_info(f"{self.prefix} {message}" if self.prefix else message, fragment)
    
    def show_error(self, message: str, fragment: Optional[Any] = None):
        """Показывает сообщение об ошибке с префиксом"""
        _BulletinHelper.show_error(f"{self.prefix} {message}" if self.prefix else message, fragment)
    
    def show_success(self, message: str, fragment: Optional[Any] = None):
        """Показывает сообщение об успехе с префиксом"""
        _BulletinHelper.show_success(f"{self.prefix} {message}" if self.prefix else message, fragment)
    
    def show_with_copy(self, message: str, text_to_copy: str, icon_res_id: int):
        """Показывает сообщение с кнопкой копирования"""
        _BulletinHelper.show_with_button(
            f"{self.prefix} {message}" if self.prefix and not message.startswith(f"{self.prefix} ") else message,
            icon_res_id,
            "Copy",
            on_click=lambda: copy_to_clipboard(text_to_copy) and _BulletinHelper.show_copied_to_clipboard(),
        )
    
    def show_info_with_copy(self, message: str, copy_text: str):
        """Показывает информацию с кнопкой копирования"""
        self.show_with_copy(message, str(copy_text), R.raw.info)
    
    def show_error_with_copy(self, message: str, copy_text: str):
        """Показывает ошибку с кнопкой копирования"""
        self.show_with_copy(message, str(copy_text), R.raw.error)
    
    def show_success_with_copy(self, message: str, copy_text: str):
        """Показывает успех с кнопкой копирования"""
        self.show_with_copy(message, str(copy_text), R.raw.contact_check)
    
    def show_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int, icon_res_id: int = 0):
        """Показывает сообщение с кнопкой перехода к посту"""
        _BulletinHelper.show_with_button(
            f"{self.prefix} {message}" if self.prefix else message,
            icon_res_id,
            button_text,
            on_click=lambda: get_last_fragment().presentFragment(ChatActivity.of(peer_id, message_id)),
        )
    
    def show_info_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        """Показывает информацию с кнопкой перехода к посту"""
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.info)
    
    def show_error_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        """Показывает ошибку с кнопкой перехода к посту"""
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.error)
    
    def show_success_with_post_redirect(self, message: str, button_text: str, peer_id: int, message_id: int):
        """Показывает успех с кнопкой перехода к посту"""
        self.show_with_post_redirect(message, button_text, peer_id, message_id, R.raw.contact_check)


def build_bulletin_helper(prefix: Optional[str] = None) -> InnerBulletinHelper:
    """Создаёт BulletinHelper с префиксом"""
    return InnerBulletinHelper(prefix)


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


# ==================== FileSystem Helpers ====================
class FileSystem:
    """Утилиты для работы с файловой системой"""
    
    File = File
    
    @classmethod
    def basedir(cls, *path: str) -> str:
        """Возвращает путь к директории плагинов"""
        if not PLUGINS_DIRECTORY:
            raise RuntimeError("PLUGINS_DIRECTORY not initialized")
        
        if path:
            return os.path.join(PLUGINS_DIRECTORY, *path)
        return PLUGINS_DIRECTORY
    
    @classmethod
    def cachedir(cls, *path: str) -> str:
        """Возвращает путь к директории кеша"""
        if not CACHE_DIRECTORY:
            raise RuntimeError("CACHE_DIRECTORY not initialized")
        
        if path:
            return os.path.join(CACHE_DIRECTORY, *path)
        return CACHE_DIRECTORY
    
    @classmethod
    def get_file_content(cls, file_path: str, mode: str = "rb") -> Union[bytes, str]:
        """Читает содержимое файла"""
        with open(file_path, mode) as f:
            return f.read()
    
    @classmethod
    def write_file(cls, file_path: str, content: Union[bytes, str], mode: str = "wb"):
        """Записывает содержимое в файл"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode) as f:
            f.write(content)
    
    @classmethod
    def delete_file(cls, file_path: str):
        """Удаляет файл"""
        if os.path.exists(file_path):
            os.remove(file_path)


# ==================== Spinner Alert Dialog ====================
class SpinnerAlertDialog:
    """Диалог с индикатором загрузки"""
    
    def __init__(self, text: Optional[str] = None):
        from org.telegram.ui.Components import LineProgressView
        
        self.text = text or DEFAULT_SPINNER_TEXT
        self.alert_builder = None
        self.alert_dialog = None
        self._shown = False
    
    def show(self):
        """Показывает диалог"""
        if self._shown:
            return
        
        @run_on_ui_thread
        def _show():
            from org.telegram.ui.Components import LineProgressView
            
            fragment = get_last_fragment()
            if not fragment:
                return
            
            activity = fragment.getParentActivity()
            if not activity:
                return
            
            resources_provider = fragment.getResourceProvider()
            
            self.alert_builder = AlertDialogBuilder(activity, resources_provider)
            
            # Создаем layout
            container = LinearLayout(activity)
            container.setOrientation(LinearLayout.VERTICAL)
            container.setPadding(
                AndroidUtilities.dp(24),
                AndroidUtilities.dp(16),
                AndroidUtilities.dp(24),
                AndroidUtilities.dp(16)
            )
            
            # Текст
            textView = TextView(activity)
            textView.setText(self.text)
            textView.setTextSize(TypedValue.COMPLEX_UNIT_DIP, 16)
            textView.setTextColor(Theme.getColor(Theme.key_dialogTextBlack, resources_provider))
            textView.setGravity(Gravity.CENTER)
            container.addView(textView)
            
            # Прогресс бар
            progress = LineProgressView(activity)
            progress.setProgressColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlueText, resources_provider))
            container.addView(progress, LinearLayout.LayoutParams(-1, AndroidUtilities.dp(4)))
            progress.setPadding(0, AndroidUtilities.dp(16), 0, 0)
            
            self.alert_builder.setView(container)
            self.alert_dialog = self.alert_builder.create()
            self.alert_dialog.setCanceledOnTouchOutside(False)
            self.alert_dialog.show()
        
        _show()
        self._shown = True
    
    def hide(self):
        """Скрывает диалог"""
        if not self._shown:
            return
        
        @run_on_ui_thread
        def _hide():
            if self.alert_dialog:
                try:
                    self.alert_dialog.dismiss()
                except:
                    pass
        
        _hide()
        self._shown = False
    
    def __enter__(self):
        """Context manager entry"""
        self.show()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.hide()
        return False


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
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
    
    def before_hooked_method(self, param):
        if not self.plugin.get_setting("enable_article_viewer_fix", False):
            return
        param.setResult(False)


# 3. NoCallConfirmation - убирает подтверждение звонка
class NoCallConfirmationHook(MethodHook):
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
    
    def before_hooked_method(self, param):
        if self.plugin.get_setting("enable_no_call_confirmation", False):
            param.args[6] = True


# 4. OldBottomForward - возвращает старый диалог пересылки
class OldBottomForwardHook(MethodHook):
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
    
    def before_hooked_method(self, param):
        if not self.plugin.get_setting("enable_old_bottom_forward", False):
            return
        param.args[0] = True


# ==================== Mixin класс для плагинов ====================
class MSPlugin:
    """
    Mixin класс для плагинов с расширенным функционалом MSLib
    
    Использование:
        class MyPlugin(MSPlugin, BasePlugin):
            strings = {"en": {...}, "ru": {...}}
            
            @command("test")
            def test_cmd(self, cmd):
                self.answer(cmd.params, "Hello!")
    
    Предоставляет:
    - JsonDB для хранения данных
    - Утилиты логирования
    - Методы локализации
    - Автоматическую регистрацию команд
    """
    
    strings: Dict[str, Dict[str, str]] = {}
    
    def __init__(self):
        super().__init__()
        self.db: Optional[JsonDB] = None
        self._commands = {}
        self._uri_handlers = {}
        self._watchers = {}
    
    def on_plugin_load(self):
        """Инициализирует БД и регистрирует обработчики"""
        if hasattr(super(), 'on_plugin_load'):
            super().on_plugin_load()
        
        # Инициализация JsonDB
        if CACHE_DIRECTORY:
            db_path = os.path.join(CACHE_DIRECTORY, f"{self.id}_data.json")
            self.db = JsonDB(db_path)
        
        # Автоматическая регистрация команд, URI и наблюдателей
        self._auto_register_handlers()
    
    def _auto_register_handlers(self):
        """Автоматически регистрирует команды и обработчики"""
        for name in dir(self):
            if name.startswith('_'):
                continue
            
            try:
                attr = getattr(self, name)
                if not callable(attr):
                    continue
                
                # Регистрация команд
                if hasattr(attr, '__is_command__'):
                    cmd = attr.__cmd__
                    self._commands[cmd] = attr
                    for alias in (attr.__aliases__ or []):
                        self._commands[alias] = attr
                
                # Регистрация URI обработчиков
                if hasattr(attr, '__is_uri_handler__'):
                    self._uri_handlers[attr.__uri__] = attr
                
                # Регистрация наблюдателей
                if hasattr(attr, '__is_watcher__'):
                    self._watchers[name] = attr
            
            except Exception as e:
                logger.error(f"Failed to register handler {name}: {format_exc_only(e)}")
    
    def get_db(self, key: str, default: Any = None) -> Any:
        """Получает значение из БД"""
        if self.db is None:
            return default
        return self.db.get(key, default)
    
    def set_db(self, key: str, value: Any):
        """Сохраняет значение в БД"""
        if self.db is not None:
            self.db.set(key, value)
    
    def lstrings(self) -> Dict[str, str]:
        """Получает строки локализации для текущей локали"""
        locale = LOCALE or "en"
        return self.strings.get(locale, self.strings.get("en", {}))
    
    def string(self, key: str, *args, **kwargs) -> str:
        """Получает локализованную строку с форматированием"""
        text = self.lstrings().get(key, key)
        try:
            if args or kwargs:
                return text.format(*args, **kwargs)
            return text
        except Exception:
            return text
    
    def plugin_log(self, message: str, level: str = "INFO"):
        """Логирует сообщение"""
        logger.log(getattr(logging, level, logging.INFO), f"[{self.id}] {message}")
    
    def plugin_debug(self, message: str):
        """Логирует debug сообщение"""
        self.plugin_log(message, "DEBUG")
    
    def plugin_info(self, message: str):
        """Логирует info сообщение"""
        self.plugin_log(message, "INFO")
    
    def plugin_warn(self, message: str):
        """Логирует warning сообщение"""
        self.plugin_log(message, "WARNING")
    
    def plugin_error(self, message: str):
        """Логирует error сообщение"""
        self.plugin_log(message, "ERROR")


# Глобальные экземпляры
autoupdater: Optional[AutoUpdater] = None
MSLib_instance: Optional['MSLib'] = None


class MSLib(BasePlugin):
    strings = {
        "en": {
            "commands_header": "Commands",
            "command_prefix_label": "Command prefix",
            "command_prefix_hint": "Symbol or text to identify commands (default: .)",
            "autoupdater_header": "AutoUpdater",
            "enable_autoupdater": "Enable AutoUpdater",
            "autoupdater_hint": "Automatically check for plugin updates",
            "force_update_check": "Force update check",
            "autoupdate_timeout_title": "Update check interval",
            "autoupdate_timeout_hint": "Time in seconds between update checks",
            "disable_timestamp_check_title": "Disable message edit check",
            "disable_timestamp_check_hint": "Plugin will be updated even if the file has not been modified",
            "plugins_header": "Integrated Plugins",
            "hashtags_fix": "HashTags Fix",
            "hashtags_fix_hint": "Open \"This chat\" instead of \"Public Posts\" on hashtag click",
            "article_viewer_fix": "Article Viewer Fix",
            "article_viewer_fix_hint": "Disable swipe-to-close gesture in browser",
            "no_call_confirmation": "No Call Confirmation",
            "no_call_confirmation_hint": "Skip call confirmation dialog",
            "old_bottom_forward": "Old Bottom Forward",
            "old_bottom_forward_hint": "Brings back old forward dialog for the bottom button",
            # Уведомления интегрированных плагинов
            "hashtags_fix_enabled": "HashTags Fix enabled",
            "hashtags_fix_disabled": "HashTags Fix disabled",
            "article_viewer_fix_enabled": "Article Viewer Fix enabled",
            "article_viewer_fix_disabled": "Article Viewer Fix disabled",
            "no_call_confirmation_enabled": "No Call Confirmation enabled",
            "no_call_confirmation_disabled": "No Call Confirmation disabled",
            "old_bottom_forward_enabled": "Old Bottom Forward enabled",
            "old_bottom_forward_disabled": "Old Bottom Forward disabled",
            "dev_header": "Developer",
            "debug_mode_title": "Debug mode",
            "debug_mode_hint": "Enables detailed logging for troubleshooting",
            "loaded": "MSLib loaded successfully!",
            "unloaded": "MSLib unloaded.",
        },
        "ru": {
            "commands_header": "Команды",
            "command_prefix_label": "Префикс команд",
            "command_prefix_hint": "Символ или текст для распознавания команд (по умолчанию: .)",
            "autoupdater_header": "Автообновление",
            "enable_autoupdater": "Включить автообновление",
            "autoupdater_hint": "Автоматически проверять обновления плагинов",
            "force_update_check": "Принудительная проверка",
            "autoupdate_timeout_title": "Интервал проверки обновлений",
            "autoupdate_timeout_hint": "Время в секундах между проверками обновлений",
            "disable_timestamp_check_title": "Отключить проверку редактирования",
            "disable_timestamp_check_hint": "Плагин будет обновлен, даже если файл не был изменен",
            "plugins_header": "Интегрированные плагины",
            "hashtags_fix": "Исправление хештегов",
            "hashtags_fix_hint": "Открывать \"Этот чат\" вместо \"Публичные посты\" при клике на хештег",
            "article_viewer_fix": "Исправление просмотра статей",
            "article_viewer_fix_hint": "Отключить свайп закрытия (слева направо) в браузере",
            "no_call_confirmation": "Без подтверждения звонка",
            "no_call_confirmation_hint": "Убрать диалог подтверждения при звонке",
            "old_bottom_forward": "Старая пересылка",
            "old_bottom_forward_hint": "Возвращает привычное открытие диалогов при нажатии на нижнюю кнопку \"Переслать\"",
            # Уведомления интегрированных плагинов
            "hashtags_fix_enabled": "Исправление хештегов включено",
            "hashtags_fix_disabled": "Исправление хештегов выключено",
            "article_viewer_fix_enabled": "Исправление просмотра статей включено",
            "article_viewer_fix_disabled": "Исправление просмотра статей выключено",
            "no_call_confirmation_enabled": "Без подтверждения звонка включено",
            "no_call_confirmation_disabled": "Без подтверждения звонка выключено",
            "old_bottom_forward_enabled": "Старая пересылка включена",
            "old_bottom_forward_disabled": "Старая пересылка выключена",
            "dev_header": "Разработчик",
            "debug_mode_title": "Режим отладки",
            "debug_mode_hint": "Включает подробное логирование для диагностики",
            "loaded": "MSLib успешно загружена!",
            "unloaded": "MSLib выгружена.",
        }
    }
    
    def on_plugin_load(self):
        """Вызывается при загрузке плагина"""
        global autoupdater, MSLib_instance, command_manager, companion
        
        # Сохраняем экземпляр для доступа из других мест
        MSLib_instance = self
        
        # Инициализация констант
        _init_constants()
        
        # Инициализация companion для хранения данных между перезагрузками
        companion = Companion()
        companion.initialize()
        logger.info("Companion initialized")
        
        # Инициализация CommandManager
        command_manager = CommandManager()
        command_manager.mark_not_temporal()
        command_manager.load_pending_commands()
        logger.info("CommandManager initialized")
        
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
        """Регистрация всех встроенных плагинов (хуки сами проверяют настройки)"""
        try:
            # 1. HashTags Fix - исправление поиска хэштегов
            from java.lang import Class as JavaClass
            chat_activity_class = ChatActivity.getClass()
            method = chat_activity_class.getDeclaredMethod(
                "openHashtagSearch", 
                String.getClass(), Boolean.TYPE
            )
            self.hook_method(method, HashTagsFixHook(self))
            
            # 2. Article Viewer Fix - фикс просмотра статей
            article_viewer_class = ArticleViewer.getClass()
            method = article_viewer_class.getDeclaredMethod(
                "shouldProcessUrl", String.getClass()
            )
            self.hook_method(method, ArticleViewerFixHook(self))
            
            # 3. No Call Confirmation - убирает подтверждение звонка
            voip_activity_class = VoIPActivity.getClass()
            method = voip_activity_class.getDeclaredMethod(
                "initiateCall", 
                Long.TYPE, Boolean.TYPE, Integer.TYPE, 
                Integer.TYPE, Boolean.TYPE, Boolean.TYPE, Boolean.TYPE
            )
            self.hook_method(method, NoCallConfirmationHook(self))
            
            # 4. Old Bottom Forward - старый диалог пересылки
            base_fragment_class = BaseFragment.getClass()
            method = base_fragment_class.getDeclaredMethod(
                "showDialog", Dialog.getClass(), Boolean.TYPE
            )
            self.hook_method(method, OldBottomForwardHook(self))
            
            logger.info("Integrated plugins hooks registered")
        except Exception as e:
            logger.error(f"Failed to setup integrated plugins: {e}")
    
    def _on_integrated_plugin_toggle(self, key: str, value: bool):
        """Callback при изменении настройки интегрированного плагина (мгновенная активация)"""
        plugin_name = key.replace("enable_", "")
        status = "enabled" if value else "disabled"
        level = "success" if value else "info"
        
        _bulletin(level, localise(f"{plugin_name}_{status}"))
    
    def on_plugin_unload(self):
        """Вызывается при выгрузке плагина"""
        global autoupdater, command_manager
        
        logger.info(localise("unloaded"))
        self.log("MSLib unloaded")
        
        # Сохранение команд в companion для восстановления после перезагрузки
        if command_manager:
            command_manager.save_commands_as_pending()
            command_manager.unregister_all()
            logger.info("Commands saved to companion")
        
        # Остановка автообновления
        if autoupdater:
            autoupdater.force_stop()
            autoupdater = None
            logger.info("AutoUpdater stopped")
    

    def create_settings(self):
        def force_update_check_onclick(_):
            """Принудительная проверка обновлений"""
            if autoupdater:
                autoupdater.force_update_check()
                _bulletin("success", localise("update_check_started"))
            else:
                _bulletin("error", localise("autoupdater_not_initialized"))
        
        def switch_debug_mode(new_value: bool):
            """Переключение режима отладки"""
            logger.setLevel(logging.DEBUG if new_value else logging.INFO)
            logger.info(f"Debug mode: {new_value}, level: {logging.getLevelName(logger.level)}")
        
        return [
            Header(text=localise("commands_header")),
            Input(
                key="command_prefix",
                text=localise("command_prefix_label"),
                subtext=localise("command_prefix_hint"),
                default=".",
                icon="msg_limit_stories"
            ),
            Divider(),
            Header(text=localise("autoupdater_header")),
            Switch(
                key="enable_autoupdater",
                text=localise("enable_autoupdater"),
                subtext=localise("autoupdater_hint"),
                default=False,
                icon="msg_autodownload"
            ),
            Text(
                text=localise("force_update_check"),
                icon="msg_photo_switch2",
                on_click=force_update_check_onclick
            ),
            Input(
                key="autoupdate_timeout",
                text=localise("autoupdate_timeout_title"),
                subtext=localise("autoupdate_timeout_hint"),
                default=DEFAULT_AUTOUPDATE_TIMEOUT,
                icon="msg2_autodelete"
            ),
            Switch(
                key="disable_timestamp_check",
                text=localise("disable_timestamp_check_title"),
                subtext=localise("disable_timestamp_check_hint"),
                default=DEFAULT_DISABLE_TIMESTAMP_CHECK,
                icon="msg_recent"
            ),
            Divider(),
            Header(text=localise("plugins_header")),
            Switch(
                key="enable_hashtags_fix",
                text=localise("hashtags_fix"),
                subtext=localise("hashtags_fix_hint"),
                default=False,
                icon="msg_link",
                on_change=lambda v: self._on_integrated_plugin_toggle("enable_hashtags_fix", v)
            ),
            Switch(
                key="enable_article_viewer_fix",
                text=localise("article_viewer_fix"),
                subtext=localise("article_viewer_fix_hint"),
                default=False,
                icon="msg_instant",
                on_change=lambda v: self._on_integrated_plugin_toggle("enable_article_viewer_fix", v)
            ),
            Switch(
                key="enable_no_call_confirmation",
                text=localise("no_call_confirmation"),
                subtext=localise("no_call_confirmation_hint"),
                default=False,
                icon="msg_calls",
                on_change=lambda v: self._on_integrated_plugin_toggle("enable_no_call_confirmation", v)
            ),
            Switch(
                key="enable_old_bottom_forward",
                text=localise("old_bottom_forward"),
                subtext=localise("old_bottom_forward_hint"),
                default=False,
                icon="msg_forward",
                on_change=lambda v: self._on_integrated_plugin_toggle("enable_old_bottom_forward", v)
            ),
            Divider(),
            Header(text=localise("dev_header")),
            Switch(
                key="debug_mode",
                text=localise("debug_mode_title"),
                subtext=localise("debug_mode_hint"),
                default=DEFAULT_DEBUG_MODE,
                icon="msg_log",
                on_change=switch_debug_mode
            ),
            Divider("Special thanks to @bleizix"),
        ]


__all__ = [
    # Основной класс
    'MSLib',
    'MSPlugin',
    
    # Классы для работы с кешем
    'CacheFile',
    'JsonCacheFile',
    'JsonDB',
    
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
    'CommandManager',
    'Command',
    'ArgSpec',
    'create_command',
    'parse_args',
    'cast_arg',
    'smart_cast',
    'command_manager',
    
    # Companion
    'Companion',
    'companion',
    
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
    'SpinnerAlertDialog',
    'FileSystem',
    
    # Inline система
    'Inline',
    
    # Декораторы
    'command',
    'uri',
    'message_uri',
    'watcher',
    
    # Интегрированные плагины (хуки)
    'HashTagsFixHook',
    'ArticleViewerFixHook',
    'NoCallConfirmationHook',
    'OldBottomForwardHook',
    
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
    'get_command_prefix',
    'pluralization_string',
    'runtime_exec',
    
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
