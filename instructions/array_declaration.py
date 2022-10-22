from typing import Union

from errors.semantic_error import SemanticError
import global_config

from elements.value_tuple import ValueTuple

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from expressions.array_expression import ArrayExpression
from element_types.c_expression_type import ExpressionType
from expressions.variable_ref import VariableReference
from expressions.array_reference import ArrayReference

from elements.c_env import Environment
from element_types.array_def_type import ArrayDefType
from generator import Generator


class ArrayDeclaration(Instruction):

    # TODO add array_reference and var_reference to expression type,
    def __init__(self, variable_id: str, array_type: Union[ArrayDefType, None],
                 expression: Union[ArrayExpression, VariableReference, ArrayReference, None], is_mutable: bool,
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

        # Variable ref from another array (total array, partial may be not allowed)

        # if isinstance(self.expression, VariableReference) or isinstance(self.expression, ArrayReference):
        if type(self.expression) in [VariableReference, ArrayReference]:
            result = self.expression.execute(env)

            if self.array_type is not None:
                # Find out what dimension should I be
                level = 1
                sizes = {}
                arr_def_type = self.array_type
                while True:

                    the_size = arr_def_type.size_expr.execute(env)
                    if the_size.expression_type is not ExpressionType.INT:
                        error_msg = f'Tamaño de array debe ser una expresión entera'
                        global_config.log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)

                    sizes[level] = int(the_size.value)

                    if not arr_def_type.is_nested_array:
                        # print(f'Inner most type:{arr_def_type.content_type}')
                        self.var_type = arr_def_type.content_type
                        break

                    arr_def_type = arr_def_type.content_type
                    level += 1

                if result.content_type != arr_def_type.content_type:
                    error_msg = f'Uno o mas elementos del array no concuerdan en tipo con su definición'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                # print(f'Dimension match:{r}')
                if len(sizes.keys()) != len(result.capacity):
                    error_msg = f'El tamaño del array no es el adecuado'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

            generator = Generator(env)
            generator.add_comment(f"-------------------------------Array Declaration of {self.variable_id} as reference"
                                  f"-------------------------------")

            generator.combine_with(result.generator)

            generator.add_comment("Array declaration by reference just copy the reference, no code actually generated")

            d = {}
            for i in range(1, len(result.capacity)+1):
                d[i] = result.capacity[i-1]

            the_symbol = env.save_variable_array(variable_id=self.variable_id, content_type=result.content_type,
                                                 dimensions=d,
                                                 is_init=True, is_mutable=self.is_mutable,
                                                 line=self.line, column=self.column)

            place = generator.new_temp()
            generator.add_expression(place, "P", the_symbol.heap_position, "+")
            generator.add_set_stack(place, result.value)

            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # Inferred array (possibly delegated from declaration)
        the_symbol = None
        the_array_expr = None
        if self.array_type is None:
            dimensions = global_config.extract_dimensions_to_dict(self.expression.value)
            tmp = self.expression
            while isinstance(tmp, ArrayExpression) and isinstance(tmp.value, list):
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
                    error_msg = f'Tamaño de array debe ser una expresión entera'
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

        # ###################################################Accepted###################################################
        flat_array = global_config.flatten_array(the_array_expr)

        generator = Generator(env)
        generator.add_comment(f"-------------------------------Array Declaration of {self.variable_id}"
                              f"-------------------------------")

        # First do all stuff in heap, then get those values/references and make array out of it
        # Why not set values while making it? Because of pointers. String for example would make array heap location
        # not continuous. This avoids that problem.
        values = []
        for expr in flat_array:
            r = expr.execute(env)
            generator.combine_with(r.generator)
            if r.expression_type == ExpressionType.BOOL:
                t = generator.new_temp()
                l_exit = generator.new_label()
                generator.add_label(r.true_label)
                generator.add_expression(t, "1", "", "")
                generator.add_goto(l_exit)
                generator.add_label(r.false_label)
                generator.add_expression(t, "0", "", "")
                generator.add_label([l_exit])
                values.append(t)
                continue
            values.append(str(r.value))

        t = generator.new_temp()
        generator.add_expression(t, "P", the_symbol.heap_position, "+")
        generator.add_set_stack(t, "H")

        for val in values:
            generator.add_set_heap("H", val)
            generator.add_next_heap()

        return ExecReturn(generator=generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)
