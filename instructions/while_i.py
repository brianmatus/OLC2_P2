from typing import List

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment, TransferType, TransferInstruction
from abstract.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause

from global_config import log_semantic_error
from errors.semantic_error import SemanticError

from generator import Generator


class WhileI(Instruction):
    def __init__(self, condition: Expression, instructions: List[Instruction], line: int, column: int):
        super().__init__(line, column)
        self.condition: Expression = condition
        self.instructions: List[Instruction] = instructions
        self.environment = Environment(None)  # default, for compiler to recognize it

    def execute(self, env: Environment) -> ExecReturn:

        final_generator: Generator = Generator(env)
        final_generator.add_comment(f"<<<-------------------------------WHILE------------------------------->>>")

        final_generator.add_comment("-----Update P for a new environment-----")
        final_generator.add_expression("P", "P", env.size, "+")

        while_env = Environment(env)

        l_loop = final_generator.new_label()
        while_env.transfer_control.append(TransferInstruction(TransferType.CONTINUE, l_loop, False))
        l_exit = final_generator.new_label()
        while_env.transfer_control.append(TransferInstruction(TransferType.BREAK, l_exit, False))

        final_generator.add_label([l_loop])

        condition_result = self.condition.execute(while_env)
        if condition_result.expression_type != ExpressionType.BOOL:
            error_msg = f"La expresión de un while debe ser de tipo booleano." \
                        f"(Se obtuvo ->{condition_result.expression_type})."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        final_generator.combine_with(condition_result.generator)

        final_generator.add_label(condition_result.true_label)
        for instruction in self.instructions:
            a = instruction.execute(while_env)
            final_generator.combine_with(a.generator)

        final_generator.add_comment("--------------GO BACK TO LOOP--------------")
        final_generator.add_goto(l_loop)

        final_generator.add_label(condition_result.false_label)
        final_generator.add_label([l_exit])

        final_generator.add_comment("-----Revert P for a previous environment-----")
        final_generator.add_expression("P", "P", env.size, "-")

        return ExecReturn(final_generator, False, False, False)


