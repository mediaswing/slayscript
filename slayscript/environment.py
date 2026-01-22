"""Environment and scope management for SlayScript."""

from typing import Any, Dict, Optional
from .errors import UnknownIncantation, ProphecyViolation


class Environment:
    """Manages variable scopes and symbol lookup."""

    def __init__(self, parent: Optional["Environment"] = None):
        self.values: Dict[str, Any] = {}
        self.constants: set = set()  # Names that cannot be reassigned
        self.parent = parent

    def define(self, name: str, value: Any, is_const: bool = False):
        """Define a new variable in the current scope."""
        self.values[name] = value
        if is_const:
            self.constants.add(name)

    def get(self, name: str, line: int = None, column: int = None) -> Any:
        """Get a variable's value, searching up the scope chain."""
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name, line, column)
        raise UnknownIncantation(f"Undefined variable '{name}'", line, column)

    def assign(self, name: str, value: Any, line: int = None, column: int = None):
        """Assign a new value to an existing variable."""
        # Check if it's a constant in the current scope
        if name in self.constants:
            raise ProphecyViolation(
                f"Cannot modify the prophecy '{name}' - it is constant",
                line, column
            )

        if name in self.values:
            self.values[name] = value
            return

        # Check parent scopes
        if self.parent is not None:
            # Check if parent has it as a constant
            if self.parent.is_constant(name):
                raise ProphecyViolation(
                    f"Cannot modify the prophecy '{name}' - it is constant",
                    line, column
                )
            self.parent.assign(name, value, line, column)
            return

        raise UnknownIncantation(f"Undefined variable '{name}'", line, column)

    def delete(self, name: str, line: int = None, column: int = None):
        """Delete a variable from the current scope."""
        if name in self.constants:
            raise ProphecyViolation(
                f"Cannot vanquish the prophecy '{name}' - it is constant",
                line, column
            )

        if name in self.values:
            del self.values[name]
            return

        if self.parent is not None:
            if self.parent.is_constant(name):
                raise ProphecyViolation(
                    f"Cannot vanquish the prophecy '{name}' - it is constant",
                    line, column
                )
            self.parent.delete(name, line, column)
            return

        raise UnknownIncantation(f"Undefined variable '{name}'", line, column)

    def is_constant(self, name: str) -> bool:
        """Check if a name is a constant anywhere in the scope chain."""
        if name in self.constants:
            return True
        if self.parent is not None:
            return self.parent.is_constant(name)
        return False

    def exists(self, name: str) -> bool:
        """Check if a variable exists in any scope."""
        if name in self.values:
            return True
        if self.parent is not None:
            return self.parent.exists(name)
        return False

    def exists_local(self, name: str) -> bool:
        """Check if a variable exists in the current (local) scope only."""
        return name in self.values


class Callable:
    """Base class for callable objects (functions)."""

    def arity(self) -> int:
        """Return the number of arguments the callable expects."""
        raise NotImplementedError

    def call(self, interpreter, arguments: list):
        """Execute the callable with the given arguments."""
        raise NotImplementedError


class SlayFunction(Callable):
    """A user-defined SlayScript function (spell/incantation)."""

    def __init__(self, declaration, closure: Environment, is_incantation: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_incantation = is_incantation

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments: list):
        # Create new environment for function scope
        env = Environment(self.closure)

        # Bind parameters to arguments
        for param, arg in zip(self.declaration.params, arguments):
            env.define(param, arg)

        # Execute function body
        return interpreter.execute_block(self.declaration.body, env)

    def __repr__(self):
        kind = "incantation" if self.is_incantation else "spell"
        return f"<{kind} {self.declaration.name}>"


class BuiltinFunction(Callable):
    """A built-in SlayScript function."""

    def __init__(self, name: str, func, arity_count: int = -1):
        self.name = name
        self.func = func
        self._arity = arity_count  # -1 means variable arity

    def arity(self) -> int:
        return self._arity

    def call(self, interpreter, arguments: list):
        return self.func(interpreter, arguments)

    def __repr__(self):
        return f"<builtin {self.name}>"
