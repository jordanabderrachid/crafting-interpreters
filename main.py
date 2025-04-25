from enum import Enum
import sys


had_error = False


def error(line: int, message: str):
    global had_error
    had_error = True
    report(line, "", message)


def report(line: int, where: str, message: str):
    global had_error
    had_error = True
    print(f"[line {line}] Error {where}: {message}")


class TokenType(Enum):
    # single-character
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"

    # one or two character
    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"

    # keywords
    AND = "AND"
    CLASS = "CLASS"
    ELSE = "ELSE"
    FALSE = "FALSE"
    FUN = "FUN"
    FOR = "FOR"
    IF = "IF"
    NIL = "NIL"
    OR = "OR"
    PRINT = "PRINT"
    RETURN = "RETURN"
    SUPER = "SUPER"
    THIS = "THIS"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"

    EOF = "EOF"


KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class Token:
    def __init__(
        self,
        token_type: TokenType,
        lexeme: str,
        literal: int | float | str | None,
        line: int,
    ):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.token_type} {self.lexeme} {self.literal}"


class Scanner:
    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _add_token(self, type: TokenType, litteral: int | float | str | None = None):
        self.tokens.append(
            Token(type, self.source[self.start : self.current], litteral, self.line)
        )

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            self._advance()

        if self._is_at_end():
            error(self.line, "Unterminated string.")
            return

        # the final '"'
        self._advance()

        self._add_token(
            TokenType.STRING, self.source[self.start + 1 : self.current - 1]
        )

    def _is_digit(self, c: str) -> bool:
        return c >= "0" and c <= "9"

    def _is_alpha(self, c: str) -> bool:
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    def _is_alphanumeric(self, c: str) -> bool:
        return self._is_alpha(c) or self._is_digit(c)

    def _number(self):
        is_float = False
        while self._is_digit(self._peek()):
            self._advance()

        if self._peek() == "." and self._is_digit(self._peek_next()):
            is_float = True
            self._advance()  # consume the "."
            while self._peek().isdigit():
                self._advance()

        self._add_token(
            TokenType.NUMBER,
            float(self.source[self.start : self.current])
            if is_float
            else int(self.source[self.start : self.current]),
        )

    def _identifier(self):
        while self._is_alphanumeric(self._peek()):
            self._advance()

        type = KEYWORDS.get(
            self.source[self.start : self.current], TokenType.IDENTIFIER
        )

        self._add_token(type)

    def _scan_token(self):
        c = self._advance()
        match c:
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "!":
                if self._match("="):
                    self._add_token(TokenType.BANG_EQUAL)
                else:
                    self._add_token(TokenType.BANG)
            case "=":
                if self._match("="):
                    self._add_token(TokenType.EQUAL_EQUAL)
                else:
                    self._add_token(TokenType.EQUAL)
            case ">":
                if self._match("="):
                    self._add_token(TokenType.GREATER_EQUAL)
                else:
                    self._add_token(TokenType.GREATER)
            case "<":
                if self._match("="):
                    self._add_token(TokenType.LESS_EQUAL)
                else:
                    self._add_token(TokenType.LESS)
            case "/":
                if self._match("/"):
                    while self._peek() != "\n" and not self._is_at_end():
                        self._advance()
                else:
                    self._add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self._string()
            case _:
                if self._is_digit(c):
                    self._number()
                elif self._is_alpha(c):
                    self._identifier()
                else:
                    error(self.line, f"Unexpected character '{c}'")

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.start = self.current
        self._add_token(TokenType.EOF)

        return self.tokens


def run_file(filepath: str):
    global had_error
    with open(filepath, "rb") as file:
        data = file.read()
        run(data.decode("utf-8"))
        if had_error:
            sys.exit(65)


def run(script: str):
    scanner = Scanner(script)
    for token in scanner.scan_tokens():
        print(token)


def run_prompt():
    global had_error
    while True:
        print("> ", end="")
        try:
            input_str = input()
        except EOFError:
            print("\n")
            break
        if input_str == "exit" or input_str == "":
            break
        run(input_str)
        had_error = False


def main():
    args = sys.argv
    if len(args) > 2:
        print("usage: plox [script]")
        sys.exit(64)
    elif len(args) == 2:
        run_file(args[1])
    elif len(args) == 1:
        run_prompt()


if __name__ == "__main__":
    from ast import Binary, Literal
    from visitors import PrintExprVisitor

    expr = Binary(
        left=Literal(value=1),
        operator=Token(token_type=TokenType.PLUS, lexeme="+", literal=None, line=1),
        right=Literal(value=2),
    )
    print_visitor = PrintExprVisitor()
    print(expr.accept(print_visitor))
    # main()
