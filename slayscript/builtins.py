"""Built-in functions for SlayScript."""

import socket
import random
import time
import webbrowser
import os
import json
from typing import Any, List
from .environment import BuiltinFunction
from .errors import ForbiddenMagic, PortalFailure, VoiceSilenced, ScrollDamaged, OracleSilent, QuestFailed

# Global TTS engine (lazy initialized)
_tts_engine = None


def get_tts_engine():
    """Get or initialize the TTS engine."""
    global _tts_engine
    if _tts_engine is None:
        try:
            import pyttsx3
            _tts_engine = pyttsx3.init()
        except ImportError:
            raise VoiceSilenced("pyttsx3 is not installed. Run: pip install pyttsx3")
        except Exception as e:
            raise VoiceSilenced(f"Failed to initialize TTS: {e}")
    return _tts_engine


# ============ Text-to-Speech Functions ============

def builtin_speak_spell(interpreter, args: List[Any]) -> None:
    """speak_spell(text) - Speak text aloud."""
    if len(args) != 1:
        raise ForbiddenMagic("speak_spell requires exactly 1 argument")
    text = str(args[0])
    try:
        engine = get_tts_engine()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Speaking]: {text}")


def builtin_whisper_spell(interpreter, args: List[Any]) -> None:
    """whisper_spell(text) - Speak quietly."""
    if len(args) != 1:
        raise ForbiddenMagic("whisper_spell requires exactly 1 argument")
    text = str(args[0])
    try:
        engine = get_tts_engine()
        # Lower volume for whisper
        original_volume = engine.getProperty('volume')
        engine.setProperty('volume', 0.3)
        engine.say(text)
        engine.runAndWait()
        engine.setProperty('volume', original_volume)
    except Exception:
        print(f"[Whispering]: {text}")


def builtin_shout_spell(interpreter, args: List[Any]) -> None:
    """shout_spell(text) - Speak loudly."""
    if len(args) != 1:
        raise ForbiddenMagic("shout_spell requires exactly 1 argument")
    text = str(args[0])
    try:
        engine = get_tts_engine()
        # Max volume for shout
        original_volume = engine.getProperty('volume')
        engine.setProperty('volume', 1.0)
        engine.say(text.upper())
        engine.runAndWait()
        engine.setProperty('volume', original_volume)
    except Exception:
        print(f"[SHOUTING]: {text.upper()}")


def builtin_change_voice(interpreter, args: List[Any]) -> None:
    """change_voice(id) - Switch voice by index."""
    if len(args) != 1:
        raise ForbiddenMagic("change_voice requires exactly 1 argument")
    voice_id = int(args[0])
    try:
        engine = get_tts_engine()
        voices = engine.getProperty('voices')
        if 0 <= voice_id < len(voices):
            engine.setProperty('voice', voices[voice_id].id)
        else:
            raise VoiceSilenced(f"Voice id {voice_id} not found. Available: 0-{len(voices)-1}")
    except VoiceSilenced:
        raise
    except Exception as e:
        raise VoiceSilenced(f"Failed to change voice: {e}")


def builtin_set_speech_rate(interpreter, args: List[Any]) -> None:
    """set_speech_rate(rate) - Adjust speech speed (words per minute)."""
    if len(args) != 1:
        raise ForbiddenMagic("set_speech_rate requires exactly 1 argument")
    rate = int(args[0])
    try:
        engine = get_tts_engine()
        engine.setProperty('rate', rate)
    except Exception as e:
        raise VoiceSilenced(f"Failed to set speech rate: {e}")


# ============ Networking Functions ============

def builtin_summon_portal(interpreter, args: List[Any]) -> socket.socket:
    """summon_portal(host, port) - Connect to a server."""
    if len(args) != 2:
        raise ForbiddenMagic("summon_portal requires 2 arguments (host, port)")
    host = str(args[0])
    port = int(args[1])
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock
    except Exception as e:
        raise PortalFailure(f"Failed to summon portal to {host}:{port}: {e}")


def builtin_open_hellmouth(interpreter, args: List[Any]) -> socket.socket:
    """open_hellmouth(port) - Start a server."""
    if len(args) != 1:
        raise ForbiddenMagic("open_hellmouth requires 1 argument (port)")
    port = int(args[0])
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))
        sock.listen(5)
        return sock
    except Exception as e:
        raise PortalFailure(f"Failed to open hellmouth on port {port}: {e}")


def builtin_send_owl(interpreter, args: List[Any]) -> int:
    """send_owl(portal, message) - Send data through portal."""
    if len(args) != 2:
        raise ForbiddenMagic("send_owl requires 2 arguments (portal, message)")
    sock = args[0]
    message = str(args[1])
    try:
        return sock.send(message.encode('utf-8'))
    except Exception as e:
        raise PortalFailure(f"Owl failed to deliver message: {e}")


def builtin_receive_owl(interpreter, args: List[Any]) -> str:
    """receive_owl(portal) - Receive data from portal."""
    if len(args) < 1 or len(args) > 2:
        raise ForbiddenMagic("receive_owl requires 1-2 arguments (portal, [buffer_size])")
    sock = args[0]
    buffer_size = int(args[1]) if len(args) > 1 else 1024
    try:
        data = sock.recv(buffer_size)
        return data.decode('utf-8')
    except Exception as e:
        raise PortalFailure(f"Failed to receive owl: {e}")


def builtin_close_portal(interpreter, args: List[Any]) -> None:
    """close_portal(portal) - Close a connection."""
    if len(args) != 1:
        raise ForbiddenMagic("close_portal requires 1 argument (portal)")
    sock = args[0]
    try:
        sock.close()
    except Exception as e:
        raise PortalFailure(f"Failed to close portal: {e}")


def builtin_await_visitor(interpreter, args: List[Any]) -> tuple:
    """await_visitor(hellmouth) - Accept a connection."""
    if len(args) != 1:
        raise ForbiddenMagic("await_visitor requires 1 argument (hellmouth)")
    server_sock = args[0]
    try:
        client_sock, addr = server_sock.accept()
        return [client_sock, addr[0], addr[1]]  # Return as list [socket, host, port]
    except Exception as e:
        raise PortalFailure(f"Failed to await visitor: {e}")


# ============ HTML/CSS Generation ============

def builtin_conjure_canvas(interpreter, args: List[Any]) -> dict:
    """conjure_canvas(title) - Create a new HTML document."""
    if len(args) != 1:
        raise ForbiddenMagic("conjure_canvas requires 1 argument (title)")
    title = str(args[0])
    return {
        'title': title,
        'styles': [],
        'body': []
    }


def builtin_enchant_element(interpreter, args: List[Any]) -> dict:
    """enchant_element(tag, content, attrs) - Create an HTML element."""
    if len(args) < 2:
        raise ForbiddenMagic("enchant_element requires at least 2 arguments (tag, content)")
    tag = str(args[0])
    content = args[1]
    attrs = args[2] if len(args) > 2 else {}

    return {
        'type': 'element',
        'tag': tag,
        'content': content,
        'attrs': attrs
    }


def builtin_enchant_style(interpreter, args: List[Any]) -> dict:
    """enchant_style(selector, properties) - Create a CSS rule."""
    if len(args) != 2:
        raise ForbiddenMagic("enchant_style requires 2 arguments (selector, properties)")
    selector = str(args[0])
    properties = args[1]

    if not isinstance(properties, dict):
        raise ForbiddenMagic("Style properties must be a grimoire (dict)")

    return {
        'type': 'style',
        'selector': selector,
        'properties': properties
    }


def builtin_append_to_canvas(interpreter, args: List[Any]) -> dict:
    """append_to_canvas(canvas, element) - Add element to body."""
    if len(args) != 2:
        raise ForbiddenMagic("append_to_canvas requires 2 arguments (canvas, element)")
    canvas = args[0]
    element = args[1]

    if not isinstance(canvas, dict) or 'body' not in canvas:
        raise ForbiddenMagic("Invalid canvas")

    canvas['body'].append(element)
    return canvas


def builtin_add_style_to_canvas(interpreter, args: List[Any]) -> dict:
    """add_style_to_canvas(canvas, style) - Add CSS to document."""
    if len(args) != 2:
        raise ForbiddenMagic("add_style_to_canvas requires 2 arguments (canvas, style)")
    canvas = args[0]
    style = args[1]

    if not isinstance(canvas, dict) or 'styles' not in canvas:
        raise ForbiddenMagic("Invalid canvas")

    canvas['styles'].append(style)
    return canvas


def _render_element(element) -> str:
    """Render an element to HTML string."""
    if isinstance(element, str):
        return element

    if not isinstance(element, dict) or element.get('type') != 'element':
        return str(element)

    tag = element['tag']
    content = element['content']
    attrs = element.get('attrs', {})

    # Build attributes string
    attr_str = ''
    if attrs:
        attr_parts = [f'{k}="{v}"' for k, v in attrs.items()]
        attr_str = ' ' + ' '.join(attr_parts)

    # Render content
    if isinstance(content, list):
        inner = '\n'.join(_render_element(c) for c in content)
    elif isinstance(content, dict) and content.get('type') == 'element':
        inner = _render_element(content)
    else:
        inner = str(content) if content is not None else ''

    # Self-closing tags
    if tag in ('br', 'hr', 'img', 'input', 'meta', 'link'):
        return f'<{tag}{attr_str} />'

    return f'<{tag}{attr_str}>{inner}</{tag}>'


def _render_style(style) -> str:
    """Render a style rule to CSS string."""
    if not isinstance(style, dict) or style.get('type') != 'style':
        return ''

    selector = style['selector']
    properties = style['properties']

    props_str = '\n'.join(f'  {k}: {v};' for k, v in properties.items())
    return f'{selector} {{\n{props_str}\n}}'


def builtin_weave_page(interpreter, args: List[Any]) -> str:
    """weave_page(canvas) - Generate complete HTML string."""
    if len(args) != 1:
        raise ForbiddenMagic("weave_page requires 1 argument (canvas)")
    canvas = args[0]

    if not isinstance(canvas, dict):
        raise ForbiddenMagic("Invalid canvas")

    title = canvas.get('title', 'Untitled')
    styles = canvas.get('styles', [])
    body = canvas.get('body', [])

    # Build CSS
    css = '\n'.join(_render_style(s) for s in styles)

    # Build body
    body_html = '\n'.join(_render_element(e) for e in body)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{body_html}
</body>
</html>'''


def builtin_scribe_page(interpreter, args: List[Any]) -> str:
    """scribe_page(canvas, filename) - Write HTML to file."""
    if len(args) != 2:
        raise ForbiddenMagic("scribe_page requires 2 arguments (canvas, filename)")
    canvas = args[0]
    filename = str(args[1])

    html = builtin_weave_page(interpreter, [canvas])

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    return filename


def builtin_summon_browser(interpreter, args: List[Any]) -> bool:
    """summon_browser(filename) - Open file in browser."""
    if len(args) != 1:
        raise ForbiddenMagic("summon_browser requires 1 argument (filename)")
    filename = str(args[0])

    # Convert to absolute path if needed
    if not os.path.isabs(filename):
        filename = os.path.abspath(filename)

    return webbrowser.open(f'file://{filename}')


# ============ Standard I/O ============

def builtin_scribe_line(interpreter, args: List[Any]) -> None:
    """scribe_line(text) - Print with newline."""
    print(*[str(a) for a in args])


def builtin_scribe(interpreter, args: List[Any]) -> None:
    """scribe(text) - Print without newline."""
    print(*[str(a) for a in args], end='')


def builtin_prophecy_input(interpreter, args: List[Any]) -> str:
    """prophecy_input(prompt) - Read user input."""
    prompt = str(args[0]) if args else ""
    return input(prompt)


# ============ Utilities ============

def builtin_measure(interpreter, args: List[Any]) -> int:
    """measure(collection) - Get length."""
    if len(args) != 1:
        raise ForbiddenMagic("measure requires 1 argument")
    val = args[0]
    if hasattr(val, '__len__'):
        return len(val)
    raise ForbiddenMagic("Cannot measure this type")


def builtin_transform_to_rune(interpreter, args: List[Any]) -> int:
    """transform_to_rune(val) - Convert to integer."""
    if len(args) != 1:
        raise ForbiddenMagic("transform_to_rune requires 1 argument")
    try:
        return int(args[0])
    except (ValueError, TypeError) as e:
        raise ForbiddenMagic(f"Cannot transform to rune: {e}")


def builtin_transform_to_scroll(interpreter, args: List[Any]) -> str:
    """transform_to_scroll(val) - Convert to string."""
    if len(args) != 1:
        raise ForbiddenMagic("transform_to_scroll requires 1 argument")
    return str(args[0])


def builtin_transform_to_potion(interpreter, args: List[Any]) -> float:
    """transform_to_potion(val) - Convert to float."""
    if len(args) != 1:
        raise ForbiddenMagic("transform_to_potion requires 1 argument")
    try:
        return float(args[0])
    except (ValueError, TypeError) as e:
        raise ForbiddenMagic(f"Cannot transform to potion: {e}")


def builtin_random_fate(interpreter, args: List[Any]) -> int:
    """random_fate(min, max) - Random integer between min and max (inclusive)."""
    if len(args) != 2:
        raise ForbiddenMagic("random_fate requires 2 arguments (min, max)")
    min_val = int(args[0])
    max_val = int(args[1])
    return random.randint(min_val, max_val)


def builtin_slumber(interpreter, args: List[Any]) -> None:
    """slumber(seconds) - Sleep for given seconds."""
    if len(args) != 1:
        raise ForbiddenMagic("slumber requires 1 argument (seconds)")
    seconds = float(args[0])
    time.sleep(seconds)


def builtin_range(interpreter, args: List[Any]) -> list:
    """range(start, end, [step]) - Generate a list of numbers."""
    if len(args) < 1 or len(args) > 3:
        raise ForbiddenMagic("range requires 1-3 arguments")
    if len(args) == 1:
        return list(range(int(args[0])))
    elif len(args) == 2:
        return list(range(int(args[0]), int(args[1])))
    else:
        return list(range(int(args[0]), int(args[1]), int(args[2])))


def builtin_append(interpreter, args: List[Any]) -> None:
    """append(list, item) - Add item to list."""
    if len(args) != 2:
        raise ForbiddenMagic("append requires 2 arguments (list, item)")
    if not isinstance(args[0], list):
        raise ForbiddenMagic("First argument must be a tome (list)")
    args[0].append(args[1])


def builtin_remove(interpreter, args: List[Any]) -> None:
    """remove(list, item) - Remove item from list."""
    if len(args) != 2:
        raise ForbiddenMagic("remove requires 2 arguments (list, item)")
    if not isinstance(args[0], list):
        raise ForbiddenMagic("First argument must be a tome (list)")
    args[0].remove(args[1])


def builtin_keys(interpreter, args: List[Any]) -> list:
    """keys(dict) - Get dictionary keys."""
    if len(args) != 1:
        raise ForbiddenMagic("keys requires 1 argument")
    if not isinstance(args[0], dict):
        raise ForbiddenMagic("Argument must be a grimoire (dict)")
    return list(args[0].keys())


def builtin_values(interpreter, args: List[Any]) -> list:
    """values(dict) - Get dictionary values."""
    if len(args) != 1:
        raise ForbiddenMagic("values requires 1 argument")
    if not isinstance(args[0], dict):
        raise ForbiddenMagic("Argument must be a grimoire (dict)")
    return list(args[0].values())


def builtin_type_of(interpreter, args: List[Any]) -> str:
    """type_of(value) - Get the type name."""
    if len(args) != 1:
        raise ForbiddenMagic("type_of requires 1 argument")
    val = args[0]
    type_map = {
        str: "scroll",
        int: "rune",
        float: "potion",
        bool: "charm",
        list: "tome",
        dict: "grimoire",
        type(None): "void"
    }
    return type_map.get(type(val), "unknown")


# ============ File I/O Functions (Ancient Scrolls Theme) ============

def builtin_unroll_scroll(interpreter, args: List[Any]):
    """unroll_scroll(path, [mode]) - Open a file for reading or writing.

    Modes: "read" (default), "write", "append"
    Returns a file handle (scroll) for further operations.
    """
    if len(args) < 1 or len(args) > 2:
        raise ForbiddenMagic("unroll_scroll requires 1-2 arguments (path, [mode])")
    path = str(args[0])
    mode_map = {"read": "r", "write": "w", "append": "a"}
    mode = str(args[1]) if len(args) > 1 else "read"
    if mode not in mode_map:
        raise ScrollDamaged(f"Unknown scroll mode '{mode}'. Use 'read', 'write', or 'append'")
    try:
        return open(path, mode_map[mode], encoding='utf-8')
    except FileNotFoundError:
        raise ScrollDamaged(f"Scroll not found: {path}")
    except PermissionError:
        raise ScrollDamaged(f"Permission denied to access scroll: {path}")
    except Exception as e:
        raise ScrollDamaged(f"Failed to unroll scroll: {e}")


def builtin_seal_scroll(interpreter, args: List[Any]) -> None:
    """seal_scroll(handle) - Close an open file handle."""
    if len(args) != 1:
        raise ForbiddenMagic("seal_scroll requires 1 argument (handle)")
    handle = args[0]
    try:
        handle.close()
    except Exception as e:
        raise ScrollDamaged(f"Failed to seal scroll: {e}")


def builtin_inscribe_scroll(interpreter, args: List[Any]) -> int:
    """inscribe_scroll(path, content) - Write content to a file (overwrites)."""
    if len(args) != 2:
        raise ForbiddenMagic("inscribe_scroll requires 2 arguments (path, content)")
    path = str(args[0])
    content = str(args[1])
    try:
        with open(path, 'w', encoding='utf-8') as f:
            return f.write(content)
    except PermissionError:
        raise ScrollDamaged(f"Permission denied to inscribe scroll: {path}")
    except Exception as e:
        raise ScrollDamaged(f"Failed to inscribe scroll: {e}")


def builtin_chronicle_scroll(interpreter, args: List[Any]) -> int:
    """chronicle_scroll(path, content) - Append content to a file."""
    if len(args) != 2:
        raise ForbiddenMagic("chronicle_scroll requires 2 arguments (path, content)")
    path = str(args[0])
    content = str(args[1])
    try:
        with open(path, 'a', encoding='utf-8') as f:
            return f.write(content)
    except PermissionError:
        raise ScrollDamaged(f"Permission denied to chronicle scroll: {path}")
    except Exception as e:
        raise ScrollDamaged(f"Failed to chronicle scroll: {e}")


def builtin_decipher_scroll(interpreter, args: List[Any]) -> str:
    """decipher_scroll(path) - Read entire file contents."""
    if len(args) != 1:
        raise ForbiddenMagic("decipher_scroll requires 1 argument (path)")
    path = str(args[0])
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ScrollDamaged(f"Scroll not found: {path}")
    except PermissionError:
        raise ScrollDamaged(f"Permission denied to decipher scroll: {path}")
    except Exception as e:
        raise ScrollDamaged(f"Failed to decipher scroll: {e}")


def builtin_read_runes(interpreter, args: List[Any]) -> str:
    """read_runes(handle, [num_chars]) - Read from an open file handle."""
    if len(args) < 1 or len(args) > 2:
        raise ForbiddenMagic("read_runes requires 1-2 arguments (handle, [num_chars])")
    handle = args[0]
    num_chars = int(args[1]) if len(args) > 1 else -1
    try:
        return handle.read(num_chars) if num_chars > 0 else handle.read()
    except Exception as e:
        raise ScrollDamaged(f"Failed to read runes: {e}")


def builtin_etch_runes(interpreter, args: List[Any]) -> int:
    """etch_runes(handle, content) - Write to an open file handle."""
    if len(args) != 2:
        raise ForbiddenMagic("etch_runes requires 2 arguments (handle, content)")
    handle = args[0]
    content = str(args[1])
    try:
        return handle.write(content)
    except Exception as e:
        raise ScrollDamaged(f"Failed to etch runes: {e}")


def builtin_divine_lines(interpreter, args: List[Any]) -> list:
    """divine_lines(path) - Read file as list of lines."""
    if len(args) != 1:
        raise ForbiddenMagic("divine_lines requires 1 argument (path)")
    path = str(args[0])
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        raise ScrollDamaged(f"Scroll not found: {path}")
    except Exception as e:
        raise ScrollDamaged(f"Failed to divine lines: {e}")


def builtin_scroll_exists(interpreter, args: List[Any]) -> bool:
    """scroll_exists(path) - Check if a file exists."""
    if len(args) != 1:
        raise ForbiddenMagic("scroll_exists requires 1 argument (path)")
    path = str(args[0])
    return os.path.exists(path)


def builtin_banish_scroll(interpreter, args: List[Any]) -> bool:
    """banish_scroll(path) - Delete a file."""
    if len(args) != 1:
        raise ForbiddenMagic("banish_scroll requires 1 argument (path)")
    path = str(args[0])
    try:
        os.remove(path)
        return True
    except FileNotFoundError:
        raise ScrollDamaged(f"Scroll not found: {path}")
    except PermissionError:
        raise ScrollDamaged(f"Permission denied to banish scroll: {path}")
    except Exception as e:
        raise ScrollDamaged(f"Failed to banish scroll: {e}")


# ============ MySQL Functions (Oracle of Delphi Theme) ============

# Global MySQL connection cache
_mysql_connection = None


def _get_mysql():
    """Lazy-load MySQL connector."""
    try:
        import mysql.connector
        return mysql.connector
    except ImportError:
        raise OracleSilent("mysql-connector-python is not installed. Run: pip install mysql-connector-python")


def builtin_awaken_oracle(interpreter, args: List[Any]):
    """awaken_oracle(host, user, password, database, [port]) - Connect to MySQL database.

    Like consulting the Oracle of Delphi, this opens a connection to divine knowledge.
    """
    if len(args) < 4 or len(args) > 5:
        raise ForbiddenMagic("awaken_oracle requires 4-5 arguments (host, user, password, database, [port])")
    host = str(args[0])
    user = str(args[1])
    password = str(args[2])
    database = str(args[3])
    port = int(args[4]) if len(args) > 4 else 3306

    mysql = _get_mysql()
    try:
        connection = mysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        return connection
    except mysql.Error as e:
        raise OracleSilent(f"Failed to awaken oracle: {e}")


def builtin_dismiss_oracle(interpreter, args: List[Any]) -> None:
    """dismiss_oracle(connection) - Close the database connection."""
    if len(args) != 1:
        raise ForbiddenMagic("dismiss_oracle requires 1 argument (connection)")
    connection = args[0]
    try:
        connection.close()
    except Exception as e:
        raise OracleSilent(f"Failed to dismiss oracle: {e}")


def builtin_consult_oracle(interpreter, args: List[Any]) -> list:
    """consult_oracle(connection, query, [params]) - Execute SELECT query and return all rows.

    Seek wisdom from the oracle with a query. Returns a tome (list) of grimoires (dicts).
    """
    if len(args) < 2 or len(args) > 3:
        raise ForbiddenMagic("consult_oracle requires 2-3 arguments (connection, query, [params])")
    connection = args[0]
    query = str(args[1])
    params = tuple(args[2]) if len(args) > 2 and args[2] else None

    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        raise OracleSilent(f"Oracle consultation failed: {e}")


def builtin_divine_one(interpreter, args: List[Any]):
    """divine_one(connection, query, [params]) - Execute SELECT and return first row.

    Divine a single prophecy from the oracle.
    """
    if len(args) < 2 or len(args) > 3:
        raise ForbiddenMagic("divine_one requires 2-3 arguments (connection, query, [params])")
    connection = args[0]
    query = str(args[1])
    params = tuple(args[2]) if len(args) > 2 and args[2] else None

    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result
    except Exception as e:
        raise OracleSilent(f"Divination failed: {e}")


def builtin_decree_oracle(interpreter, args: List[Any]) -> int:
    """decree_oracle(connection, query, [params]) - Execute INSERT/UPDATE/DELETE.

    Issue a decree to modify the sacred records. Returns number of affected rows.
    """
    if len(args) < 2 or len(args) > 3:
        raise ForbiddenMagic("decree_oracle requires 2-3 arguments (connection, query, [params])")
    connection = args[0]
    query = str(args[1])
    params = tuple(args[2]) if len(args) > 2 and args[2] else None

    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected
    except Exception as e:
        connection.rollback()
        raise OracleSilent(f"Oracle decree failed: {e}")


def builtin_last_prophecy_id(interpreter, args: List[Any]) -> int:
    """last_prophecy_id(connection) - Get the last auto-increment ID from INSERT."""
    if len(args) != 1:
        raise ForbiddenMagic("last_prophecy_id requires 1 argument (connection)")
    connection = args[0]
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        result = cursor.fetchone()[0]
        cursor.close()
        return result
    except Exception as e:
        raise OracleSilent(f"Failed to retrieve last prophecy id: {e}")


def builtin_begin_ritual(interpreter, args: List[Any]) -> None:
    """begin_ritual(connection) - Start a database transaction."""
    if len(args) != 1:
        raise ForbiddenMagic("begin_ritual requires 1 argument (connection)")
    connection = args[0]
    try:
        connection.start_transaction()
    except Exception as e:
        raise OracleSilent(f"Failed to begin ritual: {e}")


def builtin_complete_ritual(interpreter, args: List[Any]) -> None:
    """complete_ritual(connection) - Commit the current transaction."""
    if len(args) != 1:
        raise ForbiddenMagic("complete_ritual requires 1 argument (connection)")
    connection = args[0]
    try:
        connection.commit()
    except Exception as e:
        raise OracleSilent(f"Failed to complete ritual: {e}")


def builtin_abandon_ritual(interpreter, args: List[Any]) -> None:
    """abandon_ritual(connection) - Rollback the current transaction."""
    if len(args) != 1:
        raise ForbiddenMagic("abandon_ritual requires 1 argument (connection)")
    connection = args[0]
    try:
        connection.rollback()
    except Exception as e:
        raise OracleSilent(f"Failed to abandon ritual: {e}")


# ============ Gameplay Functions (Quest/Legend Theme) ============


def builtin_forge_hero(interpreter, args: List[Any]) -> dict:
    """forge_hero(name, [class], [level]) - Create a new hero/player character.

    Forge a legendary hero with base stats inspired by classic RPGs.
    """
    if len(args) < 1 or len(args) > 3:
        raise ForbiddenMagic("forge_hero requires 1-3 arguments (name, [class], [level])")
    name = str(args[0])
    hero_class = str(args[1]) if len(args) > 1 else "adventurer"
    level = int(args[2]) if len(args) > 2 else 1

    # Base stats vary by class (inspired by classic RPG archetypes)
    class_stats = {
        "adventurer": {"strength": 10, "agility": 10, "wisdom": 10, "vitality": 10},
        "warrior": {"strength": 14, "agility": 8, "wisdom": 6, "vitality": 12},
        "mage": {"strength": 6, "agility": 8, "wisdom": 14, "vitality": 8},
        "rogue": {"strength": 8, "agility": 14, "wisdom": 8, "vitality": 8},
        "ranger": {"strength": 10, "agility": 12, "wisdom": 10, "vitality": 8},
        "cleric": {"strength": 8, "agility": 6, "wisdom": 14, "vitality": 10},
        "paladin": {"strength": 12, "agility": 6, "wisdom": 10, "vitality": 12},
        "bard": {"strength": 8, "agility": 10, "wisdom": 12, "vitality": 8},
    }

    base = class_stats.get(hero_class.lower(), class_stats["adventurer"])

    # Calculate derived stats
    max_health = base["vitality"] * 10 + (level - 1) * 5
    max_mana = base["wisdom"] * 5 + (level - 1) * 3

    return {
        "name": name,
        "class": hero_class.lower(),
        "level": level,
        "experience": 0,
        "health": max_health,
        "max_health": max_health,
        "mana": max_mana,
        "max_mana": max_mana,
        "strength": base["strength"],
        "agility": base["agility"],
        "wisdom": base["wisdom"],
        "vitality": base["vitality"],
        "gold": 100,
        "inventory": [],
        "equipped": {},
        "alive": True
    }


def builtin_forge_creature(interpreter, args: List[Any]) -> dict:
    """forge_creature(name, health, damage, [loot]) - Create an enemy/NPC.

    Summon a creature from the mythic bestiary.
    """
    if len(args) < 3 or len(args) > 4:
        raise ForbiddenMagic("forge_creature requires 3-4 arguments (name, health, damage, [loot])")
    name = str(args[0])
    health = int(args[1])
    damage = int(args[2])
    loot = args[3] if len(args) > 3 else []

    return {
        "name": name,
        "health": health,
        "max_health": health,
        "damage": damage,
        "loot": loot if isinstance(loot, list) else [loot],
        "alive": True
    }


def builtin_roll_destiny(interpreter, args: List[Any]) -> int:
    """roll_destiny(sides, [count], [modifier]) - Roll dice (like fate's hand).

    Roll the dice of destiny! Examples: roll_destiny(20) for d20, roll_destiny(6, 3) for 3d6.
    """
    if len(args) < 1 or len(args) > 3:
        raise ForbiddenMagic("roll_destiny requires 1-3 arguments (sides, [count], [modifier])")
    sides = int(args[0])
    count = int(args[1]) if len(args) > 1 else 1
    modifier = int(args[2]) if len(args) > 2 else 0

    if sides < 1:
        raise QuestFailed("Dice must have at least 1 side")
    if count < 1:
        raise QuestFailed("Must roll at least 1 die")

    total = sum(random.randint(1, sides) for _ in range(count))
    return total + modifier


def builtin_inflict_wound(interpreter, args: List[Any]) -> dict:
    """inflict_wound(target, damage) - Deal damage to a creature or hero.

    The cruel hand of fate strikes! Returns the updated target.
    """
    if len(args) != 2:
        raise ForbiddenMagic("inflict_wound requires 2 arguments (target, damage)")
    target = args[0]
    damage = int(args[1])

    if not isinstance(target, dict) or "health" not in target:
        raise QuestFailed("Target must be a hero or creature with health")

    target["health"] = max(0, target["health"] - damage)
    if target["health"] <= 0:
        target["alive"] = False

    return target


def builtin_restore_vigor(interpreter, args: List[Any]) -> dict:
    """restore_vigor(target, amount) - Heal a creature or hero.

    The blessing of restoration flows! Returns the updated target.
    """
    if len(args) != 2:
        raise ForbiddenMagic("restore_vigor requires 2 arguments (target, amount)")
    target = args[0]
    amount = int(args[1])

    if not isinstance(target, dict) or "health" not in target:
        raise QuestFailed("Target must be a hero or creature with health")

    max_health = target.get("max_health", target["health"])
    target["health"] = min(max_health, target["health"] + amount)
    if target["health"] > 0:
        target["alive"] = True

    return target


def builtin_bestow_artifact(interpreter, args: List[Any]) -> dict:
    """bestow_artifact(hero, item) - Add an item to hero's inventory.

    A legendary artifact joins your quest!
    """
    if len(args) != 2:
        raise ForbiddenMagic("bestow_artifact requires 2 arguments (hero, item)")
    hero = args[0]
    item = args[1]

    if not isinstance(hero, dict) or "inventory" not in hero:
        raise QuestFailed("First argument must be a hero with an inventory")

    hero["inventory"].append(item)
    return hero


def builtin_claim_loot(interpreter, args: List[Any]) -> list:
    """claim_loot(creature) - Collect loot from a defeated creature.

    Claim the spoils of victory!
    """
    if len(args) != 1:
        raise ForbiddenMagic("claim_loot requires 1 argument (creature)")
    creature = args[0]

    if not isinstance(creature, dict):
        raise QuestFailed("Argument must be a creature")

    if creature.get("alive", True):
        raise QuestFailed("Cannot loot a living creature!")

    loot = creature.get("loot", [])
    creature["loot"] = []  # Loot can only be claimed once
    return loot


def builtin_check_fate(interpreter, args: List[Any]) -> bool:
    """check_fate(target) - Check if a hero or creature is still alive."""
    if len(args) != 1:
        raise ForbiddenMagic("check_fate requires 1 argument (target)")
    target = args[0]

    if not isinstance(target, dict):
        raise QuestFailed("Argument must be a hero or creature")

    return target.get("alive", target.get("health", 0) > 0)


def builtin_gain_experience(interpreter, args: List[Any]) -> dict:
    """gain_experience(hero, amount) - Award experience points to hero.

    Your deeds echo through legend! Returns updated hero with possible level up.
    """
    if len(args) != 2:
        raise ForbiddenMagic("gain_experience requires 2 arguments (hero, amount)")
    hero = args[0]
    amount = int(args[1])

    if not isinstance(hero, dict) or "experience" not in hero:
        raise QuestFailed("First argument must be a hero")

    hero["experience"] += amount

    # Simple level-up formula: 100 XP per level
    xp_for_next = hero["level"] * 100
    while hero["experience"] >= xp_for_next:
        hero["experience"] -= xp_for_next
        hero["level"] += 1
        # Boost stats on level up
        hero["max_health"] += 5
        hero["health"] = hero["max_health"]
        hero["max_mana"] += 3
        hero["mana"] = hero["max_mana"]
        hero["strength"] += 1
        hero["agility"] += 1
        hero["wisdom"] += 1
        hero["vitality"] += 1
        xp_for_next = hero["level"] * 100

    return hero


def builtin_saga_save(interpreter, args: List[Any]) -> bool:
    """saga_save(data, path) - Save game state to a JSON file.

    Chronicle your saga for future generations!
    """
    if len(args) != 2:
        raise ForbiddenMagic("saga_save requires 2 arguments (data, path)")
    data = args[0]
    path = str(args[1])

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        raise QuestFailed(f"Failed to save saga: {e}")


def builtin_saga_load(interpreter, args: List[Any]):
    """saga_load(path) - Load game state from a JSON file.

    Resume your legendary quest!
    """
    if len(args) != 1:
        raise ForbiddenMagic("saga_load requires 1 argument (path)")
    path = str(args[0])

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise QuestFailed(f"Saga not found: {path}")
    except json.JSONDecodeError as e:
        raise QuestFailed(f"Saga is corrupted: {e}")
    except Exception as e:
        raise QuestFailed(f"Failed to load saga: {e}")


def builtin_encounter_chance(interpreter, args: List[Any]) -> bool:
    """encounter_chance(percent) - Random chance check (0-100).

    Will fate favor your quest? Returns true if the check succeeds.
    """
    if len(args) != 1:
        raise ForbiddenMagic("encounter_chance requires 1 argument (percent)")
    percent = float(args[0])

    if percent < 0 or percent > 100:
        raise QuestFailed("Percent must be between 0 and 100")

    return random.random() * 100 < percent


def builtin_choose_fate(interpreter, args: List[Any]):
    """choose_fate(options) - Randomly select from a list of options.

    Let destiny choose your path!
    """
    if len(args) != 1:
        raise ForbiddenMagic("choose_fate requires 1 argument (options)")
    options = args[0]

    if not isinstance(options, list) or len(options) == 0:
        raise QuestFailed("Options must be a non-empty tome (list)")

    return random.choice(options)


# ============ Register All Builtins ============

def register_builtins(environment):
    """Register all built-in functions in the given environment."""
    builtins = [
        # TTS
        ("speak_spell", builtin_speak_spell, 1),
        ("whisper_spell", builtin_whisper_spell, 1),
        ("shout_spell", builtin_shout_spell, 1),
        ("change_voice", builtin_change_voice, 1),
        ("set_speech_rate", builtin_set_speech_rate, 1),

        # Networking
        ("summon_portal", builtin_summon_portal, 2),
        ("open_hellmouth", builtin_open_hellmouth, 1),
        ("send_owl", builtin_send_owl, 2),
        ("receive_owl", builtin_receive_owl, -1),
        ("close_portal", builtin_close_portal, 1),
        ("await_visitor", builtin_await_visitor, 1),

        # HTML/CSS
        ("conjure_canvas", builtin_conjure_canvas, 1),
        ("enchant_element", builtin_enchant_element, -1),
        ("enchant_style", builtin_enchant_style, 2),
        ("append_to_canvas", builtin_append_to_canvas, 2),
        ("add_style_to_canvas", builtin_add_style_to_canvas, 2),
        ("weave_page", builtin_weave_page, 1),
        ("scribe_page", builtin_scribe_page, 2),
        ("summon_browser", builtin_summon_browser, 1),

        # I/O
        ("scribe_line", builtin_scribe_line, -1),
        ("scribe", builtin_scribe, -1),
        ("prophecy_input", builtin_prophecy_input, -1),

        # Utilities
        ("measure", builtin_measure, 1),
        ("transform_to_rune", builtin_transform_to_rune, 1),
        ("transform_to_scroll", builtin_transform_to_scroll, 1),
        ("transform_to_potion", builtin_transform_to_potion, 1),
        ("random_fate", builtin_random_fate, 2),
        ("slumber", builtin_slumber, 1),
        ("range", builtin_range, -1),
        ("append", builtin_append, 2),
        ("remove", builtin_remove, 2),
        ("keys", builtin_keys, 1),
        ("values", builtin_values, 1),
        ("type_of", builtin_type_of, 1),

        # File I/O (Ancient Scrolls Theme)
        ("unroll_scroll", builtin_unroll_scroll, -1),
        ("seal_scroll", builtin_seal_scroll, 1),
        ("inscribe_scroll", builtin_inscribe_scroll, 2),
        ("chronicle_scroll", builtin_chronicle_scroll, 2),
        ("decipher_scroll", builtin_decipher_scroll, 1),
        ("read_runes", builtin_read_runes, -1),
        ("etch_runes", builtin_etch_runes, 2),
        ("divine_lines", builtin_divine_lines, 1),
        ("scroll_exists", builtin_scroll_exists, 1),
        ("banish_scroll", builtin_banish_scroll, 1),

        # MySQL (Oracle of Delphi Theme)
        ("awaken_oracle", builtin_awaken_oracle, -1),
        ("dismiss_oracle", builtin_dismiss_oracle, 1),
        ("consult_oracle", builtin_consult_oracle, -1),
        ("divine_one", builtin_divine_one, -1),
        ("decree_oracle", builtin_decree_oracle, -1),
        ("last_prophecy_id", builtin_last_prophecy_id, 1),
        ("begin_ritual", builtin_begin_ritual, 1),
        ("complete_ritual", builtin_complete_ritual, 1),
        ("abandon_ritual", builtin_abandon_ritual, 1),

        # Gameplay (Quest/Legend Theme)
        ("forge_hero", builtin_forge_hero, -1),
        ("forge_creature", builtin_forge_creature, -1),
        ("roll_destiny", builtin_roll_destiny, -1),
        ("inflict_wound", builtin_inflict_wound, 2),
        ("restore_vigor", builtin_restore_vigor, 2),
        ("bestow_artifact", builtin_bestow_artifact, 2),
        ("claim_loot", builtin_claim_loot, 1),
        ("check_fate", builtin_check_fate, 1),
        ("gain_experience", builtin_gain_experience, 2),
        ("saga_save", builtin_saga_save, 2),
        ("saga_load", builtin_saga_load, 1),
        ("encounter_chance", builtin_encounter_chance, 1),
        ("choose_fate", builtin_choose_fate, 1),
    ]

    for name, func, arity in builtins:
        environment.define(name, BuiltinFunction(name, func, arity))

    # Register M365/Entra ID built-ins
    from .m365 import register_m365_builtins
    register_m365_builtins(environment)
