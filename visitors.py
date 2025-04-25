from ast import ExprVisitor, Binary, Literal, Grouping, Unary


class PrintExprVisitor(ExprVisitor[str]):
    def visit_binary(self, expr: "Binary") -> str:
        return "binary"

    def visit_grouping(self, expr: "Grouping") -> str:
        return "grouping"

    def visit_literal(self, expr: "Literal") -> str:
        return "literal"

    def visit_unary(self, expr: "Unary") -> str:
        return "unary"
