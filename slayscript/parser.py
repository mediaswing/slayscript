"""Recursive descent parser for SlayScript."""

from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import (
    Program, Literal, Identifier, BinaryOp, UnaryOp,
    TomeExpr, GrimoireExpr, IndexExpr, CallExpr, MemberExpr,
    VarDecl, VarAssign, IndexAssign, VarDelete,
    SpellDecl, CastStmt, IfStmt, WhileStmt, ForStmt,
    BreakStmt, ContinueStmt, ExprStmt
)
from .errors import SpellMiscast


class Parser:
    """Parses tokens into an AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        """Parse the token stream into a Program AST."""
        statements = []
        while not self.is_at_end():
            self.skip_newlines()
            if not self.is_at_end():
                stmt = self.statement()
                if stmt is not None:
                    statements.append(stmt)
        return Program(statements=statements)

    def statement(self):
        """Parse a single statement."""
        self.skip_newlines()

        if self.check(TokenType.CONJURE) or self.check(TokenType.SUMMON):
            return self.var_declaration()
        if self.check(TokenType.CONST):
            return self.const_declaration()
        if self.check(TokenType.TRANSMUTE):
            return self.var_assignment()
        if self.check(TokenType.VANQUISH):
            return self.var_delete()
        if self.check(TokenType.SPELL) or self.check(TokenType.INCANTATION):
            return self.spell_declaration()
        if self.check(TokenType.CAST):
            return self.cast_statement()
        if self.check(TokenType.PROPHECY):
            return self.if_statement()
        if self.check(TokenType.PATROL):
            return self.while_statement()
        if self.check(TokenType.HUNT):
            return self.for_statement()
        if self.check(TokenType.BREAK):
            return self.break_statement()
        if self.check(TokenType.CONTINUE):
            return self.continue_statement()

        return self.expression_statement()

    def var_declaration(self):
        """Parse: conjure/summon name as value or conjure name as type value."""
        token = self.advance()  # CONJURE or SUMMON
        line, col = token.line, token.column

        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value

        self.consume(TokenType.AS, "Expected 'as' after variable name")

        # Check for type hint
        type_hint = None
        if self.check_type_keyword():
            type_hint = self.advance().value

        value = self.expression()

        return VarDecl(name=name, value=value, type_hint=type_hint, is_const=False, line=line, column=col)

    def const_declaration(self):
        """Parse: const prophecy NAME as value."""
        token = self.advance()  # CONST
        line, col = token.line, token.column

        self.consume(TokenType.PROPHECY, "Expected 'prophecy' after 'const'")

        name_token = self.consume(TokenType.IDENTIFIER, "Expected constant name")
        name = name_token.value

        self.consume(TokenType.AS, "Expected 'as' after constant name")

        value = self.expression()

        return VarDecl(name=name, value=value, type_hint=None, is_const=True, line=line, column=col)

    def var_assignment(self):
        """Parse: transmute name as value or transmute collection[index] as value."""
        token = self.advance()  # TRANSMUTE
        line, col = token.line, token.column

        # Could be simple name or indexed access
        target = self.primary()

        self.consume(TokenType.AS, "Expected 'as' after assignment target")
        value = self.expression()

        if isinstance(target, Identifier):
            return VarAssign(name=target.name, value=value, line=line, column=col)
        elif isinstance(target, IndexExpr):
            return IndexAssign(
                collection=target.collection,
                index=target.index,
                value=value,
                line=line,
                column=col
            )
        else:
            raise SpellMiscast("Invalid assignment target", line, col)

    def var_delete(self):
        """Parse: vanquish name."""
        token = self.advance()  # VANQUISH
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name to vanquish")
        return VarDelete(name=name_token.value, line=token.line, column=token.column)

    def spell_declaration(self):
        """Parse: spell/incantation name(params) { body }."""
        token = self.advance()  # SPELL or INCANTATION
        is_incantation = token.type == TokenType.INCANTATION
        line, col = token.line, token.column

        name_token = self.consume(TokenType.IDENTIFIER, "Expected spell name")
        name = name_token.value

        self.consume(TokenType.LPAREN, "Expected '(' after spell name")

        # Parse parameters
        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        body = self.block()

        return SpellDecl(
            name=name,
            params=params,
            body=body,
            is_incantation=is_incantation,
            line=line,
            column=col
        )

    def cast_statement(self):
        """Parse: cast value."""
        token = self.advance()  # CAST
        value = None
        if not self.check(TokenType.NEWLINE) and not self.check(TokenType.EOF) and not self.check(TokenType.RBRACE):
            value = self.expression()
        return CastStmt(value=value, line=token.line, column=token.column)

    def if_statement(self):
        """Parse: prophecy reveals condition { body }."""
        token = self.advance()  # PROPHECY
        line, col = token.line, token.column

        self.consume(TokenType.REVEALS, "Expected 'reveals' after 'prophecy'")
        condition = self.expression()

        then_branch = self.block()

        elif_branches = []
        else_branch = None

        # Check for otherwise/fate
        while True:
            self.skip_newlines()
            if self.check(TokenType.OTHERWISE):
                self.advance()  # OTHERWISE
                self.consume(TokenType.PROPHECY, "Expected 'prophecy' after 'otherwise'")
                elif_cond = self.expression()
                elif_body = self.block()
                elif_branches.append((elif_cond, elif_body))
            elif self.check(TokenType.FATE):
                self.advance()  # FATE
                self.consume(TokenType.DECREES, "Expected 'decrees' after 'fate'")
                else_branch = self.block()
                break
            else:
                break

        return IfStmt(
            condition=condition,
            then_branch=then_branch,
            elif_branches=elif_branches,
            else_branch=else_branch,
            line=line,
            column=col
        )

    def while_statement(self):
        """Parse: patrol until condition { body }."""
        token = self.advance()  # PATROL
        line, col = token.line, token.column

        self.consume(TokenType.UNTIL, "Expected 'until' after 'patrol'")
        condition = self.expression()

        body = self.block()

        return WhileStmt(condition=condition, body=body, line=line, column=col)

    def for_statement(self):
        """Parse: hunt each item in collection { body }."""
        token = self.advance()  # HUNT
        line, col = token.line, token.column

        self.consume(TokenType.EACH, "Expected 'each' after 'hunt'")
        var_token = self.consume(TokenType.IDENTIFIER, "Expected loop variable")
        self.consume(TokenType.IN, "Expected 'in' after loop variable")
        iterable = self.expression()

        body = self.block()

        return ForStmt(
            variable=var_token.value,
            iterable=iterable,
            body=body,
            line=line,
            column=col
        )

    def break_statement(self):
        """Parse: break."""
        token = self.advance()  # BREAK
        return BreakStmt(line=token.line, column=token.column)

    def continue_statement(self):
        """Parse: continue."""
        token = self.advance()  # CONTINUE
        return ContinueStmt(line=token.line, column=token.column)

    def expression_statement(self):
        """Parse an expression as a statement."""
        expr = self.expression()
        return ExprStmt(expression=expr, line=expr.line, column=expr.column)

    def block(self):
        """Parse a brace-delimited block of statements."""
        statements = []

        self.skip_newlines()
        self.consume(TokenType.LBRACE, "Expected '{' to begin block")

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            self.skip_newlines()
            if self.check(TokenType.RBRACE):
                break
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.RBRACE, "Expected '}' to end block")

        return statements

    # ============ Expression Parsing ============

    def expression(self):
        """Parse an expression (lowest precedence)."""
        return self.or_expr()

    def or_expr(self):
        """Parse: expr or expr."""
        left = self.and_expr()

        while self.match(TokenType.OR):
            op = "or"
            right = self.and_expr()
            left = BinaryOp(left=left, operator=op, right=right, line=left.line, column=left.column)

        return left

    def and_expr(self):
        """Parse: expr and expr."""
        left = self.not_expr()

        while self.match(TokenType.AND):
            op = "and"
            right = self.not_expr()
            left = BinaryOp(left=left, operator=op, right=right, line=left.line, column=left.column)

        return left

    def not_expr(self):
        """Parse: not expr."""
        if self.match(TokenType.NOT):
            token = self.previous()
            operand = self.not_expr()
            return UnaryOp(operator="not", operand=operand, line=token.line, column=token.column)
        return self.comparison()

    def comparison(self):
        """Parse comparison operators."""
        left = self.term()

        comparison_ops = {
            TokenType.IS: "is",
            TokenType.ISNT: "isnt",
            TokenType.EXCEEDS: "exceeds",
            TokenType.UNDER: "under",
            TokenType.ATLEAST: "atleast",
            TokenType.ATMOST: "atmost",
        }

        while True:
            matched = False
            for token_type, op_str in comparison_ops.items():
                if self.match(token_type):
                    right = self.term()
                    left = BinaryOp(left=left, operator=op_str, right=right, line=left.line, column=left.column)
                    matched = True
                    break
            if not matched:
                break

        return left

    def term(self):
        """Parse: expr + expr, expr - expr."""
        left = self.factor()

        while True:
            if self.match(TokenType.PLUS):
                right = self.factor()
                left = BinaryOp(left=left, operator="+", right=right, line=left.line, column=left.column)
            elif self.match(TokenType.MINUS):
                right = self.factor()
                left = BinaryOp(left=left, operator="-", right=right, line=left.line, column=left.column)
            else:
                break

        return left

    def factor(self):
        """Parse: expr * expr, expr / expr, expr % expr."""
        left = self.power()

        while True:
            if self.match(TokenType.STAR):
                right = self.power()
                left = BinaryOp(left=left, operator="*", right=right, line=left.line, column=left.column)
            elif self.match(TokenType.SLASH):
                right = self.power()
                left = BinaryOp(left=left, operator="/", right=right, line=left.line, column=left.column)
            elif self.match(TokenType.PERCENT):
                right = self.power()
                left = BinaryOp(left=left, operator="%", right=right, line=left.line, column=left.column)
            else:
                break

        return left

    def power(self):
        """Parse: expr ** expr (right-associative)."""
        left = self.unary()

        if self.match(TokenType.POWER):
            right = self.power()  # Right associative
            left = BinaryOp(left=left, operator="**", right=right, line=left.line, column=left.column)

        return left

    def unary(self):
        """Parse: -expr."""
        if self.match(TokenType.MINUS):
            token = self.previous()
            operand = self.unary()
            return UnaryOp(operator="-", operand=operand, line=token.line, column=token.column)
        return self.call()

    def call(self):
        """Parse function calls and index access."""
        expr = self.primary()

        while True:
            if self.match(TokenType.LPAREN):
                # Function call
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.expression())
                    while self.match(TokenType.COMMA):
                        args.append(self.expression())
                self.consume(TokenType.RPAREN, "Expected ')' after arguments")
                expr = CallExpr(callee=expr, arguments=args, line=expr.line, column=expr.column)
            elif self.match(TokenType.LBRACKET):
                # Index access
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexExpr(collection=expr, index=index, line=expr.line, column=expr.column)
            elif self.match(TokenType.DOT):
                # Member access
                member = self.consume(TokenType.IDENTIFIER, "Expected member name after '.'")
                expr = MemberExpr(object=expr, member=member.value, line=expr.line, column=expr.column)
            else:
                break

        return expr

    def primary(self):
        """Parse primary expressions (literals, identifiers, grouping)."""
        token = self.peek()

        # Literals
        if self.match(TokenType.INTEGER):
            return Literal(value=self.previous().value, line=token.line, column=token.column)
        if self.match(TokenType.FLOAT):
            return Literal(value=self.previous().value, line=token.line, column=token.column)
        if self.match(TokenType.STRING):
            return Literal(value=self.previous().value, line=token.line, column=token.column)
        if self.match(TokenType.TRUE):
            return Literal(value=True, line=token.line, column=token.column)
        if self.match(TokenType.FALSE):
            return Literal(value=False, line=token.line, column=token.column)
        if self.match(TokenType.VOID):
            return Literal(value=None, line=token.line, column=token.column)

        # Type-annotated literals
        if self.match(TokenType.SCROLL):
            val = self.consume(TokenType.STRING, "Expected string after 'scroll'")
            return Literal(value=val.value, line=token.line, column=token.column)
        if self.match(TokenType.RUNE):
            val = self.consume(TokenType.INTEGER, "Expected integer after 'rune'")
            return Literal(value=val.value, line=token.line, column=token.column)
        if self.match(TokenType.POTION):
            if self.check(TokenType.FLOAT):
                val = self.advance()
            else:
                val = self.consume(TokenType.INTEGER, "Expected number after 'potion'")
            return Literal(value=float(val.value), line=token.line, column=token.column)
        if self.match(TokenType.CHARM):
            if self.match(TokenType.TRUE):
                return Literal(value=True, line=token.line, column=token.column)
            elif self.match(TokenType.FALSE):
                return Literal(value=False, line=token.line, column=token.column)
            else:
                raise SpellMiscast("Expected 'true' or 'false' after 'charm'", token.line, token.column)

        # Tome (list)
        if self.match(TokenType.TOME):
            return self.tome_literal(token)

        # Grimoire (dict) or just [ for list literal
        if self.match(TokenType.GRIMOIRE):
            return self.grimoire_literal(token)

        # List literal without tome keyword
        if self.match(TokenType.LBRACKET):
            return self.list_literal(token)

        # Dict literal without grimoire keyword
        if self.match(TokenType.LBRACE):
            return self.dict_literal(token)

        # Identifier
        if self.match(TokenType.IDENTIFIER):
            return Identifier(name=self.previous().value, line=token.line, column=token.column)

        # Grouping
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        raise SpellMiscast(f"Unexpected token: {token.type.name}", token.line, token.column)

    def tome_literal(self, token):
        """Parse: tome [elements]."""
        self.consume(TokenType.LBRACKET, "Expected '[' after 'tome'")
        return self.list_literal(token)

    def list_literal(self, token):
        """Parse: [elements]."""
        elements = []
        if not self.check(TokenType.RBRACKET):
            elements.append(self.expression())
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACKET):
                    break  # Allow trailing comma
                elements.append(self.expression())
        self.consume(TokenType.RBRACKET, "Expected ']' after list elements")
        return TomeExpr(elements=elements, line=token.line, column=token.column)

    def grimoire_literal(self, token):
        """Parse: grimoire {pairs}."""
        self.consume(TokenType.LBRACE, "Expected '{' after 'grimoire'")
        return self.dict_literal(token)

    def dict_literal(self, token):
        """Parse: {key: value, ...}."""
        pairs = []
        if not self.check(TokenType.RBRACE):
            key = self.expression()
            self.consume(TokenType.COLON, "Expected ':' after dictionary key")
            value = self.expression()
            pairs.append((key, value))
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACE):
                    break  # Allow trailing comma
                key = self.expression()
                self.consume(TokenType.COLON, "Expected ':' after dictionary key")
                value = self.expression()
                pairs.append((key, value))
        self.consume(TokenType.RBRACE, "Expected '}' after dictionary")
        return GrimoireExpr(pairs=pairs, line=token.line, column=token.column)

    # ============ Helper Methods ============

    def check_type_keyword(self) -> bool:
        """Check if current token is a type keyword."""
        return self.check(TokenType.SCROLL) or self.check(TokenType.RUNE) or \
               self.check(TokenType.POTION) or self.check(TokenType.CHARM) or \
               self.check(TokenType.TOME) or self.check(TokenType.GRIMOIRE)

    def skip_newlines(self):
        """Skip any newline tokens."""
        while self.match(TokenType.NEWLINE):
            pass

    def advance(self) -> Token:
        """Consume and return the current token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def peek(self) -> Token:
        """Return the current token without consuming."""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Return the previously consumed token."""
        return self.tokens[self.current - 1]

    def check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def match(self, token_type: TokenType) -> bool:
        """Consume token if it matches expected type."""
        if self.check(token_type):
            self.advance()
            return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self.check(token_type):
            return self.advance()
        token = self.peek()
        raise SpellMiscast(message, token.line, token.column)

    def is_at_end(self) -> bool:
        """Check if we've reached the end of tokens."""
        return self.peek().type == TokenType.EOF
