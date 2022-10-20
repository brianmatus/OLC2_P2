from typing import List

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from abstract.expression import Expression
from elements.c_env import Environment, TransferType, TransferInstruction

from elements.value_tuple import ValueTuple

from generator import Generator


class LoopE(Expression):
    def __init__(self, instructions: List[Instruction], line: int, column: int):
        super().__init__(line, column)
        self.instructions: List[Instruction] = instructions
        self.environment = Environment(None)  # default, for compiler to recognize it

    def execute(self, environment: Environment) -> ValueTuple:

        final_generator: Generator = Generator()
        final_generator.add_comment(f"<<<---------------------------LOOP AS EXPR------------------------------->>>")

        final_generator.add_comment("-----Update P for a new environment-----")
        final_generator.add_expression("P", "P", environment.size, "+")

        loop_env = Environment(environment)

        l_loop = final_generator.new_label()
        loop_env.transfer_control.append(TransferInstruction(TransferType.CONTINUE, l_loop, True))
        l_exit = final_generator.new_label()
        loop_env.transfer_control.append(TransferInstruction(TransferType.BREAK, l_exit, True))

        final_generator.add_label([l_loop])

        for instruction in self.instructions:
            a = instruction.execute(loop_env)
            final_generator.combine_with(a.generator)

        final_generator.add_comment("--------------GO BACK TO LOOP--------------")
        final_generator.add_goto(l_loop)

        final_generator.add_label([l_exit])


        t_r = final_generator.new_temp()
        final_generator.add_expression(t_r, "t0", "", "")

        the_type = global_config.find_loop_break_type(self.instructions)

        return ValueTuple(value=t_r, expression_type=the_type, is_mutable=True, generator=final_generator,
                          content_type=the_type, capacity=None, is_tmp=True, true_label=[], false_label=[])


