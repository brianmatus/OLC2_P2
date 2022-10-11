import math
from typing import List, Union

from errors.semantic_error import SemanticError
from element_types.func_call_arg import FuncCallArg
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from elements.c_env import Symbol
from elements.c_env import ArraySymbol
from elements.c_env import VectorSymbol
from expressions.array_reference import ArrayReference
from expressions.variable_ref import VariableReference
from expressions.literal import Literal
from expressions.array_expression import ArrayExpression
from expressions.type_casting import TypeCasting
import copy

from element_types.logic_type import LogicType
from global_config import log_semantic_error
from generator import Generator


class ParameterFunctionCallE(Expression):

    def __init__(self, variable_id: Union[Expression, str], function_id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)

        self.variable_id = variable_id
        self.function_id = function_id
        self.params = params

    def execute(self, environment: Environment) -> ValueTuple:

        # print("-------------------param func call-------------------")
        # print(self.variable_id)
        # print(self.function_id)
        # print(self.params)

        # print(self.variable_id)
        # print(type(self.variable_id))

        if isinstance(self.variable_id, str):
            self.variable_id = VariableReference(self.variable_id, self.line, self.column)

        if isinstance(self.variable_id, ArrayReference):

            result = self.variable_id.execute(environment)
            if result.expression_type == ExpressionType.ARRAY:
                if self.function_id == "to_string":
                    generator = Generator()
                    generator.add_comment(
                        f"-------------------------------Parameter Func Call::to_string for array"
                        f"-------------------------------")
                    generator.combine_with(result.generator)
                    # TODO to be implemented
                    generator.add_comment("---Pointer for value")
                    ptr = generator.new_temp()
                    generator.add_expression(ptr, result.value, "", "")

                    backwards_dimensions = result.capacity[::-1]

                    string_result = generator.new_temp()
                    generator.add_expression(string_result, "H", "", "")

                    body_generator: Generator = Generator()

                    first = True

                    offset_for_none = 0  # for arrays without size, need to get it from array_stack_pos + n for n->n-dim

                    dims = []
                    if backwards_dimensions[0] is None:
                        # TODO reverse needed?
                        dims = get_dimensions_for_passed_non_fixed_array(generator, self.variable_id, environment)[::-1]

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
                            body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, True)
                            first = False
                            continue
                        body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, False)

                    generator.add_comment("---Print:Array traverse")
                    generator.combine_with(body_generator)
                    generator.add_set_heap("H", "-1")
                    generator.add_next_heap()
                    return ValueTuple(value=string_result, expression_type=ExpressionType.STRING_CLASS, is_mutable=True,
                                      generator=generator, content_type=ExpressionType.STRING_CLASS, capacity=None,
                                      is_tmp=True, true_label=[], false_label=[])

                if self.function_id == "len":
                    if result.capacity[0] is None:
                        dims = get_dimensions_for_passed_non_fixed_array(
                            result.generator, self.variable_id, environment)
                        return ValueTuple(value=dims[len(self.variable_id.indexes)],
                                          expression_type=ExpressionType.INT, is_mutable=True,
                                          generator=result.generator, content_type=ExpressionType.INT,
                                          capacity=None,
                                          is_tmp=True, true_label=[], false_label=[])

                    return ValueTuple(value=result.capacity[0], expression_type=ExpressionType.INT, is_mutable=True,
                                      generator=result.generator, content_type=ExpressionType.INT, capacity=None,
                                      is_tmp=True, true_label=[], false_label=[])

            # Result is primitive
            if self.function_id == "to_string":
                if result.expression_type in [ExpressionType.STRING_PRIMITIVE,  ExpressionType.STRING_CLASS,
                                              ExpressionType.CHAR]:
                    result.expression_type = ExpressionType.STRING_CLASS
                    return result

                # TODO Check for booleans
                # i64, f64

                init = result.generator.new_temp()
                result.value = init
                result.generator.add_expression(init, "H", "", "")

                generate_array_or_normal_primitive_stringify(result, result.generator, result.value, False)
                result.expression_type = ExpressionType.STRING_CLASS
                result.generator.add_set_heap("H", "-1")
                result.generator.add_next_heap()

        elif isinstance(self.variable_id, VariableReference):
            result = self.variable_id.execute(environment)
            pass

            # TODO check for vector
            # TODO check for struct

            if result.expression_type == ExpressionType.ARRAY:
                if self.function_id == "to_string":
                    generator = Generator()
                    generator.combine_with(result.generator)
                    generator.add_comment("---Pointer for value")
                    ptr = generator.new_temp()
                    generator.add_expression(ptr, result.value, "", "")

                    backwards_dimensions = result.capacity[::-1]

                    string_result = generator.new_temp()
                    generator.add_expression(string_result, "H", "", "")

                    body_generator: Generator = Generator()

                    first = True

                    offset_for_none = 0  # for arrays without size, need to get it from array_stack_pos + n for n->n-dim

                    dims = []
                    if backwards_dimensions[0] is None:
                        # TODO reverse needed?
                        dims = get_dimensions_for_passed_non_fixed_array(generator, self.variable_id, environment)[::-1]

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
                            body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, True)
                            first = False
                            continue
                        body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, False)

                    generator.add_comment("---Print:Array traverse")
                    generator.combine_with(body_generator)
                    generator.add_set_heap("H", "-1")
                    generator.add_next_heap()
                    return ValueTuple(value=string_result, expression_type=ExpressionType.STRING_CLASS, is_mutable=True,
                                      generator=generator, content_type=ExpressionType.STRING_CLASS, capacity=None,
                                      is_tmp=True, true_label=[], false_label=[])

                if self.function_id == "len":

                    if result.capacity[0] is None:
                        dims = get_dimensions_for_passed_non_fixed_array(
                            result.generator, self.variable_id, environment)
                        return ValueTuple(value=dims[0], expression_type=ExpressionType.INT, is_mutable=True,
                                          generator=result.generator, content_type=ExpressionType.INT, capacity=None,
                                          is_tmp=True, true_label=[], false_label=[])

                    return ValueTuple(value=result.capacity[0], expression_type=ExpressionType.INT, is_mutable=True,
                                      generator=result.generator, content_type=ExpressionType.INT, capacity=None,
                                      is_tmp=True, true_label=[], false_label=[])

            # Result is primivite
            if self.function_id == "to_string":
                if result.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS,
                                              ExpressionType.CHAR]:
                    result.expression_type = ExpressionType.STRING_CLASS
                    return result

                # TODO Check for booleans
                # i64, f64

                init = result.generator.new_temp()
                result.value = init
                result.generator.add_expression(init, "H", "", "")
                generate_array_or_normal_primitive_stringify(result, result.generator, result.value, False)
                result.expression_type = ExpressionType.STRING_CLASS
                result.generator.add_set_heap("H", "-1")
                result.generator.add_next_heap()
                return result


        elif isinstance(self.variable_id, Literal):
            if self.function_id == "to_string":
                r = self.variable_id.execute(environment)

                if r.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    return r

                new_lit = Literal(str(r.value), ExpressionType.STRING_CLASS, self.line, self.column)
                return new_lit.execute(environment)

            if self.function_id == "len":
                return self.value_len(self.variable_id, environment)


            if self.function_id == "abs":
                return self.value_abs(self.variable_id, environment)

        elif isinstance(self.variable_id, TypeCasting):
            r = self.variable_id.execute(environment)
            the_symbol = Symbol("type_casting_forced_symbol", r._type, r.value, True, False)

        elif isinstance(self.variable_id, ParameterFunctionCallE):
            # FIXME check resulting function type
            if self.function_id == "to_string":
                r = self.variable_id.execute(environment)
                return ValueTuple(str(r.value), ExpressionType.STRING_CLASS, False, None, None)


        # TODO Check if is struct
        #  elif isinstance(the_symbol, struct_symbol):

        # TODO Check if present in struct
        print("missing stuff")
        error_msg = f"Acceso a parametro de variable invalido.."
        log_semantic_error(error_msg, self.line, self.column)
        raise SemanticError(error_msg, self.line, self.column)

    def native_to_string(self, the_symbol) -> ValueTuple:
        # allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
        #                  ElementType.BOOL, ElementType.CHAR,
        #                  ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]
        # if not the_symbol._type in allowed_types:
        #     error_msg = f".to_string() solo puede ser usado con i64, usize, f64, bool, char, String, &str."
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)
        #
        # return ValueTuple(str(the_symbol.value), ElementType.STRING_CLASS, False)
        pass

    def native_abs(self, the_symbol) -> ValueTuple:
        # allowed_types = [ElementType.INT, ElementType.FLOAT]
        # if not the_symbol._type in allowed_types:
        #     error_msg = f".native_abs() solo puede ser usado con i64, f64."
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)
        #
        # return ValueTuple(abs(the_symbol.value), the_symbol._type, False, None, None)
        pass

    def native_sqrt(self, the_symbol) -> ValueTuple:
        # allowed_types = [ElementType.INT, ElementType.FLOAT]
        # if not the_symbol._type in allowed_types:
        #     error_msg = f".native_sqrt() solo puede ser usado con i64, f64."
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)
        #
        # return ValueTuple(math.sqrt(the_symbol.value), ElementType.FLOAT, False, None, None)
        pass

    def native_clone(self, the_symbol) -> ValueTuple:
        # allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
        #                  ElementType.BOOL, ElementType.CHAR,
        #                  ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]
        # if not the_symbol._type in allowed_types:
        #     error_msg = f".native_sqrt() solo puede ser usado i64, usize, f64, bool, char, String, &str."
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)
        #
        # return ValueTuple(the_symbol.value, the_symbol._type, False, None, None)
        pass

    def native_array_clone(self, the_symbol) -> ValueTuple:
        # allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
        #                  ElementType.BOOL, ElementType.CHAR,
        #                  ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]
        # if not the_symbol._type in allowed_types:
        #     error_msg = f".native_sqrt() solo puede ser usado i64, usize, f64, bool, char, String, &str."
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)
        #
        # return ValueTuple(copy.deepcopy(the_symbol.value), the_symbol._type, False, None, None)
        pass

    def native_len(self, the_symbol, env: Environment) -> ValueTuple:
        allowed_types = [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS, ExpressionType.ARRAY]

        if isinstance(the_symbol, VectorSymbol):
            # TODO implement
            # return ValueTuple(len(the_symbol.value), ElementType.INT, False, the_symbol.content_type,
            #                   the_symbol.capacity)
            pass

        generator = Generator()
        if isinstance(the_symbol, ArraySymbol):
            return ValueTuple(the_symbol.dimensions[1], ExpressionType.INT, is_mutable=True, generator=generator,
                              content_type=ExpressionType.INT, capacity=None, is_tmp=True,
                              true_label=[], false_label=[])

        if the_symbol.symbol_type not in allowed_types:
            error_msg = f".len() solo puede ser usado con String, &str arrays y vectores. " \
                        f"({the_symbol.symbol_type.name} fue dado)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        var_ref = VariableReference(the_symbol.symbol_id, -1, -1)
        ref = var_ref.execute(env)
        generator.combine_with(ref.generator)

        counter = generator.new_temp()
        generator.add_expression(counter, "0", "", "")

        exit_label = generator.new_label()

        real_ptr = generator.new_temp()
        generator.add_expression(real_ptr, ref.value, "", "")
        bucle_label = generator.new_label()
        generator.add_label([bucle_label])
        char = generator.new_temp()
        generator.add_get_heap(char, real_ptr)

        generator.add_if(char, "-1", "==", exit_label)

        generator.add_expression(counter, counter, "1", "+")
        generator.add_expression(real_ptr, real_ptr, "1", "+")
        generator.add_goto(bucle_label)
        generator.add_label([exit_label])

        return ValueTuple(counter, ExpressionType.INT, is_mutable=True, generator=generator,
                          content_type=ExpressionType.INT, capacity=None, is_tmp=True,
                          true_label=[], false_label=[])
        pass

    def value_len(self, literal_expr, env: Environment) -> ValueTuple:
        generator = Generator()
        result = literal_expr.execute(env)
        #  TODO finish implementing

    def value_len(self, literal_expr, env: Environment) -> ValueTuple:
        generator = Generator()
        ref = literal_expr.execute(env)
        generator.combine_with(ref.generator)

        counter = generator.new_temp()
        generator.add_expression(counter, "0", "", "")

        exit_label = generator.new_label()

        real_ptr = generator.new_temp()
        generator.add_expression(real_ptr, ref.value, "", "")
        bucle_label = generator.new_label()
        generator.add_label([bucle_label])
        char = generator.new_temp()
        generator.add_get_heap(char, real_ptr)

        generator.add_if(char, "-1", "==", exit_label)

        generator.add_expression(counter, counter, "1", "+")
        generator.add_expression(real_ptr, real_ptr, "1", "+")
        generator.add_goto(bucle_label)
        generator.add_label([exit_label])

        return ValueTuple(counter, ExpressionType.INT, is_mutable=True, generator=generator,
                          content_type=ExpressionType.INT, capacity=None, is_tmp=True,
                          true_label=[], false_label=[])


def get_dimensions_for_passed_non_fixed_array(generator: Generator,
                                              arg: Union[ArrayReference, VariableReference, ArrayExpression],
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

    if isinstance(arg, list):  # Derived of ArrayExpresion
        print("println.py::get_dimensions_for_passed_non_fixed_array, list instance::to be implemented")


def traverse_loop_for_stringify(generator: Generator, the_arg: ValueTuple, ptr: str, t_max: str,
                            is_first: bool) -> Generator:

    if is_first:
        generator.add_comment(
            "-------------------------------------STRINGIFY TRAVERSE OF ARRAY-------------------------------------")
        t_element = generator.new_temp()
        t_counter = generator.new_temp()
        t_mod = generator.new_temp()

        l_loop = generator.new_label()
        l_exit = generator.new_label()

        generator.add_set_heap("H", str(ord("[")))
        generator.add_next_heap()
        generator.add_comment("element = HEAP[(int)ptr]")
        generator.add_get_heap(t_element, ptr)

        if the_arg.content_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            generate_array_string_stringify(generator, ptr)
        else:
            generate_array_or_normal_primitive_stringify(the_arg, generator, ptr, True)

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

        generator.add_set_heap("H", str(ord(",")))
        generator.add_next_heap()

        generator.add_comment('element = HEAP[(int)ptr]')
        generator.add_get_heap(t_element, ptr)

        generator.add_comment("print(element)")

        if the_arg.content_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            generate_array_string_stringify(generator, ptr)
        else:
            generate_array_or_normal_primitive_stringify(the_arg, generator, ptr, True)

        generator.add_comment("ptr = ptr + 1")
        generator.add_expression(ptr, ptr, "1", "+")
        generator.add_comment("t_counter0 = t_counter0 + 1")
        generator.add_expression(t_counter, t_counter, "1", "+")
        generator.add_comment("goto L_loop0")
        generator.add_goto(l_loop)
        generator.add_comment("L_exit0:")
        generator.add_label([l_exit])
        generator.add_comment('print("]")')
        generator.add_set_heap("H", str(ord("]")))
        generator.add_next_heap()
        generator.add_comment(
            "------------------------------------END STRINGIFY TRAVERSE OF ARRAY------------------------------")
        return generator

    # ##################################################################################################################
    # Not first? wrap
    to_wrap = Generator()
    to_wrap.combine_with(generator)
    generator = Generator()
    generator.add_comment(
        "----------------------------------------STRINGIFY WRAP TRAVERSE OF ARRAY-----------------------------")

    t_counter = generator.new_temp()
    t_mod = generator.new_temp()

    l_loop = generator.new_label()
    l_jump_start = generator.new_label()
    l_exit = generator.new_label()

    generator.add_set_heap("H", str(ord("[")))
    generator.add_next_heap()

    generator.add_expression(t_counter, "0", "", "")
    generator.add_goto(l_jump_start)
    generator.add_label([l_loop])
    generator.add_expression(t_mod, f'(int){t_counter}', f'(int){t_max}', "%")
    generator.add_if(t_mod, "0", "==", l_exit)
    generator.add_set_heap("H", str(ord(",")))
    generator.add_next_heap()
    generator.add_label([l_jump_start])

    generator.combine_with(to_wrap)

    generator.add_expression(t_counter, t_counter, "1", "+")
    generator.add_goto(l_loop)
    generator.add_label([l_exit])
    generator.add_set_heap("H", str(ord("]")))
    generator.add_next_heap()
    generator.add_comment(
        "-----------------------------------END STRINGIFY TRAVERSE WRAP OF ARRAY------------------------------")
    return generator


def generate_array_or_normal_primitive_stringify(the_arg: ValueTuple, generator: Generator, ptr: str, is_array: bool):
    generator.add_comment(
        "--------------------------------print:primitive stringify--------------------------------")

    pointer: str
    char = generator.new_temp()
    if is_array:
        pointer = generator.new_temp()

        generator.add_expression(pointer, ptr, "", "")
        generator.add_get_heap(char, pointer)
    else:
        generator.add_expression(char, ptr, "", "")

    if the_arg.content_type == ExpressionType.CHAR:
        generator.add_set_heap("H", char)
        generator.add_next_heap()
        generator.add_comment(
            "-------------------------------print:END primitive stringify--------------------------------")
        return

    if the_arg.content_type in [ExpressionType.INT, ExpressionType.FLOAT]:
        l_not_zero = generator.new_label()
        l_decimals = generator.new_label()
        l_exit = generator.new_label()

        # 0 short circuit
        generator.add_if(char, "0", "!=", l_not_zero)
        generator.add_set_heap("H", str(ord("0")))
        generator.add_next_heap()
        generator.add_goto(l_exit)

        generator.add_label([l_not_zero])

        # Negative - handle

        l_non_negative = generator.new_label()
        generator.add_if(char, "0", ">=", l_non_negative)
        generator.add_set_heap("H", str(ord("-")))
        generator.add_next_heap()
        generator.add_expression(char, "0", char, "-")

        generator.add_label([l_non_negative])

        ##########################################################################
        # Reduce number to decimal
        t_original_number = generator.new_temp()
        t_number = generator.new_temp()

        generator.add_casting(t_number, char, "int")
        generator.add_casting(t_original_number, char, "int")
        t_decimals = generator.new_temp()
        generator.add_expression(t_decimals, char, t_number, "-")

        t_n = generator.new_temp()
        generator.add_expression(t_n, "0", "", "")
        l_reduction = generator.new_label()
        l_less_than_1 = generator.new_label()
        generator.add_label([l_reduction])
        generator.add_if(t_number, "1", "<", l_less_than_1)
        generator.add_expression(t_n, t_n, "1", "+")

        generator.add_expression(t_number, t_number, "10", "/")
        generator.add_goto(l_reduction)

        # ####################################################################################
        generator.add_label([l_less_than_1])
        l_iter_number = generator.new_label()
        generator.add_if(t_n, "0", "!=", l_iter_number)
        generator.add_set_heap("H", str(ord("0")))
        generator.add_next_heap()
        generator.add_goto(l_decimals)

        l_next_digit = generator.new_label()
        generator.add_label([l_next_digit])
        generator.add_expression(t_n, t_n, "1", "-")
        to_print = generator.new_temp()
        generator.add_expression(to_print, f'(int){t_number}', "10", "%")
        add_number_unicode_to_heap(to_print, generator)

        generator.add_label([l_iter_number])

        generator.add_expression(t_number, t_original_number, "", "")
        generator.add_if(t_n, "0", "<=", l_decimals)

        l_digit_loop = generator.new_label()
        t_iterator = generator.new_temp()
        generator.add_expression(t_iterator, t_n, "1", "-")
        generator.add_label([l_digit_loop])
        generator.add_comment("reached end?")
        generator.add_if(t_iterator, "0", "==", l_next_digit)

        generator.add_comment("still going")
        generator.add_expression(t_number, t_number, "10", "/")
        generator.add_expression(t_iterator, t_iterator, "1", "-")
        generator.add_goto(l_digit_loop)

        # ##############################################################################################################
        generator.add_label([l_decimals])

        if the_arg.content_type == ExpressionType.INT:
            generator.add_label([l_exit])
            return

        generator.add_set_heap("H", str(ord(".")))
        generator.add_next_heap()

        l_decimals_loop = generator.new_label()

        t_places = generator.new_temp()
        # FIXME workaround for this? idk :( hard-coded 8 decimal places
        generator.add_expression(t_places, "8", "", "")

        generator.add_if(t_decimals, "0", "!=", l_decimals_loop)
        generator.add_set_heap("H", str(ord("0")))
        generator.add_next_heap()
        generator.add_goto(l_exit)

        generator.add_label([l_decimals_loop])

        # reached end?
        generator.add_if(t_places, "0", "==", l_exit)

        # still going
        t_displaced = generator.new_temp()
        generator.add_expression(t_displaced, t_decimals, "10", "*")

        t_to_add = generator.new_temp()
        generator.add_casting(t_to_add, t_displaced, "int")

        # generator.add_set_heap("H", t_to_add)
        # generator.add_next_heap()
        add_number_unicode_to_heap(t_to_add, generator)

        generator.add_expression(t_decimals, t_displaced, t_to_add, "-")

        generator.add_expression(t_places, t_places, "1", "-")

        generator.add_goto(l_decimals_loop)

        generator.add_label([l_exit])
        return

    error_msg = f'generate_primitive_print::Array content type not detected, is this possible?'
    log_semantic_error(error_msg, -1, -1)
    raise SemanticError(error_msg, -1, -1)


def generate_array_string_stringify(generator: Generator, ptr: str):
    exit_label = generator.new_label()

    pointer = generator.new_temp()
    generator.add_comment("--------------------------------print:string stringify--------------------------------")
    generator.add_expression(pointer, ptr, "", "")
    real_ptr = generator.new_temp()
    bucle_label = generator.new_label()
    generator.add_get_heap(real_ptr, pointer)

    # generator.add_print_message("\"")
    generator.add_set_heap("H", str(ord("\"")))
    generator.add_next_heap()

    generator.add_label([bucle_label])
    char = generator.new_temp()
    generator.add_get_heap(char, real_ptr)

    generator.add_if(char, "-1", "==", exit_label)

    # generator.add_printf("c", f"(int){char}")
    generator.add_set_heap("H", char)
    generator.add_next_heap()
    generator.add_expression(real_ptr, real_ptr, "1", "+")
    generator.add_goto(bucle_label)
    generator.add_label([exit_label])
    # generator.add_print_message("\"")
    generator.add_set_heap("H", str(ord("\"")))
    generator.add_next_heap()

    generator.add_comment("-------------------------------print:END string stringify--------------------------------")


def add_number_unicode_to_heap(t_n: str, generator: Generator):
    already_added = generator.new_label()
    for i in range(10):
        t_n_plus_1 = generator.new_label()
        generator.add_if(t_n, str(i), "!=", t_n_plus_1)
        generator.add_set_heap("H", str(ord(str(i))))
        generator.add_next_heap()
        generator.add_goto(already_added)
        generator.add_label([t_n_plus_1])
    generator.add_label([already_added])




