import math
from typing import Union, List

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.c_env import Environment
from abstract.expression import Expression
from expressions.array_expression import ArrayExpression
from elements.c_env import ArraySymbol
from element_types.c_expression_type import ExpressionType
from elements.value_tuple import ValueTuple

from errors.semantic_error import SemanticError
from global_config import log_semantic_error


class ArrayAssignment(Instruction):

    def __init__(self, variable_id: str, indexes: List[Expression], expr: Union[Expression, ArrayExpression],
                 line: int, column: int):
        super().__init__(line, column)
        self.variable_id = variable_id
        self.indexes: List[Expression] = indexes
        self.expr: Expression = expr

    def execute(self, env: Environment) -> ExecReturn:

        expr = self.expr.execute(env)

        the_symbol: ArraySymbol = env.get_variable(self.variable_id)

        if the_symbol is None:
            error_msg = f'Variable {self.variable_id} no esta definida en el ámbito actual'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if not isinstance(the_symbol, ArraySymbol):
            error_msg = f'Variable {self.variable_id} no es de tipo array y no puede ser indexada'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if not the_symbol.is_mutable and the_symbol.is_init:
            error_msg = f'Variable {self.variable_id} es constante y no puede ser asignado un valor nuevo'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        from generator import Generator
        generator = Generator()
        generator.add_comment("---------------ARRAY ASSIGNMENT---------------")
        generator.combine_with(expr.generator)

        dimensions = []
        ind: Expression
        for ind in self.indexes:
            result: ValueTuple = ind.execute(env)
            if result.expression_type not in [ExpressionType.INT, ExpressionType.USIZE]:
                error_msg = f'El acceso a array debe de ser con tipo entero/usize'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            generator.combine_with(result.generator)
            dimensions.append(result.value)

        if the_symbol.symbol_type != expr.expression_type:
            error_msg = f'El elemento del array no concuerda en tipo con su definición'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # if not isinstance(expr.value, list):
        #     if the_symbol.symbol_type != expr.expression_type:
        #         error_msg = f'El elemento del array no concuerda en tipo con su definición'
        #         global_config.log_semantic_error(error_msg, self.line, self.column)
        #         raise SemanticError(error_msg, self.line, self.column)
        #
        # else:
        #     r = global_config.match_array_type(the_symbol.symbol_type, expr.value)
        #     # print(f'Type match:{r}')
        #
        #     if not r:
        #         error_msg = f'Uno o mas elementos del array no concuerdan en tipo con su definición'
        #         global_config.log_semantic_error(error_msg, self.line, self.column)
        #         raise SemanticError(error_msg, self.line, self.column)

        # print(the_symbol.dimensions)
        # print(dimensions)

        # Too much dimensions?
        if len(dimensions) != len(the_symbol.dimensions) and len(dimensions) != 0:
            error_msg = f'Solo se permiten reasignaciones a array de la misma profundidad. Considere usar un for-loop' \
                        f'({len(dimensions)} != {len(the_symbol.dimensions)})'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # Index out of bounds check
        # resulting = the_symbol
        error_label = generator.new_label()
        exit_label = generator.new_label()
        for i in range(len(dimensions)):

            if the_symbol.dimensions[i+1] is None:
                continue

            generator.add_if(dimensions[i], the_symbol.dimensions[i + 1], ">=", error_label)

            if isinstance(dimensions[i], str):
                continue

            if dimensions[i] > the_symbol.dimensions[i + 1]:
                error_msg = f'Las dimensiones del array son menores a las ingresadas'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

        generator.add_goto(exit_label)
        generator.add_label([error_label])
        generator.add_print_message(f"ERROR SEMANTIC: Size incorrecto de array "
                                    f"en linea:{self.line} columna:{self.column}")
        generator.add_error_return("2")

        generator.add_label([exit_label])

        # # print(resulting)
        # # Same dimensions?
        # to_match = global_config.extract_dimensions_to_dict(resulting)
        #
        # # print("aquí xd")
        # # print(to_match)
        # # print(expr.value)
        #
        # match = global_config.match_dimensions(list(to_match.keys()), expr.value)
        # # print(match)
        #
        # # print('aquí 2')
        # # print("to be replaced:")
        # # print(resulting)
        # # print("the replacement:")
        # # print(expr)

        if len(dimensions) == 0:

            r = global_config.match_dimensions(list(the_symbol.dimensions.values()), expr.value)
            if not r:
                error_msg = f'Las dimensiones del array definidas anteriormente no son iguales a las ingresadas'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            flat_array = global_config.flatten_array(expr.value)
            from generator import Generator
            generator = Generator()
            generator.add_comment(f"-------------------------------Array Assignment of {self.variable_id}"
                                  f"-------------------------------")
            t = generator.new_temp()
            generator.add_expression(t, "P", the_symbol.heap_position, "+")
            generator.add_set_stack(t, "H")
            for expr in flat_array:
                r = expr.execute(env)
                generator.combine_with(r.generator)
                generator.add_set_heap("H", str(r.value))
                generator.add_next_heap()

            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # Define index of access by row-major
        coefficients = list(the_symbol.dimensions.values())

        generator.add_comment("array_ref::Mapping multidimensional indexes to single index (row major)")
        p = generator.new_temp()
        generator.add_expression(p, "0", "", "")

        p_deepness = env.get_variable_p_deepness(self.variable_id, 0)
        stack_value = generator.new_temp()
        generator.add_expression(stack_value, "P", str(0 - p_deepness), "+")
        # #######################################Define index of access by row-major####################################

        # Sliced array, r will have to be calculated in 3ac
        coefficients = list(the_symbol.dimensions.values())
        if coefficients[0] is None:
            for i in range(0, len(coefficients)):
                index = generator.new_temp()
                generator.add_expression(index, stack_value, str(i + 1), "+")
                generator.add_get_stack(index, index)
                coefficients[i] = index

            for i in range(len(dimensions)):

                r = generator.new_temp()
                generator.add_expression(r, "1", "", "")
                for coefficient in coefficients[i + 1:]:
                    generator.add_expression(r, r, coefficient, "*")

                partial = generator.new_temp()
                generator.add_expression(partial, r, dimensions[i], "*")
                generator.add_expression(p, p, partial, "+")

        else:
            # Normal definition, size is known in compile time
            # for i in range(len(dimensions) - 1):
            for i in range(len(dimensions)):
                r = math.prod(coefficients[i + 1:])
                partial = generator.new_temp()
                generator.add_expression(partial, str(r), dimensions[i], "*")
                generator.add_expression(p, p, partial, "+")

            # generator.add_expression(p, p, dimensions[len(dimensions) - 1], "+")

        base_heap_address = generator.new_temp()
        generator.add_get_stack(base_heap_address, stack_value)
        final_heap_address = generator.new_temp()
        generator.add_expression(final_heap_address, base_heap_address, p, "+")

        # ##############################################################################################################

        generator.add_set_heap(final_heap_address, expr.value)

        return ExecReturn(generator=generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # return ExecReturn(ExecReturn.BOOL, True, False, False, False)
