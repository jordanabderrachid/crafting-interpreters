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


class Token:
    def __init__(
        self, token_type: TokenType, lexeme: str, literal: int | float | str, line: int
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
        self.tokens = []

    def _is_at_end(self) -> bool:
        return True

    def _scan_token(self):
        pass

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, 0))
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
    main()
