from errors.semantic_error import SemanticError
import global_config
from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from abstract.expression import Expression
from elements.value_tuple import ValueTuple
from elements.c_env import Symbol
from generator import Generator


class Declaration(Instruction):

    def __init__(self, variable_id: str, expression_type: ExpressionType, expression: Expression, is_mutable: bool,
                 line: int, column: int):
        super().__init__(line, column)
        self.variable_id = variable_id
        self.expression_type: ExpressionType = expression_type
        self.expression: Expression = expression
        self.is_mutable = is_mutable

        # if self._type is None:
        #     print(f'Instance of declaration with id:{self._id} type:inferred')
        # else:
        #     print(f'Instance of declaration with id:{self._id} type:{self._type.name}')

    def execute(self, env: Environment) -> ExecReturn:

        # Using not_init instead
        if self.expression is None:
            # tmp_var: Symbol = env.save_variable(self.variable_id, self.expression_type, self.is_mutable, False,
            #                                     self.line, self.column)
            #
            # generator = Generator()
            # # bla bla for adding it, should implement generator.add_not_init or something with better name lmao
            #
            # return ExecReturn(generator=generator,
            #                   propagate_method_return=False, propagate_continue=False, propagate_break=False)

            error_msg = f'No pueden declararse variables sin inicializarse ' \
                        f'(<{self.variable_id}>)'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        expr: Expression = self.expression
        # print(expr)

        # Infer if not explicitly specified
        if self.expression_type is None:
            self.expression_type = expr.expression_type

        # bool is a special type
        if expr.expression_type == ExpressionType.BOOL:

            generator = Generator()
            generator.add_comment(f"-------------------------------Declaration of {self.variable_id}"
                                  f"-------------------------------")
            result: ValueTuple = expr.execute(env)
            generator.combine_with(result.generator)

            the_symbol: Symbol = env.save_variable(self.variable_id, self.expression_type,
                                                   self.is_mutable, True, self.line, self.column)

            exit_label = generator.new_label()
            generator.add_label(result.false_label)
            t = generator.new_temp()
            generator.add_expression(t, "P", the_symbol.stack_position, "+")
            generator.add_set_stack(t, "0")
            generator.add_goto(exit_label)

            generator.add_label(result.true_label)
            t = generator.new_temp()
            generator.add_expression(t, "P", the_symbol.stack_position, "+")
            generator.add_set_stack(t, "1")
            generator.add_label([exit_label])

            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # Check same type
        if expr.expression_type == self.expression_type:
            result: ValueTuple = expr.execute(env)
            the_symbol: Symbol = env.save_variable(self.variable_id, self.expression_type,
                                                   self.is_mutable, True, self.line, self.column)

            generator = Generator()
            generator.add_comment(f"-------------------------------Declaration of {self.variable_id}"
                                  f"-------------------------------")

            generator.combine_with(result.generator)

            t = generator.new_temp()
            generator.add_expression(t, "P", the_symbol.stack_position, "+")
            generator.add_set_stack(t, str(result.value))
            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # Exceptions of same type:
        # char var_type with str expr_type
        if self.expression_type == ExpressionType.CHAR and expr.expression_type == ExpressionType.STRING_PRIMITIVE:
            result: ValueTuple = expr.execute(env)
            the_symbol: Symbol = env.save_variable(self.variable_id, self.expression_type,
                                                   self.is_mutable, True, self.line, self.column)

            generator = Generator()
            generator.add_comment(f"-------------------------------Declaration of {self.variable_id}"
                                  f"-------------------------------")

            generator.combine_with(result.generator)

            t = generator.new_temp()
            generator.add_expression(t, "P", the_symbol.stack_position, "+")
            generator.add_set_stack(t, str(result.value))

            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # usize var_type with int expr_type
        if self.expression_type == ExpressionType.USIZE and expr.expression_type == ExpressionType.INT:

            if global_config.is_arithmetic_pure_literals(self.expression):
                result: ValueTuple = expr.execute(env)
                the_symbol: Symbol = env.save_variable(self.variable_id, self.expression_type,
                                                       self.is_mutable, True, self.line, self.column)

                t = result.generator.new_temp()
                result.generator.add_expression(t, "P", the_symbol.stack_position, "+")
                result.generator.add_set_stack(t, str(result.value))
                return ExecReturn(generator=result.generator,
                                  propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # Error:
        error_msg = f'Asignación de tipo {expr.expression_type.name} a variable <{self.variable_id}> ' \
                    f'de tipo {self.expression_type.name}'
        global_config.log_semantic_error(error_msg, self.line, self.column)
        raise SemanticError(error_msg, self.line, self.column)
