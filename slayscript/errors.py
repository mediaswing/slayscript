"""Themed exception classes for SlayScript."""


class SlayScriptError(Exception):
    """Base exception for all SlayScript errors."""

    def __init__(self, message: str, line: int = None, column: int = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())

    def format_message(self) -> str:
        location = ""
        if self.line is not None:
            location = f" at line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"
        return f"{self.message}{location}"


class SpellMiscast(SlayScriptError):
    """Syntax error - the spell was written incorrectly."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Spell Miscast! {base}"


class DarkMagicDetected(SlayScriptError):
    """Lexer error - invalid characters or tokens."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Dark Magic Detected! {base}"


class UnknownIncantation(SlayScriptError):
    """Name error - undefined variable or function."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Unknown Incantation! {base}"


class ForbiddenMagic(SlayScriptError):
    """Type error - invalid operation for type."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Forbidden Magic! {base}"


class CursedScroll(SlayScriptError):
    """Value error - invalid value."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Cursed Scroll! {base}"


class ProphecyViolation(SlayScriptError):
    """Attempted to modify a constant."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Prophecy Violation! {base}"


class PortalFailure(SlayScriptError):
    """Network/connection error."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Portal Failure! {base}"


class VoiceSilenced(SlayScriptError):
    """Text-to-speech error."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Voice Silenced! {base}"


class SlayerInterrupt(SlayScriptError):
    """Break statement signal (internal use)."""
    pass


class PatrolContinue(SlayScriptError):
    """Continue statement signal (internal use)."""
    pass


class SpellReturn(SlayScriptError):
    """Return statement signal (internal use)."""

    def __init__(self, value=None):
        self.value = value
        super().__init__("Return from spell")
