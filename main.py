from enum import Enum
import sys
from typing import Any

from lox_ast import (
    Expr,
    Binary,
    Unary,
    Literal,
    Grouping,
    ExprVisitor,
    StmtVisitor,
    PrintStmt,
    Stmt,
    ExprStmt,
    Variable,
    Assign,
    VarStmt,
)

had_error = False
had_runtime_error = False


class ParseError(Exception):
    pass


class RuntimeError(Exception):
    def __init__(self, token: "Token", msg: str):
        self.token = token
        self.msg = msg


def error(line: int, message: str):
    global had_error
    had_error = True
    report(line, "", message)


def runtime_error(rerr: RuntimeError):
    global had_runtime_error
    had_runtime_error = True
    print(f"{rerr.msg}\n[line {rerr.token.line}]")


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
            (
                float(self.source[self.start : self.current])
                if is_float
                else int(self.source[self.start : self.current])
            ),
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


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def is_at_end(self) -> bool:
        return self._peek().token_type == TokenType.EOF

    def _advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self._previous()

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self._peek().token_type == token_type

    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True

        return False

    def _consume(self, token_type: TokenType, msg: str) -> Token:
        if self._check(token_type):
            return self._advance()

        raise self._error(self._peek(), msg)

    def _error(self, token: Token, msg: str) -> ParseError:
        if token.token_type == TokenType.EOF:
            report(token.line, " at end", msg)
        else:
            report(token.line, f" at '{token.lexeme}'", msg)

        return ParseError()

    def _synchronize(self):
        self._advance()

        while not self.is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            match self._peek().token_type:
                case TokenType.CLASS:
                    return
                case TokenType.FUN:
                    return
                case TokenType.VAR:
                    return
                case TokenType.FOR:
                    return
                case TokenType.IF:
                    return
                case TokenType.WHILE:
                    return
                case TokenType.PRINT:
                    return
                case TokenType.RETURN:
                    return

            self._advance()

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()

            return self._statement()
        except ParseError:
            self._synchronize()
            return None

    def _var_declaration(self) -> Stmt:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name.")
        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")

        return VarStmt(name, initializer)

    def _statement(self) -> Stmt:
        if self._match(TokenType.PRINT):
            return self._print_statement()

        return self._expression_statement()

    def _expression_statement(self) -> Stmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return ExprStmt(value)

    def _print_statement(self) -> Stmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)

    # expression → assignment ;
    def _expression(self) -> Expr:
        return self._assignment()

    # assignment → IDENTIFIER "=" assignment
    #            | equality ;
    def _assignment(self) -> Expr:
        expr = self._equality()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    # equality → comparison ( ( "!=" | "==" ) comparison )* ;
    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    # comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    # term → factor ( ( "-" | "+" ) factor )* ;
    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    # factor → unary ( ( "/" | "*" ) unary )* ;
    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    # unary → ( "!" | "-" ) unary
    #       | primary ;
    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._primary()

    # primary → NUMBER | STRING | "true" | "false" | "nil" | IDENTIFIER
    #         | "(" expression ")" ;
    def _primary(self) -> Expr:
        if self._match(TokenType.TRUE):
            return Literal(True)

        if self._match(TokenType.FALSE):
            return Literal(True)

        if self._match(TokenType.NIL):
            return Literal(None)

        if self._match(TokenType.STRING, TokenType.NUMBER):
            return Literal(self._previous().literal)

        if self._match(TokenType.IDENTIFIER):
            return Variable(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.is_at_end():
            stmt = self._declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    def __init__(self) -> None:
        self.environment = Environment()

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "nil"

        if type(value) is bool:
            return "true" if value else "false"

        if self._is_number(value):
            repr = str(value)
            if repr.endswith(".0"):
                repr = repr[:-2]
            return repr

        return str(value)

    def _evaluate(self, expr: "Expr") -> Any:
        return expr.accept(self)

    def _execute(self, stmt: "Stmt") -> None:
        stmt.accept(self)

    def _is_truthy(self, value: Any) -> bool:
        if value is None:
            return False

        if type(value) is bool:
            return bool(value)

        return True

    def _is_number(self, value: Any) -> bool:
        return type(value) is float or type(value) is int

    def _check_number_operand(self, operator: Token, operand: Any):
        if self._is_number(operand):
            return

        raise RuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: Any, right: Any):
        if self._is_number(left) and self._is_number(right):
            return

        raise RuntimeError(operator, "Operands must be a number.")

    def visit_binary(self, expr: "Binary") -> Any:
        left: Any = self._evaluate(expr.left)
        right: Any = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                return float(left) / float(right)
            case TokenType.STAR:
                self._check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.PLUS:
                if type(left) is str and type(right) is str:
                    return f"{left}{right}"

                if self._is_number(left) and self._is_number(right):
                    return float(left) + float(right)

                raise RuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not left == right
            case TokenType.EQUAL_EQUAL:
                return left == right

        return None

    def visit_grouping(self, expr: "Grouping") -> Any:
        return self._evaluate(expr.expression)

    def visit_literal(self, expr: "Literal") -> Any:
        return expr.value

    def visit_unary(self, expr: "Unary") -> Any:
        right: Any = self._evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self._is_truthy(right)

        # unreachable
        return None

    def visit_variable(self, expr: "Variable") -> Any:
        return self.environment.get(expr.name)

    def visit_assign(self, expr: "Assign") -> Any:
        value = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_expression_stmt(self, stmt: "ExprStmt") -> None:
        self._evaluate(stmt.expr)

    def visit_print_stmt(self, stmt: "PrintStmt") -> None:
        value = self._evaluate(stmt.expr)
        print(self._stringify(value))

    def visit_var_stmt(self, stmt: "VarStmt") -> None:
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def interpret(self, stmts: "list[Stmt]"):
        try:
            for stmt in stmts:
                self._execute(stmt)
        except RuntimeError as rerr:
            runtime_error(rerr)


class Environment:
    def __init__(self) -> None:
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.values[name] = value

    def _ensure(self, name: Token):
        if name.lexeme not in self.values:
            raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get(self, name: Token) -> Any:
        self._ensure(name)
        return self.values[name.lexeme]

    def assign(self, name: Token, value: Any):
        self._ensure(name)
        self.define(name.lexeme, value)


def run_file(filepath: str):
    global had_error
    global had_runtime_error
    with open(filepath, "rb") as file:
        data = file.read()
        run(data.decode("utf-8"))
        if had_error:
            sys.exit(65)
        if had_runtime_error:
            sys.exit(70)


interpreter = Interpreter()


def run(script: str):
    global interpreter
    scanner = Scanner(script)
    parser = Parser(scanner.scan_tokens())
    statements = parser.parse()

    if had_error:
        return

    interpreter.interpret(statements)


def run_prompt():
    global had_error
    global had_runtime_error
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
        had_runtime_error = False


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
