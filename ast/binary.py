from . import Expr
from . import Token

class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr
