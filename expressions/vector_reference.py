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


class VectorReference(Expression):

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

        if not isinstance(the_symbol, VectorSymbol):
            error_msg = f'Variable {self.variable_id} fue referida (indexada) como array sin serlo.'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        generator = Generator()
        generator.add_comment(f"-------------------------------Vector Reference of {self.variable_id} as vector"
                              f"-------------------------------")

        if len(self.indexes) > the_symbol.deepness:
            error_msg = f'La profundidad del vector es menor a la ingresada'
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

        generator.add_comment("Mapping final address of vector")
        p = generator.new_temp()
        generator.add_expression(p, "0", "", "")

        p_deepness = environment.get_variable_p_deepness(self.variable_id, 0)
        stack_value = generator.new_temp()
        generator.add_expression(stack_value, "P", str(0 - p_deepness), "+")

        base_heap_address = generator.new_temp()
        generator.add_get_stack(base_heap_address, stack_value)

        # Every first vector element holds 4 values:
        # 1: length
        # 2: capacity
        # 3: element, default_heap_value if not set
        # 4: ptr_to_next_element, -1 if non

        # Every next element holds 2 values:
        # 1: element
        # 2: pointer no next, -1 if non
        t_pointer = generator.new_temp()
        generator.add_expression(t_pointer, base_heap_address, "", "")
        for i in range(len(dimensions)):
            dim = dimensions[i]

            counter = generator.new_temp()

            l_not_index_out_of_bounds = generator.new_label()
            generator.add_expression(counter, dim, "", "")
            length = generator.new_temp()
            generator.add_get_heap(length, t_pointer)
            generator.add_if(counter, length, "<", l_not_index_out_of_bounds)

            generator.add_print_message(f"<VectorReference>r->{self.line} c->{self.column}::Index out of bounds")
            generator.add_error_return("7")

            generator.add_label([l_not_index_out_of_bounds])

            # Offset pointer to act as a "normal element" rather than header

            generator.add_expression(t_pointer, t_pointer, "2", "+")  # offsets to element

            l_loop = generator.new_label()
            l_arrived = generator.new_label()

            generator.add_label([l_loop])
            generator.add_if(counter, "0", "==", l_arrived)

            generator.add_expression(t_pointer, t_pointer, "1", "+")  # offsets to ptr_next
            generator.add_get_heap(t_pointer, t_pointer)
            generator.add_expression(counter, counter, "1", "-")
            generator.add_goto(l_loop)

            generator.add_label([l_arrived])
            if i != len(dimensions)-1:
                generator.add_comment("access pointer to next vect")
                generator.add_get_heap(t_pointer, t_pointer)

        final_heap_address = generator.new_temp()
        # generator.add_get_heap(final_heap_address, t_pointer)
        generator.add_expression(final_heap_address, t_pointer, "", "")

        # #######################################Define index of access####################################

        if len(dimensions) != the_symbol.deepness:
            # Referring to a subarray
            generator.add_get_heap(final_heap_address, final_heap_address)

            deepness = the_symbol.deepness - len(dimensions)
            return ValueTuple(value=final_heap_address, expression_type=ExpressionType.VECTOR, is_mutable=False,
                              generator=generator, content_type=the_symbol.symbol_type, capacity=[deepness],
                              is_tmp=True,
                              true_label=[], false_label=[])

        # #######################################Normal, should copy####################################################

        # Strings
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

        if the_symbol.symbol_type == ExpressionType.BOOL:
            l_true = generator.new_label()
            l_false = generator.new_label()
            generator.add_if(value, "1", "==", l_true)
            generator.add_goto(l_false)
            return ValueTuple(value=value, expression_type=the_symbol.symbol_type, is_mutable=False,
                              generator=generator,
                              content_type=the_symbol.symbol_type, capacity=None, is_tmp=True,
                              true_label=[l_true], false_label=[l_false])

        # TODO will this break? idk, uncomment?
        # t = generator.new_temp()
        # generator.add_expression(t, "H", "", "")
        # generator.add_set_heap("H", value)
        # generator.add_next_heap()

        return ValueTuple(value=value, expression_type=the_symbol.symbol_type, is_mutable=False, generator=generator,
                          content_type=the_symbol.symbol_type, capacity=None, is_tmp=True,
                          true_label=[], false_label=[])
