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
        self.expr = expr
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

        gen = Generator()
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
        if self.expr.is_expansion:
            # expr: ValueTuple = self.values.execute(environment)
            # repetitions: ValueTuple = self.expansion_size.execute(environment)
            #
            # if repetitions.expression_type is not ExpressionType.INT:
            #     error_msg = f"La expansion de vector debe tener como cantidad un numero entero." \
            #                 f"(Se obtuvo {repetitions.expression_type})"
            #     global_config.log_semantic_error(error_msg, self.line, self.column)
            #     raise SemanticError(error_msg, self.line, self.column)
            #
            # if repetitions.value < 1:
            #     error_msg = f"La expansion de vector debe ser como minimo 1 (Se obtuvo {repetitions.value})"
            #     global_config.log_semantic_error(error_msg, self.line, self.column)
            #     raise SemanticError(error_msg, self.line, self.column)
            #
            # # FIX ME, should check if last 2 Nones are correct
            # return ValueTuple(value=[expr]*int(repetitions.value), expression_type=ExpressionType.VECTOR,
            #                   is_mutable=False, content_type=None, capacity=None,
            #                   is_tmp=False, true_label=[], false_label=[], generator=Generator())
            # TODO implement
            for i in range(20):
                print(f"array_expression.py::({i}/20 warnings) as expansion, to be implemented")

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
                tmp = tmp[0].values
                continue
            content_type = tmp[0].expression_type
            break

        gen = Generator()
        gen.add_comment("---------Vector Expression-------------")

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



