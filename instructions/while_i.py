from typing import List

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
from abstract.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class WhileI(Instruction):
    def __init__(self, condition: Expression, instructions: List[Instruction], line: int, column: int):
        super().__init__(line, column)
        self.condition: Expression = condition
        self.instructions: List[Instruction] = instructions
        self.environment = Environment(None)  # default, for compiler to recognize it

    def execute(self, env: Environment) -> ExecReturn:
        # print("while")
        env.remove_child(self.environment)
        self.environment = Environment(env)
        env.children_environment.append(self.environment)

        while self.condition.execute(env).value:
            # print("accepted condition")
            result = self.execute_instructions()
            if result.propagate_method_return or result.propagate_break:
                return result

            # if continue don't anything, keep rolling

        # no return?
        return ExecReturn(ElementType.BOOL, False, False, False, False)

    def execute_instructions(self):
        instruction: Instruction
        for instruction in self.instructions:
            result = instruction.execute(self.environment)
            if result.propagate_method_return or result.propagate_break or result.propagate_continue:
                return result

        return ExecReturn(ElementType.VOID, None, False, False, False)
