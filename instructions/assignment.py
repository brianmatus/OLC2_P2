from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from elements.c_env import Environment
from abstract.expression import Expression
from element_types.c_expression_type import ExpressionType

from generator import Generator


class Assigment(Instruction):
    def __init__(self, variable_id: str, expression: Expression, line: int, column: int):
        super().__init__(line, column)
        self.variable_id: str = variable_id
        self.expression: Expression = expression
        # print(f"Instance of assignment with id {variable_id}")

    def execute(self, env: Environment) -> ExecReturn:

        generator = Generator(env)
        generator.add_comment(f"-------------------------------Assignment of {self.variable_id}"
                              f"-------------------------------")
        result = self.expression.execute(env)


        # the symbol = ...
        env.set_variable(self.variable_id, result, self.line, self.column)

        # Accepted
        if self.expression.expression_type == ExpressionType.BOOL:

            exit_label = generator.new_label()
            ref_position = generator.new_temp()

            p_deepness = env.get_variable_p_deepness(self.variable_id, 0)
            generator.add_expression(ref_position, "P", str(0 - p_deepness), "+")

            generator.combine_with(result.generator)

            generator.add_label(result.false_label)
            generator.add_set_stack(ref_position, "0")
            generator.add_goto(exit_label)

            generator.add_label(result.true_label)
            generator.add_set_stack(ref_position, "1")

            generator.add_label([exit_label])

            return ExecReturn(generator=generator,

                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        generator.combine_with(result.generator)
        p_deepness = env.get_variable_p_deepness(self.variable_id, 0)
        ref_position = generator.new_temp()
        generator.add_expression(ref_position, "P", str(0 - p_deepness), "+")

        generator.add_set_stack(ref_position, str(result.value))
        return ExecReturn(generator=generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)
