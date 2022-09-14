from typing import List

import global_config

from elements.value_tuple import ValueTuple
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
from abstract.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class LoopE(Instruction):
    def __init__(self, instructions: List[Instruction], line: int, column: int):
        super().__init__(line, column)
        self.instructions: List[Instruction] = instructions
        self.environment = Environment(None)  # default, for compiler to recognize it

    def execute(self, env: Environment) -> ValueTuple:
        # print("loop_e")
        env.remove_child(self.environment)
        self.environment = Environment(env)
        env.children_environment.append(self.environment)

        counter = 0

        while True:
            # print("accepted condition")
            result = self.execute_instructions()
            if result.propagate_method_return:
                error_msg = f"Return Invalido: No se puede usar return dentro e un loop como expresion." \
                            f"Para asignar un valor, use \"break expr\""
                global_config.log_semantic_error(error_msg, -1, -1)
                raise SemanticError(error_msg, -1, -1)

            if result.propagate_break:
                return ValueTuple(result.value, result._type, False)

            # if continue don't anything, keep rolling

            counter += 1
            if counter >= 50000:
                error_msg = f"INFINITE LOOP: La función loop ha iterado por demasiadas veces (50k)"
                global_config.log_semantic_error(error_msg, -1, -1)
                raise SemanticError(error_msg, -1, -1)

        # no return? This shouldn't happen
        # return ValueTuple(None, ElementType.VOID, False)

    def execute_instructions(self):
        instruction: Instruction
        for instruction in self.instructions:
            result = instruction.execute(self.environment)
            if result.propagate_method_return or result.propagate_break or result.propagate_continue:
                return result

        return ExecReturn(ElementType.VOID, None, False, False, False)
