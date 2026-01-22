"""AST node definitions for SlayScript."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


# ============ Expressions ============

@dataclass
class Literal(ASTNode):
    """Literal value (int, float, string, bool, void)."""
    value: Any = None


@dataclass
class Identifier(ASTNode):
    """Variable reference."""
    name: str = ""


@dataclass
class BinaryOp(ASTNode):
    """Binary operation (arithmetic, comparison, logical)."""
    left: ASTNode = None
    operator: str = ""
    right: ASTNode = None


@dataclass
class UnaryOp(ASTNode):
    """Unary operation (not, negation)."""
    operator: str = ""
    operand: ASTNode = None


@dataclass
class TomeExpr(ASTNode):
    """List literal: tome [1, 2, 3]."""
    elements: list = field(default_factory=list)


@dataclass
class GrimoireExpr(ASTNode):
    """Dict literal: grimoire {"key": "value"}."""
    pairs: list = field(default_factory=list)  # List of (key, value) tuples


@dataclass
class IndexExpr(ASTNode):
    """Index access: collection[index]."""
    collection: ASTNode = None
    index: ASTNode = None


@dataclass
class CallExpr(ASTNode):
    """Function call: funcname(args)."""
    callee: ASTNode = None
    arguments: list = field(default_factory=list)


@dataclass
class MemberExpr(ASTNode):
    """Member access: object.member."""
    object: ASTNode = None
    member: str = ""


# ============ Statements ============

@dataclass
class Program(ASTNode):
    """Root node containing all statements."""
    statements: list = field(default_factory=list)


@dataclass
class VarDecl(ASTNode):
    """Variable declaration: conjure/summon x as value."""
    name: str = ""
    value: ASTNode = None
    type_hint: Optional[str] = None  # scroll, rune, potion, etc.
    is_const: bool = False


@dataclass
class VarAssign(ASTNode):
    """Variable reassignment: transmute x as value."""
    name: str = ""
    value: ASTNode = None


@dataclass
class IndexAssign(ASTNode):
    """Index assignment: transmute collection[index] as value."""
    collection: ASTNode = None
    index: ASTNode = None
    value: ASTNode = None


@dataclass
class VarDelete(ASTNode):
    """Variable deletion: vanquish x."""
    name: str = ""


@dataclass
class SpellDecl(ASTNode):
    """Function declaration: spell funcname(params):."""
    name: str = ""
    params: list = field(default_factory=list)
    body: list = field(default_factory=list)
    is_incantation: bool = False  # Auto-speaks when called


@dataclass
class CastStmt(ASTNode):
    """Return statement: cast value."""
    value: Optional[ASTNode] = None


@dataclass
class IfStmt(ASTNode):
    """If statement: prophecy reveals condition:."""
    condition: ASTNode = None
    then_branch: list = field(default_factory=list)
    elif_branches: list = field(default_factory=list)  # List of (condition, body) tuples
    else_branch: Optional[list] = None


@dataclass
class WhileStmt(ASTNode):
    """While loop: patrol until condition:."""
    condition: ASTNode = None
    body: list = field(default_factory=list)


@dataclass
class ForStmt(ASTNode):
    """For loop: hunt each item in collection:."""
    variable: str = ""
    iterable: ASTNode = None
    body: list = field(default_factory=list)


@dataclass
class BreakStmt(ASTNode):
    """Break statement."""
    pass


@dataclass
class ContinueStmt(ASTNode):
    """Continue statement."""
    pass


@dataclass
class ExprStmt(ASTNode):
    """Expression statement (function call, etc.)."""
    expression: ASTNode = None
