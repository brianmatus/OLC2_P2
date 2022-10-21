import errors.semantic_error
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from element_types.arithmetic_type import ArithmeticType

import global_config
from generator import Generator


class Arithmetic(Expression):

    def __init__(self, left: Expression, right: Expression,
                 arithmetic_type: ArithmeticType, expression_type: ExpressionType,
                 line: int, column: int):
        super().__init__(line, column)
        self.left = left
        self.right = right
        self.arithmetic_type = arithmetic_type
        self.expression_type = expression_type

    def __str__(self):
        return f'Arithmetic({self.left}, {self.arithmetic_type.name}, {self.right}'

    def execute(self, environment: Environment) -> ValueTuple:

        left: ValueTuple = self.left.execute(environment)
        right: ValueTuple = self.right.execute(environment)

        self.expression_type = left.content_type

        generator = Generator()
        match self.arithmetic_type:

            case ArithmeticType.POW_INT:

                if left.expression_type != ExpressionType.INT or right.expression_type != ExpressionType.INT:

                    error_msg = f"Operación Aritmética POW {left.expression_type.name} <->" \
                                f"{right.expression_type.name} es invalida."
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

                # <a code>
                # <b code>
                # generator.code = left.generator.code + right.generator.code
                generator = left.generator.combine_with(right.generator)

                tf = generator.new_temp()
                t1 = generator.new_temp()

                label_loop = generator.new_label()
                label_end = generator.new_label()
                label_exit = generator.new_label()

                # tf = 1
                generator.add_expression(tf, "1", "", "")

                # t1 = b.val
                generator.add_expression(t1, str(right.value), "", "")

                # if b.val >= 0 goto Loop
                generator.add_if(right.value, "0", ">=", label_loop)

                # t1 = 0 - t1  //make positive
                generator.add_expression(t1, "0", t1, "-")

                # Loop:
                generator.add_label([label_loop])

                # if t1 == 0 then goto End
                generator.add_if(t1, "0", "==", label_end)

                # tf = tf * a.val
                generator.add_expression(tf, tf, left.value, "*")

                # t1 = t1 - 1
                generator.add_expression(t1, t1, "1", "-")

                # goto Loop
                generator.add_goto(label_loop)

                # End:
                generator.add_label([label_end])

                # if b.val >= 0 goto Exit
                generator.add_if(right.value, "0", ">=", label_exit)

                # tf = 1 / tf
                generator.add_expression(tf, "1", tf, "/")

                generator.add_label([label_exit])

                return ValueTuple(tf, ExpressionType.INT, False, generator, ExpressionType.INT, None, True, [], [])

            case ArithmeticType.POW_FLOAT:
                error_msg = f"Not implemented in 3-address-code"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.SUM:

                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    # generator.code = left.generator.code + right.generator.code
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "+")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        # generator.code = left.generator.code + right.generator.code
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, left.value, right.value, "+")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        # generator.code = left.generator.code + right.generator.code
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, left.value, right.value, "+")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    # generator.code = left.generator.code + right.generator.code
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "+")
                    return ValueTuple(new_tmp, ExpressionType.FLOAT, False,
                                      generator, ExpressionType.FLOAT, None, True, [], [])

                # &str + String
                a = left.expression_type == ExpressionType.STRING_PRIMITIVE \
                    and right.expression_type == ExpressionType.STRING_CLASS
                # String + &str
                b = left.expression_type == ExpressionType.STRING_CLASS \
                    and right.expression_type == ExpressionType.STRING_PRIMITIVE

                if a or b:
                    # generator.code = left.generator.code + right.generator.code
                    generator = left.generator.combine_with(right.generator)

                    # if string, need to buffer al heap to other location
                    exit_label = generator.new_label()
                    exit2_label = generator.new_label()

                    pointer = generator.new_temp()
                    first_char_heap_address = generator.new_temp()
                    generator.add_expression(first_char_heap_address, "H", "", "")

                    generator.add_expression(pointer, left.value, "", "")
                    char = generator.new_temp()

                    # #####################################
                    bucle_label = generator.new_label()
                    bucle2_label = generator.new_label()
                    generator.add_label([bucle_label])

                    generator.add_get_heap(char, pointer)
                    generator.add_if(char, "-1", "==", exit_label)
                    generator.add_set_heap("H", char)
                    generator.add_next_heap()
                    generator.add_expression(pointer, pointer, "1", "+")
                    generator.add_goto(bucle_label)

                    generator.add_label([exit_label])
                    generator.add_expression(pointer, right.value, "", "")

                    generator.add_label([bucle2_label])
                    generator.add_get_heap(char, pointer)
                    generator.add_if(char, "-1", "==", exit2_label)
                    generator.add_set_heap("H", char)
                    generator.add_next_heap()
                    generator.add_expression(pointer, pointer, "1", "+")
                    generator.add_goto(bucle2_label)

                    generator.add_label([exit2_label])
                    generator.add_set_heap("H", "-1")
                    generator.add_next_heap()
                    return ValueTuple(value=first_char_heap_address, expression_type=ExpressionType.STRING_CLASS,
                                      is_mutable=False, generator=generator,
                                      content_type=ExpressionType.STRING_CLASS,
                                      capacity=None, is_tmp=True, true_label=[""], false_label=[""])

                error_msg = f"Operación Aritmética SUMA " \
                            f"{left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.SUB:
                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    # generator.code = left.generator.code + right.generator.code
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "-")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])

                # USIZE
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.USIZE:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "-")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])

                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "+")
                    return ValueTuple(new_tmp, ExpressionType.FLOAT, False,
                                      generator, ExpressionType.FLOAT, None, True, [], [])

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        generator = left.generator.combine_with(right.generator)

                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, left.value, right.value, "-")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, left.value, right.value, "-")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                error_msg = f"Operación Aritmética RESTA " \
                            f"{left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.MULT:
                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "*")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, left.value, right.value, "*")
                    return ValueTuple(new_tmp, ExpressionType.FLOAT, False,
                                      generator, ExpressionType.FLOAT, None, True, [], [])

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, left.value, right.value, "*")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, left.value, right.value, "*")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                error_msg = f"Operación Aritmética MULTIPLICACIÓN " \
                            f"{left.expression_type.name}<-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.DIV:

                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()

                    not_div_by_zero_label = generator.new_label()
                    generator.add_if(right.value, "0", "!=", not_div_by_zero_label)
                    generator.add_print_message(f"ERROR SEMANTIC: Division por 0 "
                                                f"en linea:{self.line} columna:{self.column}")
                    generator.add_error_return("1")
                    generator.add_label([not_div_by_zero_label])

                    generator.add_expression(new_tmp, left.value, f"(double) {right.value}", "/")
                    return ValueTuple(new_tmp, ExpressionType.FLOAT, False,
                                      generator, ExpressionType.FLOAT, None, True, [], [])
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()

                    not_div_by_zero_label = generator.new_label()
                    generator.add_if(right.value, "0", "!=", not_div_by_zero_label)
                    generator.add_print_message(f"ERROR SEMANTIC: Division por 0 "
                                                f"en linea:{self.line} columna:{self.column}\n")
                    generator.add_error_return("1")
                    generator.add_label([not_div_by_zero_label])

                    generator.add_expression(new_tmp, left.value, right.value, "/")
                    return ValueTuple(new_tmp, ExpressionType.FLOAT, False,
                                      generator, ExpressionType.FLOAT, None, True, [], [])

                error_msg = f"Operación Aritmética DIVISION " \
                            f"{left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.MOD:
                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, f'(int){left.value}', f'(int){right.value}', "%")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, f'(int){left.value}', f'(int){right.value}', "%")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, f'(int){left.value}', f'(int){right.value}', "%")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        generator = left.generator.combine_with(right.generator)
                        new_tmp = generator.new_temp()
                        generator.add_expression(new_tmp, f'(int){left.value}', f'(int){right.value}', "%")
                        return ValueTuple(new_tmp, ExpressionType.USIZE, False,
                                          generator, ExpressionType.USIZE, None, True, [], [])

                error_msg = f"Operación Aritmética MODULAR " \
                            f"{left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.NEG:

                # INT
                if left.expression_type == ExpressionType.INT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, "", left.value, "-")
                    return ValueTuple(new_tmp, ExpressionType.INT, False,
                                      generator, ExpressionType.INT, None, True, [], [])
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT:
                    generator = left.generator.combine_with(right.generator)
                    new_tmp = generator.new_temp()
                    generator.add_expression(new_tmp, "", left.value, "-")
                    return ValueTuple(new_tmp, ExpressionType.FLOAT, False,
                                      generator, ExpressionType.FLOAT, None, True, [], [])

                error_msg = f"Operación Aritmética MODULAR " \
                            f"{left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case _:
                print("ERROR??? Unknown arithmetic type?")
