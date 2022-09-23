from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from returns.ast_return import ASTReturn

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
            vector_symbol: VectorSymbol = the_symbol
            return ValueTuple(value=ExpressionType.VECTOR, expression_type=vector_symbol.symbol_type,
                              is_mutable=vector_symbol.is_mutable, generator=Generator(),
                              content_type=vector_symbol.symbol_type, capacity=vector_symbol.capacity, is_tmp=True,
                              true_label=[""], false_label=[""])
        #TODO check, this may need stack referencing in a tmp and then assigning that, idk

        if isinstance(the_symbol, ArraySymbol):
            array_symbol: ArraySymbol = the_symbol

            generator = Generator()
            generator.add_comment(f"-------------------------------Variable Reference of {self.variable_id} as array"
                                  f"-------------------------------")
            generator.add_comment("var_ref::Calculated offset internally")
            # TODO check if this is correct lol
            p_deepness = environment.get_variable_p_deepness(self.variable_id, 0)

            ref_position = generator.new_temp()
            generator.add_expression(ref_position, "P", str(0-p_deepness), "+")

            heap_address = generator.new_temp()
            generator.add_comment("var_ref::Get the symbol stack value")
            generator.add_get_stack(heap_address, ref_position)

            pass

            return ValueTuple(value=heap_address, expression_type=ExpressionType.ARRAY,
                              is_mutable=the_symbol.is_mutable, generator=generator,
                              content_type=the_symbol.symbol_type, capacity=the_symbol.symbol_type, is_tmp=True,
                              true_label=[""], false_label=[""])

        # TODO check, this may need stack referencing in a tmp and then assigning that, idk
        generator = Generator()
        generator.add_comment(f"-------------------------------Variable Reference of {self.variable_id}"
                              f"-------------------------------")
        # Normal symbols other than array and vectors should be copied
        stack_address = generator.new_temp()
        generator.add_expression(stack_address, "P", the_symbol.stack_position, "+")

        value = generator.new_temp()
        generator.add_get_stack(value, stack_address)

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

        generator.add_expression(char, "-1", "==", exit_label)

        generator.add_set_heap("H", char)
        generator.add_next_heap()
        generator.add_goto(bucle_label)
        generator.add_label([exit_label])
        generator.add_set_heap("H", "-1")
        generator.add_next_heap()

        return ValueTuple(value=first_char_heap_address, expression_type=the_symbol.symbol_type,
                          is_mutable=the_symbol.is_mutable, generator=generator, content_type=the_symbol.symbol_type,
                          capacity=None, is_tmp=True, true_label=[""], false_label=[""])

