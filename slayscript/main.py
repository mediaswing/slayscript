"""CLI entry point for SlayScript."""

import sys
import argparse
from . import __version__
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .builtins import register_builtins
from .errors import SlayScriptError


def run_file(filename: str, debug: bool = False):
    """Run a SlayScript file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Scroll not found: {filename}")
        sys.exit(1)
    except IOError as e:
        print(f"Failed to read scroll: {e}")
        sys.exit(1)

    run(source, debug)


def run(source: str, debug: bool = False):
    """Run SlayScript source code."""
    try:
        # Lexer
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        if debug:
            print("=== Tokens ===")
            for token in tokens:
                print(f"  {token}")
            print()

        # Parser
        parser = Parser(tokens)
        ast = parser.parse()

        if debug:
            print("=== AST ===")
            print_ast(ast)
            print()

        # Interpreter
        interpreter = Interpreter()
        register_builtins(interpreter.globals)

        result = interpreter.interpret(ast)

        if debug and result is not None:
            print(f"=== Result: {result} ===")

    except SlayScriptError as e:
        print(f"\n{e}")
        sys.exit(1)


def print_ast(node, indent=0):
    """Pretty-print an AST node (for debugging)."""
    prefix = "  " * indent
    name = type(node).__name__

    if hasattr(node, '__dict__'):
        print(f"{prefix}{name}:")
        for key, value in node.__dict__.items():
            if key in ('line', 'column'):
                continue
            if isinstance(value, list):
                print(f"{prefix}  {key}:")
                for item in value:
                    if hasattr(item, '__dict__'):
                        print_ast(item, indent + 2)
                    else:
                        print(f"{prefix}    {item}")
            elif hasattr(value, '__dict__') and not isinstance(value, type):
                print(f"{prefix}  {key}:")
                print_ast(value, indent + 2)
            else:
                print(f"{prefix}  {key}: {value}")
    else:
        print(f"{prefix}{node}")


def repl():
    """Start the interactive REPL."""
    print(f"SlayScript REPL v{__version__}")
    print("Cast spells, slay bugs.")
    print("Type 'exit' or 'quit' to leave the Hellmouth.\n")

    interpreter = Interpreter()
    register_builtins(interpreter.globals)

    # For multi-line input
    buffer = []
    indent_level = 0

    while True:
        try:
            prompt = "slay> " if not buffer else "....> "
            line = input(prompt)

            # Check for exit
            if line.strip() in ('exit', 'quit') and not buffer:
                print("The Slayer departs. Stay vigilant.")
                break

            # Handle empty line
            if not line.strip():
                if buffer:
                    # Empty line ends multi-line input
                    source = '\n'.join(buffer)
                    buffer = []
                    indent_level = 0

                    try:
                        execute_repl_input(interpreter, source)
                    except SlayScriptError as e:
                        print(f"{e}")
                continue

            # Check if line ends with colon (starts a block)
            if line.rstrip().endswith(':'):
                buffer.append(line)
                indent_level += 1
                continue

            # Check indentation for multi-line mode
            if buffer:
                stripped = line.lstrip()
                current_indent = len(line) - len(stripped)

                if current_indent > 0 or stripped.startswith(('otherwise', 'fate')):
                    buffer.append(line)
                    continue
                else:
                    # Dedent detected, execute buffer first
                    source = '\n'.join(buffer)
                    buffer = []
                    indent_level = 0

                    try:
                        execute_repl_input(interpreter, source)
                    except SlayScriptError as e:
                        print(f"{e}")

            # Single line execution
            try:
                execute_repl_input(interpreter, line)
            except SlayScriptError as e:
                print(f"{e}")

        except EOFError:
            print("\nThe Slayer departs. Stay vigilant.")
            break
        except KeyboardInterrupt:
            print("\n^C - Spell interrupted")
            buffer = []
            indent_level = 0


def execute_repl_input(interpreter, source: str):
    """Execute REPL input and print result if applicable."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    result = interpreter.interpret(ast)

    # Print result for expressions (but not for declarations/statements)
    if result is not None and len(ast.statements) == 1:
        from .ast_nodes import ExprStmt
        if isinstance(ast.statements[0], ExprStmt):
            print(format_value(result))


def format_value(value):
    """Format a value for display."""
    if value is None:
        return "void"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, list):
        items = ", ".join(format_value(v) for v in value)
        return f"tome [{items}]"
    if isinstance(value, dict):
        pairs = ", ".join(f"{format_value(k)}: {format_value(v)}" for k, v in value.items())
        return f"grimoire {{{pairs}}}"
    return str(value)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SlayScript - Cast spells, slay bugs.",
        prog="slayscript"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to a .slay file to execute"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Show debug output (tokens and AST)"
    )
    parser.add_argument(
        "-c", "--command",
        help="Execute a single command"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"SlayScript {__version__}"
    )

    args = parser.parse_args()

    if args.command:
        run(args.command, args.debug)
    elif args.file:
        run_file(args.file, args.debug)
    else:
        repl()


if __name__ == "__main__":
    main()
