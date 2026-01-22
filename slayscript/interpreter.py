"""AST interpreter for SlayScript."""

from typing import Any, List
from .ast_nodes import (
    Program, Literal, Identifier, BinaryOp, UnaryOp,
    TomeExpr, GrimoireExpr, IndexExpr, CallExpr, MemberExpr,
    VarDecl, VarAssign, IndexAssign, VarDelete,
    SpellDecl, CastStmt, IfStmt, WhileStmt, ForStmt,
    BreakStmt, ContinueStmt, ExprStmt
)
from .environment import Environment, SlayFunction, Callable
from .errors import (
    ForbiddenMagic, SlayerInterrupt, PatrolContinue, SpellReturn,
    UnknownIncantation
)


class Interpreter:
    """Evaluates SlayScript AST."""

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.tts_engine = None  # Lazy init for TTS

    def interpret(self, program: Program) -> Any:
        """Interpret a program."""
        result = None
        for statement in program.statements:
            result = self.execute(statement)
        return result

    def execute(self, node) -> Any:
        """Execute a single AST node."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise ForbiddenMagic(f"No visitor for {type(node).__name__}", node.line, node.column)

    def execute_block(self, statements: List, env: Environment) -> Any:
        """Execute a block of statements in a given environment."""
        previous = self.environment
        result = None
        try:
            self.environment = env
            for stmt in statements:
                result = self.execute(stmt)
        finally:
            self.environment = previous
        return result

    # ============ Statement Visitors ============

    def visit_Program(self, node: Program) -> Any:
        result = None
        for stmt in node.statements:
            result = self.execute(stmt)
        return result

    def visit_VarDecl(self, node: VarDecl) -> Any:
        value = self.evaluate(node.value)
        self.environment.define(node.name, value, is_const=node.is_const)
        return value

    def visit_VarAssign(self, node: VarAssign) -> Any:
        value = self.evaluate(node.value)
        self.environment.assign(node.name, value, node.line, node.column)
        return value

    def visit_IndexAssign(self, node: IndexAssign) -> Any:
        collection = self.evaluate(node.collection)
        index = self.evaluate(node.index)
        value = self.evaluate(node.value)

        if isinstance(collection, list):
            if not isinstance(index, int):
                raise ForbiddenMagic("Tome index must be a rune (integer)", node.line, node.column)
            collection[index] = value
        elif isinstance(collection, dict):
            collection[index] = value
        else:
            raise ForbiddenMagic("Cannot index into this type", node.line, node.column)

        return value

    def visit_VarDelete(self, node: VarDelete) -> Any:
        self.environment.delete(node.name, node.line, node.column)
        return None

    def visit_SpellDecl(self, node: SpellDecl) -> Any:
        func = SlayFunction(node, self.environment, is_incantation=node.is_incantation)
        self.environment.define(node.name, func)
        return func

    def visit_CastStmt(self, node: CastStmt) -> Any:
        value = None
        if node.value is not None:
            value = self.evaluate(node.value)
        raise SpellReturn(value)

    def visit_IfStmt(self, node: IfStmt) -> Any:
        if self.is_truthy(self.evaluate(node.condition)):
            return self.execute_block(node.then_branch, Environment(self.environment))

        for elif_cond, elif_body in node.elif_branches:
            if self.is_truthy(self.evaluate(elif_cond)):
                return self.execute_block(elif_body, Environment(self.environment))

        if node.else_branch is not None:
            return self.execute_block(node.else_branch, Environment(self.environment))

        return None

    def visit_WhileStmt(self, node: WhileStmt) -> Any:
        result = None
        # Note: "patrol until" means "while NOT condition" - loop while condition is false
        while not self.is_truthy(self.evaluate(node.condition)):
            try:
                result = self.execute_block(node.body, Environment(self.environment))
            except SlayerInterrupt:
                break
            except PatrolContinue:
                continue
        return result

    def visit_ForStmt(self, node: ForStmt) -> Any:
        iterable = self.evaluate(node.iterable)
        result = None

        if not hasattr(iterable, '__iter__'):
            raise ForbiddenMagic("Cannot hunt through non-iterable", node.line, node.column)

        for item in iterable:
            env = Environment(self.environment)
            env.define(node.variable, item)
            try:
                result = self.execute_block(node.body, env)
            except SlayerInterrupt:
                break
            except PatrolContinue:
                continue

        return result

    def visit_BreakStmt(self, node: BreakStmt) -> Any:
        raise SlayerInterrupt()

    def visit_ContinueStmt(self, node: ContinueStmt) -> Any:
        raise PatrolContinue()

    def visit_ExprStmt(self, node: ExprStmt) -> Any:
        return self.evaluate(node.expression)

    # ============ Expression Visitors ============

    def evaluate(self, node) -> Any:
        """Evaluate an expression node."""
        return self.execute(node)

    def visit_Literal(self, node: Literal) -> Any:
        return node.value

    def visit_Identifier(self, node: Identifier) -> Any:
        return self.environment.get(node.name, node.line, node.column)

    def visit_BinaryOp(self, node: BinaryOp) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        op = node.operator

        # Arithmetic
        if op == "+":
            return self.add(left, right, node)
        if op == "-":
            return self.check_numbers(left, right, node) and (left - right)
        if op == "*":
            return self.multiply(left, right, node)
        if op == "/":
            self.check_numbers(left, right, node)
            if right == 0:
                raise ForbiddenMagic("Division by void is forbidden", node.line, node.column)
            return left / right
        if op == "%":
            self.check_numbers(left, right, node)
            return left % right
        if op == "**":
            self.check_numbers(left, right, node)
            return left ** right

        # Comparison
        if op == "is":
            return left == right
        if op == "isnt":
            return left != right
        if op == "exceeds":
            return left > right
        if op == "under":
            return left < right
        if op == "atleast":
            return left >= right
        if op == "atmost":
            return left <= right

        # Logical
        if op == "and":
            return self.is_truthy(left) and self.is_truthy(right)
        if op == "or":
            return self.is_truthy(left) or self.is_truthy(right)

        raise ForbiddenMagic(f"Unknown operator '{op}'", node.line, node.column)

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        operand = self.evaluate(node.operand)

        if node.operator == "-":
            if not isinstance(operand, (int, float)):
                raise ForbiddenMagic("Negation requires a number", node.line, node.column)
            return -operand

        if node.operator == "not":
            return not self.is_truthy(operand)

        raise ForbiddenMagic(f"Unknown unary operator '{node.operator}'", node.line, node.column)

    def visit_TomeExpr(self, node: TomeExpr) -> Any:
        return [self.evaluate(elem) for elem in node.elements]

    def visit_GrimoireExpr(self, node: GrimoireExpr) -> Any:
        result = {}
        for key_expr, value_expr in node.pairs:
            key = self.evaluate(key_expr)
            value = self.evaluate(value_expr)
            result[key] = value
        return result

    def visit_IndexExpr(self, node: IndexExpr) -> Any:
        collection = self.evaluate(node.collection)
        index = self.evaluate(node.index)

        if isinstance(collection, list):
            if not isinstance(index, int):
                raise ForbiddenMagic("Tome index must be a rune (integer)", node.line, node.column)
            if index < 0 or index >= len(collection):
                raise ForbiddenMagic(f"Tome index {index} out of range", node.line, node.column)
            return collection[index]

        if isinstance(collection, dict):
            if index not in collection:
                raise ForbiddenMagic(f"Key '{index}' not found in grimoire", node.line, node.column)
            return collection[index]

        if isinstance(collection, str):
            if not isinstance(index, int):
                raise ForbiddenMagic("Scroll index must be a rune (integer)", node.line, node.column)
            if index < 0 or index >= len(collection):
                raise ForbiddenMagic(f"Scroll index {index} out of range", node.line, node.column)
            return collection[index]

        raise ForbiddenMagic("Cannot index into this type", node.line, node.column)

    def visit_CallExpr(self, node: CallExpr) -> Any:
        callee = self.evaluate(node.callee)
        arguments = [self.evaluate(arg) for arg in node.arguments]

        if not isinstance(callee, Callable):
            raise ForbiddenMagic("Can only invoke spells and incantations", node.line, node.column)

        # Check arity if not variable
        if callee.arity() != -1 and len(arguments) != callee.arity():
            raise ForbiddenMagic(
                f"Expected {callee.arity()} arguments but got {len(arguments)}",
                node.line, node.column
            )

        try:
            result = callee.call(self, arguments)

            # If it's an incantation, speak the result
            if isinstance(callee, SlayFunction) and callee.is_incantation:
                if result is not None:
                    self.speak(str(result))

            return result
        except SpellReturn as ret:
            result = ret.value

            # If it's an incantation, speak the result
            if isinstance(callee, SlayFunction) and callee.is_incantation:
                if result is not None:
                    self.speak(str(result))

            return result

    def visit_MemberExpr(self, node: MemberExpr) -> Any:
        obj = self.evaluate(node.object)

        # Handle dict member access like object.key
        if isinstance(obj, dict) and node.member in obj:
            return obj[node.member]

        raise ForbiddenMagic(f"No such member '{node.member}'", node.line, node.column)

    # ============ Helper Methods ============

    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True

    def check_numbers(self, left, right, node) -> bool:
        """Verify both operands are numbers."""
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True
        raise ForbiddenMagic(
            "Arithmetic operations require numbers",
            node.line, node.column
        )

    def add(self, left, right, node):
        """Handle addition (numbers or string concatenation)."""
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        if isinstance(left, list) and isinstance(right, list):
            return left + right
        raise ForbiddenMagic("Invalid operands for addition", node.line, node.column)

    def multiply(self, left, right, node):
        """Handle multiplication."""
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left * right
        if isinstance(left, str) and isinstance(right, int):
            return left * right
        if isinstance(left, int) and isinstance(right, str):
            return left * right
        if isinstance(left, list) and isinstance(right, int):
            return left * right
        raise ForbiddenMagic("Invalid operands for multiplication", node.line, node.column)

    def speak(self, text: str):
        """Speak text using TTS (for incantations)."""
        if self.tts_engine is None:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
            except Exception:
                # TTS not available, just print
                print(f"[Speaking]: {text}")
                return

        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception:
            print(f"[Speaking]: {text}")
