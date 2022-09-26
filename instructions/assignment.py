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
        print(f"Instance of assignment with id {variable_id}")

    def execute(self, env: Environment) -> ExecReturn:

        generator = Generator()
        generator.add_comment(f"-------------------------------Assignment of {self.variable_id}"
                              f"-------------------------------")
        result = self.expression.execute(env)
        generator.combine_with(result.generator)
        the_symbol = env.set_variable(self.variable_id, result, self.line, self.column)

        # Accepted
        if self.expression.expression_type == ExpressionType.BOOL:

            exit_label = generator.new_label()
            t = generator.new_temp()
            generator.add_expression(t, "P", the_symbol.heap_position, "+")

            generator.add_label(result.false_label)
            generator.add_set_stack(t, "0")
            generator.add_goto(exit_label)

            generator.add_label(result.true_label)
            generator.add_set_stack(t, "1")

            generator.add_label([exit_label])

            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        generator.add_set_stack(str(the_symbol.heap_position), str(result.value))
        return ExecReturn(generator=generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)
