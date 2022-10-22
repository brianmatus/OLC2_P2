from typing import Union, List

from errors.semantic_error import SemanticError
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from expressions.literal import Literal

from generator import Generator


import global_config


class VectorExpression(Expression):
    # expr: ArrayExpression (to clone lol) | None
    def __init__(self, expr, capacity: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)
        self.expr: Union[Expression, None] = expr
        self.capacity = capacity

    def execute(self, environment: Environment) -> ValueTuple:


        # Every first vector element holds 4 values:
        # 1: length
        # 2: capacity
        # 3: element, default_heap_value if not set
        # 4: ptr_to_next_element, -1 if non

        # Every next element holds 2 values:
        # 1: element
        # 2: pointer no next, -1 if non

        gen = Generator(environment)
        gen.add_comment("----------------------------------------"
                        "Vector Expression----------------------------------------")

        if self.expr is None:
            if self.capacity is None:  # Vec::new()
                gen.add_comment("Vec::new()")
                t_ptr = gen.new_temp()
                gen.add_expression(t_ptr, "H", "", "")

                # 1: length
                gen.add_set_heap("H", "0")
                gen.add_next_heap()
                # 2: capacity
                gen.add_set_heap("H", "0")
                gen.add_next_heap()
                # 3: element, -6969 if not set
                gen.add_set_heap("H", "-6969")
                gen.add_next_heap()
                # 4: ptr_to_next_element, -1 if non
                gen.add_set_heap("H", "-1")
                gen.add_next_heap()
                return ValueTuple(value=t_ptr, expression_type=ExpressionType.ARRAY, is_mutable=True, generator=gen,
                                  content_type=None, capacity=[0], is_tmp=True,
                                  true_label=[], false_label=[])
            else:  # Vec::with_capacity()
                capacity_result = self.capacity.execute(environment)
                if capacity_result.expression_type not in [ExpressionType.INT, ExpressionType.USIZE]:
                    error_msg = f'La capacidad de un vector debe ser una expresión i64/usize'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                gen.combine_with(capacity_result.generator)

                correct_capacity = gen.new_label()

                gen.add_if(capacity_result.value, "0", ">=", correct_capacity)
                gen.add_print_message("La capacidad ingresada no es valida. debe ser un numero entero positivo")

                gen.add_label([correct_capacity])

                gen.add_comment("Vec::with_capacity()")
                t_ptr = gen.new_temp()
                gen.add_expression(t_ptr, "H", "", "")

                # 1: length
                gen.add_set_heap("H", "0")
                gen.add_next_heap()
                # 2: capacity
                gen.add_set_heap("H", capacity_result.value)
                gen.add_next_heap()
                # 3: element, -6969 if not set
                gen.add_set_heap("H", "-6969")
                gen.add_next_heap()
                # 4: ptr_to_next_element, -1 if non
                gen.add_set_heap("H", "-1")
                gen.add_next_heap()
                return ValueTuple(value=t_ptr, expression_type=ExpressionType.ARRAY, is_mutable=True, generator=gen,
                                  content_type=None, capacity=[0], is_tmp=True,
                                  true_label=[], false_label=[])

        # Normal declaration

        # Definition by expansion
        if self.capacity is not None:
            if not isinstance(self.capacity, Literal):
                error_msg = f'La expansion de un vector debe ser un literal entero/usize'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            repeats = self.capacity.execute(environment)

            if repeats.expression_type not in [ExpressionType.INT, ExpressionType.USIZE]:
                error_msg = f'La expansion de un vector debe ser un literal entero/usize'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            if repeats.value <= 0:
                error_msg = f'La expansion de un vector debe ser mayor a 0'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            result = self.expr.execute(environment)
            # ############################### ACCEPTED ###############################
            # Init it

            # Every first vector element holds 4 values:
            # 1: length
            # 2: capacity
            # 3: element, default_heap_value if not set
            # 4: ptr_to_next_element, -1 if non
            gen.add_comment("#################First element#################")

            first_one = gen.new_temp()
            gen.add_expression(first_one, "H", "", "")

            gen.add_comment("1: length")
            # 1: length
            gen.add_set_heap("H", str(repeats.value))
            gen.add_next_heap()

            # 2: capacity
            gen.add_comment("2: capacity")
            gen.add_set_heap("H", str(repeats.value))
            gen.add_next_heap()

            # 3: element
            gen.add_comment("3: element")
            element_ptr = gen.new_temp()
            gen.add_expression(element_ptr, "H", "", "")
            gen.add_next_heap()

            # 4: ptr_to_next_element
            gen.add_comment("4: ptr_to_next_element")
            next_pointer = gen.new_temp()
            gen.add_expression(next_pointer, "H", "", "")
            gen.add_set_heap("H", "-1")
            gen.add_next_heap()

            # Set value of 3)
            gen.combine_with(result.generator)
            gen.add_set_heap(element_ptr, result.value)

            before_me_next_pointer = next_pointer

            # Every next element holds 2 values:
            # 1: element
            # 2: pointer to next, -1 if non
            for i in range(repeats.value-1):
                gen.add_comment("#################Non-first element#################")

                # ###########################Every next element###########################
                # Link to previous
                gen.add_set_heap(before_me_next_pointer, "H")

                # 1: element
                gen.add_comment("1: element")
                element_ptr = gen.new_temp()
                gen.add_expression(element_ptr, "H", "", "")
                gen.add_next_heap()

                # 2: pointer to next
                gen.add_comment("2: pointer to next")
                next_pointer = gen.new_temp()
                gen.add_expression(next_pointer, "H", "", "")
                gen.add_set_heap("H", "-1")
                gen.add_next_heap()

                # Set value of 1)
                gen.combine_with(result.generator)
                gen.add_set_heap(element_ptr, result.value)

                before_me_next_pointer = next_pointer

            the_capacity = result.capacity

            if the_capacity is None:
                the_capacity = [1]
            else:
                the_capacity = [the_capacity[0]+1]

            return ValueTuple(value=first_one, expression_type=ExpressionType.VECTOR, is_mutable=True, generator=gen,
                              content_type=result.expression_type, capacity=the_capacity, is_tmp=True,
                              true_label=[], false_label=[])

        # ############Definition by list (or by new()/with_capacity() which is handled in this constructor)#############

    # ##################################################################################################################

        # Extract content type
        content_type = None
        tmp = self.expr.value
        deepness = []
        while True:
            deepness.append(len(tmp))
            if len(tmp) <= 0:
                break
            if tmp[0].expression_type in [ExpressionType.ARRAY, ExpressionType.VOID]:
                tmp = tmp[0].expr.value
                continue
            content_type = tmp[0].expression_type
            break

        # TODO unnecessary?
        # gen = Generator()
        # gen.add_comment("---------Vector Expression-------------")

        # Allocating headers

        before_me_next_pointer = None
        first_one = "non_set_vector_error"

        value: Expression
        # Every first vector element holds 4 values:
        # 1: length
        # 2: capacity
        # 3: element, default_heap_value if not set
        # 4: ptr_to_next_element, -1 if non

        # Every next element holds 2 values:
        # 1: element
        # 2: pointer to next, -1 if non
        for value in self.expr.value:

            if before_me_next_pointer is None:  # First one
                gen.add_comment("#################First element#################")

                store_in = gen.new_temp()
                first_one = store_in
                gen.add_expression(store_in, "H", "", "")

                gen.add_comment("1: length")
                # 1: length
                gen.add_set_heap("H", str(len(self.expr.value)))
                gen.add_next_heap()

                # 2: capacity
                gen.add_comment("2: capacity")
                gen.add_set_heap("H", str(len(self.expr.value)))
                gen.add_next_heap()

                # 3: element
                gen.add_comment("3: element")
                element_ptr = gen.new_temp()
                gen.add_expression(element_ptr, "H", "", "")
                gen.add_next_heap()

                # 4: ptr_to_next_element
                gen.add_comment("4: ptr_to_next_element")
                next_pointer = gen.new_temp()
                gen.add_expression(next_pointer, "H", "", "")
                gen.add_set_heap("H", "-1")
                gen.add_next_heap()

                # Set value of 3)
                result = value.execute(environment)
                gen.combine_with(result.generator)
                gen.add_set_heap(element_ptr, result.value)

                before_me_next_pointer = next_pointer
                continue

            gen.add_comment("#################Non-first element#################")

            # ###########################Every next element###########################
            # Link to previous
            gen.add_set_heap(before_me_next_pointer, "H")

            # 1: element
            gen.add_comment("1: element")
            element_ptr = gen.new_temp()
            gen.add_expression(element_ptr, "H", "", "")
            gen.add_next_heap()

            # 2: pointer to next
            gen.add_comment("2: pointer to next")
            next_pointer = gen.new_temp()
            gen.add_expression(next_pointer, "H", "", "")
            gen.add_set_heap("H", "-1")
            gen.add_next_heap()

            # Set value of 1)
            result = value.execute(environment)
            gen.combine_with(result.generator)
            gen.add_set_heap(element_ptr, result.value)

            before_me_next_pointer = next_pointer

        return ValueTuple(value=first_one, expression_type=ExpressionType.VECTOR, is_mutable=True, generator=gen,
                          content_type=content_type, capacity=deepness, is_tmp=True,
                          true_label=[], false_label=[])



