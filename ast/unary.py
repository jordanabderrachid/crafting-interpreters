from . import Expr
from . import Token

class Unary(Expr):
    operator: Token
    right: Expr
