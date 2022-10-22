from typing import List, Union

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from abstract.expression import Expression
from expressions.literal import Literal
from elements.value_tuple import ValueTuple

from global_config import log_semantic_error
from errors.semantic_error import SemanticError

from generator import Generator


class ForInRanged:
    def __init__(self, a: Expression, b: Expression):
        self.a: Expression = a
        self.b: Expression = b


class ForInI(Instruction):
    def __init__(self, looper: str, range_expr: Union[Expression, ForInRanged], instructions: List[Instruction],
                 line: int, column: int):
        super().__init__(line, column)
        self.looper: str = looper
        self.instructions: List[Instruction] = instructions
        self.range_expr: Union[Expression, ForInRanged] = range_expr
        self.environment = Environment(None)  # default, for compiler to recognize it
        self.intermediate_env = Environment(None)

    def execute(self, env: Environment) -> ExecReturn:
        gen = Generator(env)
        gen.add_comment(f"<<<-------------------------------FOR IN------------------------------->>>")

        for_in_env = Environment(env)
        if isinstance(self.range_expr, ForInRanged):
            gen.add_comment("---------RANGED---------")
            a = self.range_expr.a.execute(env)
            b = self.range_expr.b.execute(env)

            if a.expression_type not in [ExpressionType.INT, ExpressionType.USIZE] \
                    or b.expression_type not in [ExpressionType.INT, ExpressionType.USIZE]:
                error_msg = f"Un rango definido por a..b debe de ser tipo int o usize"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            gen.combine_with(a.generator)
            gen.combine_with(b.generator)

            gen.add_comment("-----Update P for a new environment-----")
            gen.add_expression("P", "P", env.size, "+")

            l_valid_range = gen.new_label()
            gen.add_if(a.value, b.value, "<=", l_valid_range)
            gen.add_print_message(f"for-in-ranged::r->{self.line} c->{self.column}::ERROR:Rango invalido. El numero de "
                                  f"la izquierda no puede ser mayor al de la derecha")
            gen.add_error_return("16")

            gen.add_label([l_valid_range])

            # Looper is guaranteed to be first in env, so no need to get its deepness
            gen.add_set_stack("P", a.value)

            t_a = gen.new_temp()

            t_b = gen.new_temp()
            gen.add_expression(t_b, b.value, "", "")

            l_loop = gen.new_label()
            l_finished = gen.new_label()

            gen.add_label([l_loop])
            gen.add_get_stack(t_a, "P")
            gen.add_if(t_a, t_b, "==", l_finished)
            for_in_env.save_variable(self.looper, ExpressionType.INT, True, True, self.line, self.column)

            for instruction in self.instructions:
                gen.combine_with(instruction.execute(for_in_env).generator)

            gen.add_expression(t_a, t_a, "1", "+")
            gen.add_set_stack("P", t_a)

            gen.add_comment("--------------GO BACK TO LOOP--------------")
            gen.add_goto(l_loop)

            gen.add_label([l_finished])

            gen.add_comment("-----Revert P for a previous environment-----")
            gen.add_expression("P", "P", env.size, "-")
            return ExecReturn(gen, False, False, False)

        result = self.range_expr.execute(env)



        return ExecReturn(gen, False, False, False)
