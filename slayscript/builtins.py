"""Built-in functions for SlayScript."""

import socket
import random
import time
import webbrowser
import os
from typing import Any, List
from .environment import BuiltinFunction
from .errors import ForbiddenMagic, PortalFailure, VoiceSilenced

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
    ]

    for name, func, arity in builtins:
        environment.define(name, BuiltinFunction(name, func, arity))

    # Register M365/Entra ID built-ins
    from .m365 import register_m365_builtins
    register_m365_builtins(environment)
