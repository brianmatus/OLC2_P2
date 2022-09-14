from typing import Union, List

from abstract.expression import Expression
from elements.env import Environment


class MatchExpressionClause:
    def __init__(self, condition: Union[List[Expression], None],
                 expr: Expression, environment: Environment):
        self.condition: List[Expression] = condition
        self.expr: Expression = expr
        self.environment: Environment = environment
