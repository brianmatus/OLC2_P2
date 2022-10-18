from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType

from errors.semantic_error import SemanticError

from elements.c_env import VectorSymbol
from elements.c_env import ArraySymbol
from elements.c_env import Symbol

import global_config
from generator import Generator


class VariableReference(Expression):

    def __init__(self, variable_id: str, line: int, column: int):
        super().__init__(line, column)
        self.variable_id = variable_id

    def execute(self, environment: Environment) -> ValueTuple:
        the_symbol: Symbol = environment.get_variable(self.variable_id)
        if the_symbol is None:
            print("Variable not defined in scope")
            error_msg = f'Variable {self.variable_id} no esta definida en el ámbito actual'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if isinstance(the_symbol, VectorSymbol):
            array_symbol: VectorSymbol = the_symbol

            generator = Generator()
            generator.add_comment(f"-------------------------------Variable Reference of {self.variable_id} as vector"
                                  f"-------------------------------")
            generator.add_comment("var_ref::Calculated offset internally")
            p_deepness = environment.get_variable_p_deepness(self.variable_id, 0)
            ref_position = generator.new_temp()
            generator.add_expression(ref_position, "P", str(0 - p_deepness), "+")

            heap_address = generator.new_temp()
            generator.add_comment("var_ref::Get the symbol stack value")
            generator.add_get_stack(heap_address, ref_position)

            return ValueTuple(value=heap_address, expression_type=ExpressionType.VECTOR,
                              is_mutable=array_symbol.is_mutable, generator=generator,
                              content_type=array_symbol.symbol_type, capacity=[the_symbol.deepness],
                              is_tmp=True, true_label=[], false_label=[])

        if isinstance(the_symbol, ArraySymbol):
            array_symbol: ArraySymbol = the_symbol

            generator = Generator()
            generator.add_comment(f"-------------------------------Variable Reference of {self.variable_id} as array"
                                  f"-------------------------------")
            generator.add_comment("var_ref::Calculated offset internally")
            p_deepness = environment.get_variable_p_deepness(self.variable_id, 0)
            ref_position = generator.new_temp()
            generator.add_expression(ref_position, "P", str(0-p_deepness), "+")

            heap_address = generator.new_temp()
            generator.add_comment("var_ref::Get the symbol stack value")
            generator.add_get_stack(heap_address, ref_position)

            return ValueTuple(value=heap_address, expression_type=ExpressionType.ARRAY,
                              is_mutable=array_symbol.is_mutable, generator=generator,
                              content_type=array_symbol.symbol_type, capacity=list(array_symbol.dimensions.values()),
                              is_tmp=True, true_label=[], false_label=[])

        generator = Generator()
        generator.add_comment(f"-------------------------------Variable Reference of {self.variable_id}"
                              f"-------------------------------")

        p_deepness = environment.get_variable_p_deepness(self.variable_id, 0)
        stack_address = generator.new_temp()
        generator.add_expression(stack_address, "P", str(0 - p_deepness), "+")

        value = generator.new_temp()
        generator.add_get_stack(value, stack_address)

        if the_symbol.symbol_type == ExpressionType.BOOL:
            true_label = generator.new_label()
            false_label = generator.new_label()
            generator.add_if(value, "1", "==", true_label)
            generator.add_goto(false_label)

            return ValueTuple(value="dont_use_me", expression_type=the_symbol.symbol_type,
                              is_mutable=the_symbol.is_mutable,
                              generator=generator, content_type=the_symbol.symbol_type, capacity=None, is_tmp=True,
                              true_label=[true_label], false_label=[false_label])

        # Normal symbols other than array and vectors should be copied
        if the_symbol.symbol_type not in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            return ValueTuple(value=value, expression_type=the_symbol.symbol_type, is_mutable=the_symbol.is_mutable,
                              generator=generator, content_type=the_symbol.symbol_type, capacity=None, is_tmp=True,
                              true_label=[""], false_label=[""])

        # if string, need to buffer al heap to other location
        exit_label = generator.new_label()

        pointer = generator.new_temp()
        first_char_heap_address = generator.new_temp()
        generator.add_expression(first_char_heap_address, "H", "", "")

        generator.add_expression(pointer, value, "", "")
        char = generator.new_temp()
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

        return ValueTuple(value=first_char_heap_address, expression_type=the_symbol.symbol_type,
                          is_mutable=the_symbol.is_mutable, generator=generator, content_type=the_symbol.symbol_type,
                          capacity=None, is_tmp=True, true_label=[""], false_label=[""])
