"""Token definitions for SlayScript."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords - Variable declarations
    CONJURE = auto()      # conjure x as 5
    SUMMON = auto()       # summon name as "Buffy"
    TRANSMUTE = auto()    # transmute x as x + 1
    CONST = auto()        # const prophecy PI as 3.14
    PROPHECY = auto()     # prophecy (used in const and if)
    VANQUISH = auto()     # vanquish x (delete)
    AS = auto()           # assignment keyword

    # Data type keywords
    SCROLL = auto()       # string
    RUNE = auto()         # integer
    POTION = auto()       # float
    CHARM = auto()        # boolean
    TOME = auto()         # list
    GRIMOIRE = auto()     # dict
    VOID = auto()         # null
    TRUE = auto()         # charm true
    FALSE = auto()        # charm false

    # Function keywords
    SPELL = auto()        # spell funcname():
    INCANTATION = auto()  # incantation funcname(): (auto-speaks)
    CAST = auto()         # cast value (return)

    # Control flow keywords
    REVEALS = auto()      # prophecy reveals (if)
    OTHERWISE = auto()    # otherwise prophecy (elif)
    FATE = auto()         # fate decrees (else)
    DECREES = auto()      # fate decrees
    PATROL = auto()       # patrol until (while)
    UNTIL = auto()        # patrol until
    HUNT = auto()         # hunt each (for)
    EACH = auto()         # hunt each
    IN = auto()           # in
    BREAK = auto()        # break loop
    CONTINUE = auto()     # continue loop

    # Comparison operators (keywords)
    IS = auto()           # ==
    ISNT = auto()         # !=
    EXCEEDS = auto()      # >
    UNDER = auto()        # <
    ATLEAST = auto()      # >=
    ATMOST = auto()       # <=

    # Logical operators
    AND = auto()
    OR = auto()
    NOT = auto()

    # Arithmetic operators
    PLUS = auto()         # +
    MINUS = auto()        # -
    STAR = auto()         # *
    SLASH = auto()        # /
    PERCENT = auto()      # %
    POWER = auto()        # **

    # Delimiters
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    COMMA = auto()        # ,
    COLON = auto()        # :
    DOT = auto()          # .

    # Special tokens
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

    # Comment (handled by lexer, not passed to parser)
    COMMENT = auto()


@dataclass
class Token:
    """A token produced by the lexer."""
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"


# Keyword mapping
KEYWORDS = {
    # Variable declarations
    "conjure": TokenType.CONJURE,
    "summon": TokenType.SUMMON,
    "transmute": TokenType.TRANSMUTE,
    "const": TokenType.CONST,
    "prophecy": TokenType.PROPHECY,
    "vanquish": TokenType.VANQUISH,
    "as": TokenType.AS,

    # Data types
    "scroll": TokenType.SCROLL,
    "rune": TokenType.RUNE,
    "potion": TokenType.POTION,
    "charm": TokenType.CHARM,
    "tome": TokenType.TOME,
    "grimoire": TokenType.GRIMOIRE,
    "void": TokenType.VOID,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,

    # Functions
    "spell": TokenType.SPELL,
    "incantation": TokenType.INCANTATION,
    "cast": TokenType.CAST,

    # Control flow
    "reveals": TokenType.REVEALS,
    "otherwise": TokenType.OTHERWISE,
    "fate": TokenType.FATE,
    "decrees": TokenType.DECREES,
    "patrol": TokenType.PATROL,
    "until": TokenType.UNTIL,
    "hunt": TokenType.HUNT,
    "each": TokenType.EACH,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,

    # Comparison
    "is": TokenType.IS,
    "isnt": TokenType.ISNT,
    "exceeds": TokenType.EXCEEDS,
    "under": TokenType.UNDER,
    "atleast": TokenType.ATLEAST,
    "atmost": TokenType.ATMOST,

    # Logical
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}
