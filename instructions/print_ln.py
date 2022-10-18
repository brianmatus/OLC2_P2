from typing import List, Union


from errors.semantic_error import SemanticError
import global_config
from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from abstract.expression import Expression
from elements.value_tuple import ValueTuple

from expressions.array_reference import ArrayReference
from expressions.variable_ref import VariableReference
from expressions.array_expression import ArrayExpression
from elements.c_env import ArraySymbol

from generator import Generator


class PrintLN(Instruction):

    def __init__(self, expr_list, has_ln: bool, line: int, column: int):
        super().__init__(line, column)
        self.expr_list: List[Expression] = expr_list
        self.has_ln: bool = has_ln

    def execute(self, env: Environment) -> ExecReturn:

        if self.expr_list[0].expression_type is not ExpressionType.STRING_PRIMITIVE:
            print("println formatter is not string_primitive")
            error_msg = f'El primer argumento de println debería ser un string primitivo'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        r: ValueTuple = self.expr_list[0].execute(env, forced_string=True)
        the_str = r.true_label[0]  # little hack lol

        needed = the_str.count("{}") + the_str.count("{:?}")

        if needed != len(self.expr_list[1:]):
            error_msg = f'La cantidad de elementos de formato y argumentos obtenidos no es la misma'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # r = the_str.find("\\n")
        # the_str.replace("\\n", "\n")
        generator = Generator()
        generator.add_comment(f"<<<-------------------------------PRINTLN------------------------------->>>")

        if len(self.expr_list[1:]) == 0:
            generator.add_print_message(the_str)
            the_str = ""

        for arg in self.expr_list[1:]:
            the_arg = arg.execute(env)
            if the_arg.content_type != ExpressionType.BOOL:
                generator.combine_with(the_arg.generator)

            if isinstance(arg, ArrayExpression):
                the_arg.capacity = list(global_config.extract_dimensions_to_dict(the_arg.value).values())
                flat_array = global_config.flatten_array(arg.value)
                the_arg.content_type = flat_array[0].expression_type

                generator = the_arg.generator
                generator.add_comment(f"-------------------------------println::direct reference of array"
                                      f"-------------------------------")

                # First do all stuff in heap, then get those values/references and make array out of it
                # Why not set values while making it? Because of pointers.
                # String for example would make array heap location not continuous. This avoids that problem.
                values = []
                for expr in flat_array:
                    r = expr.execute(env)
                    generator.combine_with(r.generator)
                    values.append(str(r.value))

                t = generator.new_temp()
                generator.add_expression(t, "H", "", "")
                the_arg.value = t  # idk? xD

                for val in values:
                    generator.add_set_heap("H", val)
                    generator.add_next_heap()

            i1 = the_str.find("{}")  # -1
            i2 = the_str.find("{:?}")  # 4
            next_is_simple = ((i1 < i2) or (i2 == -1)) and (i1 != -1)

            # ######################################## ARRAYS ##########################################################
            if the_arg.expression_type in [ExpressionType.ARRAY, ExpressionType.VECTOR]:
                # print("change for array")
                if next_is_simple:
                    error_msg = f'{{}} fue dado para una variable que es array/vector'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                if the_arg.expression_type == ExpressionType.VECTOR:
                    # if the_arg.expression_type == ExpressionType.ARRAY:
                    generator.add_comment("-----------------##Printing Vector arg")
                    ind = the_str.find("{:?}")
                    message_before = the_str[:ind]
                    generator.add_print_message(message_before)
                    the_str = the_str[ind + 4:]

                    generator.add_comment("---Pointer for value")
                    ptr = generator.new_temp()
                    generator.add_expression(ptr, the_arg.value, "", "")

                    #
                    #
                    #
                    body_generator = Generator()
                    is_first = True
                    the_ptr = generator.new_temp()
                    for i in range(the_arg.capacity[0]):
                        if is_first:
                            traverse_vector_for_print(body_generator, the_arg, the_ptr, True)
                            is_first = False
                        else:
                            the_ptr = traverse_vector_for_print(body_generator, the_arg, the_ptr, False)

                    generator.add_comment("outer assignment of pointer")
                    generator.add_expression(the_ptr, ptr, "", "")
                    generator.combine_with(body_generator)

                    continue

                    # TODO finish implement
                    # raise NotImplementedError()

                # if the_arg.expression_type == ExpressionType.ARRAY:
                generator.add_comment("-----------------##Printing Array arg")
                ind = the_str.find("{:?}")
                message_before = the_str[:ind]
                generator.add_print_message(message_before)
                the_str = the_str[ind + 4:]

                generator.add_comment("---Pointer for value")
                ptr = generator.new_temp()
                generator.add_expression(ptr, the_arg.value, "", "")

                backwards_dimensions = the_arg.capacity[::-1]

                body_generator: Generator = Generator()
                first = True

                offset_for_none = 0  # for arrays without size, need to get it from array_stack_pos + n for n->n-dim

                dims = []
                if backwards_dimensions[0] is None:
                    if isinstance(arg, ArrayExpression):
                        dims = list(global_config.extract_dimensions_to_dict(the_arg.value).values())
                    else:
                        dims = get_dimensions_for_passed_non_fixed_array(generator, arg, env)[::-1]

                for dim in backwards_dimensions:
                    dim = str(dim)
                    t_max = generator.new_temp()
                    generator.add_comment("t_max = dim")
                    if dim == "None":
                        generator.add_comment("non-set size, gathering from stack")
                        dim = dims[offset_for_none]
                        offset_for_none += 1

                    generator.add_expression(t_max, dim, "", "")
                    if first:
                        body_generator = traverse_loop_for_print(body_generator, the_arg, ptr, t_max, True)
                        first = False
                        continue
                    body_generator = traverse_loop_for_print(body_generator, the_arg, ptr, t_max, False)

                generator.add_comment("---Print:Array traverse")
                generator.combine_with(body_generator)
                continue

            # ############################################# Normal Values ##############################################
            allowed_types = [ExpressionType.INT, ExpressionType.USIZE, ExpressionType.FLOAT,
                             ExpressionType.BOOL, ExpressionType.CHAR,
                             ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]

            if the_arg.expression_type not in allowed_types:
                error_msg = f'El tipo {the_arg.expression_type.name} debe ser casteado para usar en print.'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            if not next_is_simple:
                error_msg = f'{{:?}} fue dado para una variable que no es array'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            # print stuff before {} and remove both from str
            ind = the_str.find("{}")
            message_before = the_str[:ind]
            generator.add_print_message(message_before)
            the_str = the_str[ind + 2:]
            # ############################################ For Strings #################################################
            if the_arg.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                generate_normal_string_print(generator, the_arg.value)
                continue
            # ############################################# Primitives #################################################
            generate_normal_primitive_print(the_arg, generator, the_arg.value)
            continue

        if len(the_str) != 0:
            generator.add_print_message(the_str)

        if self.has_ln:
            generator.add_newline()

        return ExecReturn(generator=generator,
                          propagate_break=False, propagate_continue=False, propagate_method_return=False)


def traverse_vector_for_print(generator: Generator, the_arg: ValueTuple, ptr: str,
                            is_first: bool) -> str:

    if is_first:
        generator.add_comment(
            "-------------------------------------START PRINT TRAVERSE OF VECTOR-------------------------------------")
        t_pointer = generator.new_temp()  #FIXME unnecesary? idk test nested first
        generator.add_expression(t_pointer, ptr, "", "")

        l_loop = generator.new_label()
        l_exit = generator.new_label()

        generator.add_printf("c", str(ord("[")))

        length = generator.new_temp()
        generator.add_get_heap(length, t_pointer)

        generator.add_if(length, "0", "==", l_exit)

        generator.add_expression(t_pointer, t_pointer, "2", "+")
        l_avoid_comma = generator.new_label()
        generator.add_goto(l_avoid_comma)

        generator.add_label([l_loop])
        generator.add_printf("c", str(ord(",")))

        generator.add_label([l_avoid_comma])

        if the_arg.content_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            generate_array_string_print(generator, t_pointer)
        else:
            generate_array_primitive_print(the_arg, generator, t_pointer)

        t_next = generator.new_temp()
        generator.add_expression(t_next, t_pointer, "1", "+")
        generator.add_get_heap(t_next, t_next)
        generator.add_if(t_next, "-1", "==", l_exit)

        generator.add_expression(t_pointer, t_next, "", "")

        generator.add_goto(l_loop)

        generator.add_label([l_exit])
        generator.add_printf("c", str(ord("]")))

        generator.add_comment(
            "-------------------------------------END PRINT TRAVERSE OF VECTOR-------------------------------------")
        return ptr


    gen = generator
    generator = Generator()

    the_new_ptr = generator.new_temp()
    generator.add_comment(
        "------------------------------------START PRINT WRAP OF VECTOR------------------------------")
    t_pointer = generator.new_temp()  # FIXME unnecesary? idk test nested first
    generator.add_expression(t_pointer, the_new_ptr, "", "")

    l_loop = generator.new_label()
    l_exit = generator.new_label()

    generator.add_printf("c", str(ord("[")))

    length = generator.new_temp()
    generator.add_get_heap(length, t_pointer)

    generator.add_if(length, "0", "==", l_exit)

    generator.add_expression(t_pointer, t_pointer, "2", "+")
    l_avoid_comma = generator.new_label()
    generator.add_goto(l_avoid_comma)

    generator.add_label([l_loop])
    generator.add_printf("c", str(ord(",")))

    generator.add_label([l_avoid_comma])

    generator.add_get_heap(ptr, t_pointer)

    # ##############################################################################################
    generator.combine_with(gen)
    # ##############################################################################################

    t_next = generator.new_temp()
    generator.add_expression(t_next, t_pointer, "1", "+")
    generator.add_get_heap(t_next, t_next)
    generator.add_if(t_next, "-1", "==", l_exit)

    generator.add_expression(t_pointer, t_next, "", "")

    generator.add_goto(l_loop)

    generator.add_label([l_exit])
    generator.add_printf("c", str(ord("]")))

    generator.add_comment(
        "------------------------------------END PRINT WRAP OF VECTOR------------------------------")

    gen.code = generator.code
    return the_new_ptr




def get_dimensions_for_passed_non_fixed_array(generator: Generator,
                                              arg: Union[ArrayReference, VariableReference,ArrayExpression],
                                              environment: Environment) -> list:

    if type(arg) in [ArrayReference, VariableReference]:
        generator.add_comment("##################non-fixed-array-set##################")
        the_symbol: ArraySymbol = environment.get_variable(arg.variable_id)

        dims = []

        p_deepness = environment.get_variable_p_deepness(arg.variable_id, 0)
        stack_value = generator.new_temp()
        generator.add_expression(stack_value, "P", str(0 - p_deepness), "+")

        for i in range(len(the_symbol.dimensions.keys())):
            t_dim = generator.new_temp()
            dims.append(t_dim)
            generator.add_expression(t_dim, stack_value, str(i+1), "+")
            generator.add_get_stack(t_dim, t_dim)

        return dims

    # if isinstance(arg, list):  # Derived of ArrayExpresion
    #     pass
    #     # TODO to be implemented


def traverse_loop_for_print(generator: Generator, the_arg: ValueTuple, ptr: str, t_max: str,
                            is_first: bool) -> Generator:

    if is_first:
        generator.add_comment(
            "-------------------------------------TRAVERSE OF ARRAY-------------------------------------")
        t_element = generator.new_temp()
        t_counter = generator.new_temp()
        t_mod = generator.new_temp()

        l_loop = generator.new_label()
        l_exit = generator.new_label()

        generator.add_print_message("[")
        generator.add_comment("element = HEAP[(int)ptr]")
        generator.add_get_heap(t_element, ptr)

        if the_arg.content_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            generate_array_string_print(generator, ptr)
        else:
            generate_array_primitive_print(the_arg, generator, ptr)

        generator.add_comment("ptr = ptr + 1")
        generator.add_expression(ptr, ptr, "1", "+")
        generator.add_comment("t_counter0 = 1")
        generator.add_expression(t_counter, "1", "", "")
        generator.add_comment("L_loop:")
        generator.add_label([l_loop])
        generator.add_comment("t_mod0 = (int)t_counter0 % (int)t_max0")
        generator.add_expression(t_mod, f'(int){t_counter}', f'(int){t_max}', "%")
        generator.add_comment("if t_mod0 == 0 goto L_exit0:")
        generator.add_if(t_mod, "0", "==", l_exit)
        generator.add_comment('print(",")')
        generator.add_print_message(",")
        generator.add_comment('element = HEAP[(int)ptr]')
        generator.add_get_heap(t_element, ptr)

        generator.add_comment("print(element)")

        if the_arg.content_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            generate_array_string_print(generator, ptr)
        else:
            generate_array_primitive_print(the_arg, generator, ptr)

        generator.add_comment("ptr = ptr + 1")
        generator.add_expression(ptr, ptr, "1", "+")
        generator.add_comment("t_counter0 = t_counter0 + 1")
        generator.add_expression(t_counter, t_counter, "1", "+")
        generator.add_comment("goto L_loop0")
        generator.add_goto(l_loop)
        generator.add_comment("L_exit0:")
        generator.add_label([l_exit])
        generator.add_comment('print("]")')
        generator.add_print_message("]")
        generator.add_comment("------------------------------------END TRAVERSE OF ARRAY------------------------------")
        return generator

    # ##################################################################################################################
    # Not first? wrap
    to_wrap = Generator()
    to_wrap.combine_with(generator)
    generator = Generator()
    generator.add_comment("----------------------------------------WRAP TRAVERSE OF ARRAY-----------------------------")

    t_counter = generator.new_temp()
    t_mod = generator.new_temp()

    l_loop = generator.new_label()
    l_jump_start = generator.new_label()
    l_exit = generator.new_label()

    generator.add_print_message("[")

    generator.add_expression(t_counter, "0", "", "")
    generator.add_goto(l_jump_start)
    generator.add_label([l_loop])
    generator.add_expression(t_mod, f'(int){t_counter}', f'(int){t_max}', "%")
    generator.add_if(t_mod, "0", "==", l_exit)
    generator.add_print_message(",")
    generator.add_label([l_jump_start])

    generator.combine_with(to_wrap)

    generator.add_expression(t_counter, t_counter, "1", "+")
    generator.add_goto(l_loop)
    generator.add_label([l_exit])
    generator.add_print_message("]")
    generator.add_comment("-----------------------------------END TRAVERSE WRAP OF ARRAY------------------------------")
    return generator


def generate_normal_primitive_print(the_arg: ValueTuple, generator: Generator, ptr: str):
    char = generator.new_temp()
    generator.add_comment("--------------------------------print:normal primitive printing----------------------------")

    match the_arg.content_type:
        case ExpressionType.CHAR:
            generator.add_expression(char, ptr, "", "")
            generator.add_printf("c", f"(int){char}")
        case ExpressionType.INT:
            generator.add_expression(char, ptr, "", "")
            generator.add_printf("i", f"(int){char}")
        case ExpressionType.FLOAT:
            generator.add_expression(char, ptr, "", "")
            generator.add_printf("f", char)
        case ExpressionType.BOOL:
            generator.combine_with(the_arg.generator)
            exit_label = generator.new_label()
            generator.add_label(the_arg.true_label)
            generator.add_print_message("true")
            generator.add_goto(exit_label)
            generator.add_label(the_arg.false_label)
            generator.add_print_message("false")
            generator.add_label([exit_label])
        case _:
            error_msg = f'generate_primitive_print::expression type not detected, is this possible?'
            global_config.log_semantic_error(error_msg, -1, -1)
            raise SemanticError(error_msg, -1, -1)

    generator.add_comment("-------------------------------print:END normal primitive printing-------------------------")


def generate_array_primitive_print(the_arg: ValueTuple, generator: Generator, ptr: str):
    pointer = generator.new_temp()
    generator.add_comment("--------------------------------print:primitive printing--------------------------------")
    generator.add_expression(pointer, ptr, "", "")
    char = generator.new_temp()
    generator.add_get_heap(char, pointer)
    match the_arg.content_type:
        case ExpressionType.CHAR:
            generator.add_printf("c", f"(int){char}")
        case ExpressionType.INT:
            generator.add_printf("i", f"(int){char}")
        case ExpressionType.FLOAT:
            generator.add_printf("f", char)
        case ExpressionType.BOOL:
            l_true = generator.new_label()
            l_exit = generator.new_label()
            generator.add_if(char, "1", "==", l_true)
            generator.add_print_message("false")
            generator.add_goto(l_exit)
            generator.add_label([l_true])
            generator.add_print_message("true")
            generator.add_label([l_exit])
        case _:
            error_msg = f'generate_primitive_print::Array content type not detected, is this possible?'
            global_config.log_semantic_error(error_msg, -1, -1)
            raise SemanticError(error_msg, -1, -1)

    generator.add_comment("-------------------------------print:END primitive printing--------------------------------")


def generate_normal_string_print(generator: Generator, ptr: str):
    exit_label = generator.new_label()

    real_ptr = generator.new_temp()
    generator.add_comment("--------------------------------print:string printing--------------------------------")
    generator.add_expression(real_ptr, ptr, "", "")
    bucle_label = generator.new_label()
    # generator.add_print_message("\"")
    generator.add_label([bucle_label])
    char = generator.new_temp()
    generator.add_get_heap(char, real_ptr)

    generator.add_if(char, "-1", "==", exit_label)

    generator.add_printf("c", f"(int){char}")
    generator.add_expression(real_ptr, real_ptr, "1", "+")
    generator.add_goto(bucle_label)
    generator.add_label([exit_label])
    # generator.add_print_message("\"")
    generator.add_comment("-------------------------------print:END string printing--------------------------------")


def generate_array_string_print(generator: Generator, ptr: str):
    exit_label = generator.new_label()

    pointer = generator.new_temp()
    generator.add_comment("--------------------------------print:string printing--------------------------------")
    generator.add_expression(pointer, ptr, "", "")
    real_ptr = generator.new_temp()
    bucle_label = generator.new_label()
    generator.add_get_heap(real_ptr, pointer)
    generator.add_print_message("\"")
    generator.add_label([bucle_label])
    char = generator.new_temp()
    generator.add_get_heap(char, real_ptr)

    generator.add_if(char, "-1", "==", exit_label)

    generator.add_printf("c", f"(int){char}")
    generator.add_expression(real_ptr, real_ptr, "1", "+")
    generator.add_goto(bucle_label)
    generator.add_label([exit_label])
    generator.add_print_message("\"")
    generator.add_comment("-------------------------------print:END string printing--------------------------------")
