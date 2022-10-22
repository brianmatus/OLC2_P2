from typing import Union, Tuple

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.c_env import Environment, TransferType
from element_types.c_expression_type import ExpressionType
from abstract.expression import Expression

import global_config
from errors.semantic_error import SemanticError
from generator import Generator


class BreakI(Instruction):
    def __init__(self, expr: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)
        self.expr = expr

    def execute(self, env: Environment) -> ExecReturn:
        generator = Generator(env)
        generator.add_comment(f"-------------------------------BREAK Instruction-------------------------------")

        t = self.expr is not None

        where_to_jump, the_type, r, a = env.get_transfer_control_label(TransferType.BREAK, t,
                                                                 self.line, self.column)

        if self.expr is None:
            generator.add_comment("No value returned, this only to avoid past value being referenced")
            generator.add_expression("t0", "-4242", "", "")
            generator.add_expression("t2", "1", "", "")
            generator.add_goto(where_to_jump)
            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_break=False, propagate_continue=False)
        result = self.expr.execute(env)

        if result.expression_type == ExpressionType.ARRAY:
            gen, ptr = return_custom_array_expr(result.value, env)
            generator.combine_with(gen)
            generator.add_expression("t0", ptr, "", "")
            generator.add_expression("t2", "1", "", "")
            generator.add_goto(where_to_jump)
            return ExecReturn(generator=generator,
                              propagate_method_return=True, propagate_continue=False, propagate_break=False)

        # if the_type != result.expression_type:
        #     error_msg = f'Se ha devuelto un tipo de dato incorrecto {the_type.name} <=> {result.expression_type.name}'
        #     global_config.log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)


        generator.combine_with(result.generator)
        if result.expression_type == ExpressionType.BOOL:
            l_added = generator.new_label()
            generator.add_label(result.true_label)
            generator.add_expression("t0", "1", "", "")
            generator.add_goto(l_added)
            generator.add_label(result.false_label)
            generator.add_expression("t0", "0", "", "")
            generator.add_label([l_added])
        else:
            generator.add_expression("t0", result.value, "", "")
        generator.add_expression("t2", "1", "", "")
        generator.add_goto(where_to_jump)

        return ExecReturn(generator=generator,
                          propagate_method_return=True, propagate_continue=False, propagate_break=False)


def return_custom_array_expr(the_array_expr, env: Environment) -> Tuple[Generator, str]:
    flat_array = global_config.flatten_array(the_array_expr)
    generator = Generator(env)
    generator.add_comment(f"-------------------------------Array Expr passed as arg-------------------------------")

    values = []
    for expr in flat_array:
        r = expr.execute(env)
        generator.combine_with(r.generator)
        values.append(str(r.value))

    t = generator.new_temp()
    generator.add_expression(t, "H", "", "")
    generator.add_set_stack(t, "H")

    for val in values:
        generator.add_set_heap("H", val)
        generator.add_next_heap()

    return generator, t
