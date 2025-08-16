from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from .expr import Expr
    from .print import PrintStmt

R = TypeVar("R")


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: "StmtVisitor[R]") -> R:
        pass


class StmtVisitor(Generic[R], ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "ExprStmt") -> R:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: "PrintStmt") -> R:
        pass


class ExprStmt(Stmt):
    def __init__(self, expr: "Expr"):
        self.expr = expr

    def accept(self, visitor: "StmtVisitor[R]") -> R:
        return visitor.visit_expression_stmt(self)
