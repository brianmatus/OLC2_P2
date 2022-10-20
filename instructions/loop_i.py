from typing import List

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.c_env import Environment, TransferType, TransferInstruction

from generator import Generator


class LoopI(Instruction):
    def __init__(self, instructions: List[Instruction], line: int, column: int):
        super().__init__(line, column)
        self.instructions: List[Instruction] = instructions
        self.environment = Environment(None)  # default, for compiler to recognize it

    def execute(self, env: Environment) -> ExecReturn:

        final_generator: Generator = Generator()
        final_generator.add_comment(f"<<<-------------------------------LOOP------------------------------->>>")

        final_generator.add_comment("-----Update P for a new environment-----")
        final_generator.add_expression("P", "P", env.size, "+")

        while_env = Environment(env)

        l_loop = final_generator.new_label()
        while_env.transfer_control.append(TransferInstruction(TransferType.CONTINUE, l_loop, False))
        l_exit = final_generator.new_label()
        while_env.transfer_control.append(TransferInstruction(TransferType.BREAK, l_exit, False))

        final_generator.add_label([l_loop])

        for instruction in self.instructions:
            a = instruction.execute(while_env)
            final_generator.combine_with(a.generator)

        final_generator.add_comment("--------------GO BACK TO LOOP--------------")
        final_generator.add_goto(l_loop)

        final_generator.add_label([l_exit])

        return ExecReturn(final_generator, False, False, False)


