from typing import Union

from errors.semantic_error import SemanticError
import global_config

from elements.value_tuple import ValueTuple

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from expressions.array_expression import ArrayExpression
from element_types.c_expression_type import ExpressionType

from elements.c_env import Environment

from element_types.array_def_type import ArrayDefType


class ArrayDeclaration(Instruction):

    # TODO add array_reference and var_reference to expression type,
    def __init__(self, variable_id: str, array_type: Union[ArrayDefType, None], expression: Union[ArrayExpression, None], is_mutable: bool,
                 line: int, column: int):
        self.variable_id = variable_id
        self.array_type = array_type
        self.dimensions: int = -1
        self.expression = expression
        self.values = []
        self.is_mutable = is_mutable
        super().__init__(line, column)
        self.var_type = None

    def execute(self, env: Environment) -> ExecReturn:

        #Inferred array (possibly delegated from declaration)
        the_symbol = None
        the_array_expr = None
        if self.array_type is None:
            dimensions = global_config.extract_dimensions_to_dict(self.expression.value)
            tmp = self.expression
            while isinstance(tmp.value, list):
                tmp = tmp.value[0]
            the_type = tmp.expression_type

            self.array_type = the_type
            r = global_config.match_array_type(the_type, self.expression.value)
            # print(f'Type match:{r}')

            if not r:
                error_msg = f'Uno o mas elementos del array no concuerdan en tipo con su definición'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            the_symbol = env.save_variable_array(self.variable_id, the_type, dimensions, self.is_mutable, True,
                                                 self.line, self.column)
            the_array_expr = self.expression.value

        else:
            # Find out what dimension should I be
            level = 1
            sizes = {}
            arr_def_type = self.array_type
            while True:

                the_size = arr_def_type.size_expr.execute(env)
                if the_size.expression_type is not ExpressionType.INT:
                    error_msg = f'Tamaño de array debe ser una expresion entera'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                sizes[level] = int(the_size.value)

                if not arr_def_type.is_nested_array:
                    # print(f'Inner most type:{arr_def_type.content_type}')
                    self.var_type = arr_def_type.content_type
                    break

                arr_def_type = arr_def_type.content_type
                level += 1

            # Not initialized
            if self.expression is None:
                # env.save_variable_array(self._id, self.var_type, self.dimensions, None, self.is_mutable, False,
                #                         self.line, self.column)
                #
                # return ExecReturn(ExpressionType.BOOL, True, False, False, False)
                # FIXME Allowed?
                error_msg = f'Un array debe inicializarse con un tamaño fijo'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            # TODO check for expansions

            # Get my supposed values and match dimensions
            result: ValueTuple = self.expression.execute(env)
            r = global_config.match_dimensions(list(sizes.values()), result.value)
            # print(f'Dimension match:{r}')
            if not r:
                error_msg = f'Uno o mas elementos del array no concuerdan en tamaño con su definición'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            self.dimensions = sizes

            r = global_config.match_array_type(self.var_type, result.value)
            # print(f'Type match:{r}')

            if not r:
                error_msg = f'Uno o mas elementos del array no concuerdan en tipo con su definición'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            the_symbol = env.save_variable_array(self.variable_id, self.var_type, self.dimensions, self.is_mutable,
                                                 True,
                                                 self.line, self.column)
            the_array_expr = result.value

        # Accepted

        flat_array = global_config.flatten_array(the_array_expr)

        from generator import Generator
        generator = Generator()
        generator.add_comment(f"-------------------------------Array Declaration of {self.variable_id}"
                              f"-------------------------------")
        t = generator.new_temp()
        generator.add_expression(t, "P", the_symbol.stack_position, "+")
        generator.add_set_stack(t, "H")
        for expr in flat_array:

            r = expr.execute(env)
            generator.combine_with(r.generator)
            generator.add_set_heap("H", str(r.value))
            generator.add_next_heap()

        return ExecReturn(generator=generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)





