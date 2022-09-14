from typing import List, Union

from abstract.expression import Expression
from abstract.instruction import Instruction
from elements.env import Environment


class ConditionClause:
    def __init__(self, condition: Union[Expression, None], instructions: List[Instruction], environment: Environment):
        self.condition: Expression = condition
        self.instructions: List[Instruction] = instructions
        self.environment: Environment = environment
