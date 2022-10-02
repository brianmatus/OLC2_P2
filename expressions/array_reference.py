import math

from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType

from elements.c_env import ArraySymbol
from elements.c_env import VectorSymbol

from global_config import log_semantic_error
from errors.semantic_error import SemanticError

from generator import Generator


class ArrayReference(Expression):

    def __init__(self, variable_id: str, indexes: list, line: int, column: int):
        super().__init__(line, column)
        self.variable_id = variable_id
        self.indexes = indexes

    def execute(self, environment: Environment) -> ValueTuple:
        the_symbol: ArraySymbol = environment.get_variable(self.variable_id)

        if the_symbol is None:
            error_msg = f'Variable {self.variable_id} no esta definida en el ámbito actual'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # TODO check for VectorSymbol

        if not isinstance(the_symbol, ArraySymbol):
            error_msg = f'Variable {self.variable_id} fue referida (indexada) como array sin serlo.'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        generator = Generator()
        generator.add_comment(f"-------------------------------Array Reference of {self.variable_id} as array"
                              f"-------------------------------")

        if len(self.indexes) > len(the_symbol.dimensions):
            error_msg = f'La profundidad del array es menor a la ingresada'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        dimensions = []
        ind: Expression
        for ind in self.indexes:
            result: ValueTuple = ind.execute(environment)
            if result.expression_type not in [ExpressionType.INT, ExpressionType.USIZE]:
                error_msg = f'El acceso a array debe de ser con tipo entero/usize'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            generator.combine_with(result.generator)
            dimensions.append(result.value)

            # Index out of bounds check
            error_label = generator.new_label()
            exit_label = generator.new_label()
            for i in range(len(dimensions)):
                generator.add_if(dimensions[i], the_symbol.dimensions[i + 1], ">=", error_label)
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

        # Define index of access by row-major
        coefficients = list(the_symbol.dimensions.values())

        generator.add_comment("Mapping multidimensional indexes to single index (row major)")
        p = generator.new_temp()
        generator.add_expression(p, "0", "", "")
        for i in range(len(dimensions) - 1):
            r = math.prod(coefficients[i + 1:])
            partial = generator.new_temp()
            generator.add_expression(partial, str(r), dimensions[i], "*")
            generator.add_expression(p, p, partial, "+")

        generator.add_expression(p, p, dimensions[len(dimensions) - 1], "+")

        p_deepness = environment.get_variable_p_deepness(self.variable_id, 0)
        stack_value = generator.new_temp()
        generator.add_expression(stack_value, "P", str(0 - p_deepness), "+")

        base_heap_address = generator.new_temp()
        generator.add_get_stack(base_heap_address, stack_value)

        final_heap_address = generator.new_temp()

        generator.add_expression(final_heap_address, base_heap_address, p, "+")

        if len(dimensions) != len(the_symbol.dimensions):
            # Referring to a subarray

            vals = list(the_symbol.dimensions.values())
            vals = vals[len(dimensions):]

            new_dic = {}
            for i in range(len(vals)):
                new_dic[i+1] = vals[i]

            return ValueTuple(value=final_heap_address, expression_type=ExpressionType.ARRAY, is_mutable=False,
                              generator=generator, content_type=the_symbol.symbol_type, capacity=vals, is_tmp=True,
                              true_label=[], false_label=[])

        # Normal, should copy

        if the_symbol.symbol_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            # Get original string pointer
            value = generator.new_temp()
            generator.add_get_heap(value, final_heap_address)

            # Set it up on an pointer that will iter it
            pointer = generator.new_temp()
            first_char_heap_address = generator.new_temp()
            generator.add_expression(first_char_heap_address, "H", "", "")

            generator.add_expression(pointer, value, "", "")
            char = generator.new_temp()

            # Iter string
            exit_label = generator.new_label()
            bucle_label = generator.new_label()
            generator.add_label([bucle_label])

            generator.add_get_heap(char, pointer)
            generator.add_if(char, "-1", "==", exit_label)
            generator.add_set_heap("H", char)
            generator.add_next_heap()
            generator.add_expression(pointer, pointer, "1", "+")
            generator.add_goto(bucle_label)

            generator.add_label([exit_label])
            generator.add_set_heap("H", "-1")
            generator.add_next_heap()

            return ValueTuple(value=first_char_heap_address, expression_type=the_symbol.symbol_type, is_mutable=False,
                              generator=generator, content_type=the_symbol.symbol_type, capacity=None, is_tmp=True,
                              true_label=[], false_label=[])

        # Normal value
        value = generator.new_temp()
        generator.add_get_heap(value, final_heap_address)

        t = generator.new_temp()
        generator.add_expression(t, "H", "", "")
        generator.add_set_heap("H", value)
        generator.add_next_heap()

        return ValueTuple(value=t, expression_type=the_symbol.symbol_type, is_mutable=False, generator=generator,
                          content_type=the_symbol.symbol_type, capacity=None, is_tmp=True,
                          true_label=[], false_label=[])

        # TODO Vector
        # if isinstance(the_symbol, VectorSymbol):
        #     print("vect, not array lmao")
        #     if the_symbol.deepness < len(dimensions):
        #         error_msg = f'La profundidad del vector es menor a la ingresada'
        #         log_semantic_error(error_msg, self.line, self.column)
        #         raise SemanticError(error_msg, self.line, self.column)
        #
        #     returning = the_symbol.value
        #     aux = the_symbol.deepness
        #     for i in range(len(dimensions)):
        #         # print(f"requested:{dimensions[i]} existing:{the_symbol.dimensions[i+1]}")
        #         if dimensions[i] > len(returning):
        #             error_msg = f'Las dimensiones del vector son menores a las ingresadas'
        #             log_semantic_error(error_msg, self.line, self.column)
        #             raise SemanticError(error_msg, self.line, self.column)
        #
        #         returning = returning[dimensions[i]].value
        #
        #     if isinstance(returning, ValueTuple):
        #         return ValueTuple(_type=returning._type, value=returning.value, is_mutable=the_symbol.is_mutable,
        #                           content_type=the_symbol.content_type, capacity=the_symbol.capacity)
        #
        #     if isinstance(returning, list):
        #         return ValueTuple(_type=the_symbol.symbol_type, value=returning, is_mutable=the_symbol.is_mutable,
        #                           content_type=the_symbol.content_type, capacity=the_symbol.capacity)
        #
        #     return ValueTuple(_type=the_symbol.content_type, value=returning, is_mutable=the_symbol.is_mutable,
        #                       content_type=the_symbol.content_type, capacity=the_symbol.capacity)

        # # ARRAY:
        #
        # if len(the_symbol.dimensions.keys()) < len(dimensions):
        #     error_msg = f'La profundidad del array es menor a la ingresada'
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)
        #
        # returning = the_symbol.value
        # for i in range(len(dimensions)):
        #     # print(f"requested:{dimensions[i]} existing:{the_symbol.dimensions[i+1]}")
        #     if dimensions[i] > the_symbol.dimensions[i+1]:
        #         error_msg = f'Las dimensiones del array son menores a las ingresadas'
        #         log_semantic_error(error_msg, self.line, self.column)
        #         raise SemanticError(error_msg, self.line, self.column)
        #
        #     returning = returning[dimensions[i]].value
        #
        # if isinstance(returning, ValueTuple):
        #     return ValueTuple(_type=returning._type, value=returning.value, is_mutable=the_symbol.is_mutable,
        #                       content_type=None, capacity=None)
        # return ValueTuple(_type=the_symbol.symbol_type, value=returning, is_mutable=the_symbol.is_mutable,
        #                   content_type=None, capacity=None)
