from typing import Union, List
from abstract.expression import Expression


class FuncCallArg:

    def __init__(self, expr: Expression, as_reference: bool, as_mutable: bool):
        self.expr: Expression = expr
        self.as_reference: bool = as_reference
        self.as_mutable: bool = as_mutable
