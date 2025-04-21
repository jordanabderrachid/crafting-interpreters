from typing import Any
from . import Expr

class Literal(Expr):
    value: Any
