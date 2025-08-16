from typing import TYPE_CHECKING, override, TypeVar

from .stmt import Stmt

if TYPE_CHECKING:
    from .stmt import StmtVisitor
    from .expr import Expr

R = TypeVar("R")


class PrintStmt(Stmt):
    def __init__(self, expr: "Expr"):
        self.expr = expr

    @override
    def accept(self, visitor: "StmtVisitor[R]") -> R:
        return visitor.visit_print_stmt(self)
