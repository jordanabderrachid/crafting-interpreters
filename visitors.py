from lox_ast import ExprVisitor, Binary, Literal, Grouping, Unary, Expr


class PrintExprVisitor(ExprVisitor[str]):
    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        parts = [f"({name}"]
        for expr in exprs:
            parts.append(f" {expr.accept(self)}")
        parts.append(")")
        return "".join(parts)

    def visit_binary(self, expr: "Binary") -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr: "Grouping") -> str:
        return self._parenthesize("group", expr.left, expr.right)

    def visit_literal(self, expr: "Literal") -> str:
        if expr.value is None:
            return "nil"

        return str(expr.value)

    def visit_unary(self, expr: "Unary") -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def print(self, expr: "Expr") -> str:
        return expr.accept(self)
