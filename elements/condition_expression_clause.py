from typing import Union, List

from abstract.expression import Expression
from abstract.instruction import Instruction
from elements.c_env import Environment


class ConditionExpressionClause:
    def __init__(self, condition: Union[Expression, None], instructions: List[Instruction], expr: Expression,
                 environment: Environment):
        self.condition: Expression = condition
        self.expr: Expression = expr
        self.environment: Environment = environment
        self.instructions: List[Instruction] = instructions
