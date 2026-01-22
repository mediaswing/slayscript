"""Lexer/Tokenizer for SlayScript."""

from .tokens import Token, TokenType, KEYWORDS
from .errors import DarkMagicDetected


class Lexer:
    """Tokenizes SlayScript source code."""

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.bracket_depth = 0  # Track nesting inside (), [], {}

    def tokenize(self) -> list:
        """Tokenize the entire source."""
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def scan_token(self):
        """Scan a single token."""
        c = self.advance()

        # Skip whitespace
        if c in ' \t\r':
            return

        # Newlines - suppress when inside brackets (for multi-line expressions)
        if c == '\n':
            if self.bracket_depth == 0:
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
            self.line += 1
            self.column = 1
            return

        # Comments
        if c == '~':
            if self.peek() == '~':
                self.multi_line_comment()
            else:
                self.single_line_comment()
            return

        # Strings
        if c == '"':
            self.string('"')
            return
        if c == "'":
            self.string("'")
            return

        # Numbers
        if c.isdigit():
            self.number()
            return

        # Identifiers and keywords
        if c.isalpha() or c == '_':
            self.identifier()
            return

        # Two-character operators
        if c == '*' and self.match('*'):
            self.add_token(TokenType.POWER, '**')
            return

        # Single-character tokens
        token_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            '.': TokenType.DOT,
        }

        if c in token_map:
            # Track bracket depth for potential future use
            if c in '([{':
                self.bracket_depth += 1
            elif c in ')]}':
                self.bracket_depth = max(0, self.bracket_depth - 1)
            self.add_token(token_map[c], c)
            return

        raise DarkMagicDetected(f"Unexpected character '{c}'", self.line, self.column - 1)

    def string(self, quote: str):
        """Parse a string literal."""
        value = []
        while not self.is_at_end() and self.peek() != quote:
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            if self.peek() == '\\' and self.peek_next() in (quote, '\\', 'n', 't', 'r'):
                self.advance()  # consume backslash
                escaped = self.advance()
                if escaped == 'n':
                    value.append('\n')
                elif escaped == 't':
                    value.append('\t')
                elif escaped == 'r':
                    value.append('\r')
                else:
                    value.append(escaped)
            else:
                value.append(self.advance())

        if self.is_at_end():
            raise DarkMagicDetected("Unterminated string", self.line, self.column)

        self.advance()  # closing quote
        self.add_token(TokenType.STRING, ''.join(value))

    def number(self):
        """Parse a number literal."""
        while self.peek().isdigit():
            self.advance()

        # Check for decimal
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # consume '.'
            while self.peek().isdigit():
                self.advance()
            value = float(self.source[self.start:self.current])
            self.add_token(TokenType.FLOAT, value)
        else:
            value = int(self.source[self.start:self.current])
            self.add_token(TokenType.INTEGER, value)

    def identifier(self):
        """Parse an identifier or keyword."""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]

        # Check if it's a keyword
        if text in KEYWORDS:
            self.add_token(KEYWORDS[text], text)
        else:
            self.add_token(TokenType.IDENTIFIER, text)

    def single_line_comment(self):
        """Skip a single-line comment."""
        while not self.is_at_end() and self.peek() != '\n':
            self.advance()

    def multi_line_comment(self):
        """Skip a multi-line comment (~~ ... ~~)."""
        self.advance()  # consume second ~
        while not self.is_at_end():
            if self.peek() == '~' and self.peek_next() == '~':
                self.advance()
                self.advance()
                return
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
        raise DarkMagicDetected("Unterminated multi-line comment", self.line, self.column)

    def advance(self) -> str:
        """Consume and return the current character."""
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def peek(self) -> str:
        """Return the current character without consuming."""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        """Return the next character without consuming."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        """Consume character if it matches expected."""
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def is_at_end(self) -> bool:
        """Check if we've reached the end of source."""
        return self.current >= len(self.source)

    def add_token(self, token_type: TokenType, value):
        """Add a token to the list."""
        col = self.column - (self.current - self.start)
        self.tokens.append(Token(token_type, value, self.line, col))
