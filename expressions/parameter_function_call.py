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

        # ##############################################################################################################

        if isinstance(self.variable_id, ArrayReference):

            result = self.variable_id.execute(environment)
            if result.expression_type == ExpressionType.ARRAY:
                if self.function_id == "to_string":
                    gen = Generator()
                    gen.add_comment(
                        f"-------------------------------Parameter Func Call::to_string for array"
                        f"-------------------------------")
                    gen.combine_with(result.generator)
                    gen.add_comment("---Pointer for value")
                    ptr = gen.new_temp()
                    gen.add_expression(ptr, result.value, "", "")

                    backwards_dimensions = result.capacity[::-1]

                    string_result = gen.new_temp()
                    gen.add_expression(string_result, "H", "", "")

                    body_generator: Generator = Generator()

                    first = True

                    offset_for_none = 0  # for arrays without size, need to get it from array_stack_pos + n for n->n-dim

                    dims = []
                    if backwards_dimensions[0] is None:
                        # TODO reverse needed?
                        dims = get_dimensions_for_passed_non_fixed_array(gen, self.variable_id, environment)[::-1]

                    for dim in backwards_dimensions:
                        dim = str(dim)
                        t_max = gen.new_temp()
                        gen.add_comment("t_max = dim")
                        if dim == "None":
                            gen.add_comment("non-set size, gathering from stack")
                            dim = dims[offset_for_none]
                            offset_for_none += 1

                        gen.add_expression(t_max, dim, "", "")
                        if first:
                            body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, True)
                            first = False
                            continue
                        body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, False)

                    gen.add_comment("---Print:Array traverse")
                    gen.combine_with(body_generator)
                    gen.add_set_heap("H", "-1")
                    gen.add_next_heap()
                    return ValueTuple(value=string_result, expression_type=ExpressionType.STRING_CLASS, is_mutable=True,
                                      generator=gen, content_type=ExpressionType.STRING_CLASS, capacity=None,
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
                return result

            if self.function_id == "abs":
                if result.expression_type in [ExpressionType.INT, ExpressionType.FLOAT]:
                    t_abs = result.generator.new_temp()
                    l_positive = result.generator.new_label()
                    l_exit = result.generator.new_label()
                    result.generator.add_if(result.value, "0", ">=", l_positive)
                    result.generator.add_expression(t_abs, "0", result.value, "-")
                    result.generator.add_goto(l_exit)
                    result.generator.add_label([l_positive])
                    result.generator.add_expression(t_abs, result.value, "", "")
                    result.generator.add_label([l_exit])
                    result.value = t_abs
                    return result

            if self.function_id == "sqrt":
                if result.expression_type == ExpressionType.FLOAT:
                    gen: Generator = result.generator
                    x = result.value
                    tol = gen.new_temp()
                    x0 = gen.new_temp()
                    root_approx = gen.new_temp()
                    y_n = gen.new_temp()
                    dy_n = gen.new_temp()
                    tol_neg = gen.new_temp()
                    the_div = gen.new_temp()

                    l_while_loop = gen.new_label()
                    l_continue = gen.new_label()
                    l_stop = gen.new_label()

                    gen.add_expression(tol, "1.0", "1000000000000", "/")
                    gen.add_expression(x0, x, "2.0", "/")

                    gen.add_expression(root_approx, x0, "", "")
                    gen.add_expression(y_n, x0, x0, "*")
                    gen.add_expression(y_n, y_n, x, "-")

                    gen.add_expression(dy_n, "2", x0, "*")

                    gen.add_label([l_while_loop])
                    gen.add_expression(tol_neg, "0.0", tol, "-")
                    gen.add_if(tol_neg, y_n, ">=", l_continue)
                    gen.add_if(y_n, tol, ">=", l_continue)
                    gen.add_goto(l_stop)

                    gen.add_label([l_continue])
                    gen.add_expression(the_div, y_n, dy_n, "/")
                    gen.add_expression(root_approx, root_approx, the_div, "-")

                    gen.add_expression(y_n, root_approx, root_approx, "*")
                    gen.add_expression(y_n, y_n, x, "-")
                    gen.add_expression(dy_n, "2.0", x0, "*")
                    gen.add_goto(l_while_loop)

                    gen.add_label([l_stop])
                    gen.add_expression(root_approx, root_approx, "10000000", "*")
                    gen.add_casting(root_approx, root_approx, "int")
                    gen.add_expression(root_approx, root_approx, "10000000", "/")
                    result.value = root_approx
                    return result

        elif type(self.variable_id) in [VariableReference, TypeCasting]:
            result = self.variable_id.execute(environment)
            pass

            # TODO check for struct
            if result.expression_type == ExpressionType.VECTOR:
                if self.function_id == "len":

                    gen = Generator()
                    gen.add_comment("-------------------param func call::var_ref::vector len-------------------")
                    gen.combine_with(result.generator)
                    gen.add_comment("---Pointer for value")
                    value = gen.new_temp()
                    gen.add_expression(value, result.value, "", "")
                    gen.add_get_heap(value, value)

                    return ValueTuple(value=value, expression_type=ExpressionType.INT, is_mutable=True,
                                      generator=gen, content_type=ExpressionType.INT, capacity=None,
                                      is_tmp=True, true_label=[], false_label=[])

                if self.function_id == "capacity":

                    gen = Generator()
                    gen.add_comment("-------------------param func call::var_ref::vector capacity-------------------")
                    gen.combine_with(result.generator)
                    gen.add_comment("---Pointer for value")
                    value = gen.new_temp()
                    gen.add_expression(value, result.value, "1", "+")
                    gen.add_get_heap(value, value)

                    return ValueTuple(value=value, expression_type=ExpressionType.INT, is_mutable=True,
                                      generator=gen, content_type=ExpressionType.INT, capacity=None,
                                      is_tmp=True, true_label=[], false_label=[])

                if self.function_id == "contains":

                    if result.capacity[0] != 1:
                        error_msg = f".contains() solo es valido para vectores no anidados (o su ultima capa)"
                        log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)

                    gen = Generator()
                    gen.add_comment("-------------------param func call::var_ref::vector contains-------------------")

                    if len(self.params) != 1:
                        error_msg = f".contains() solo toma 1 argumento, {len(self.params)} fueron dados"
                        log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)

                    compare_to_result = self.params[0].expr.execute(environment)
                    gen.combine_with(compare_to_result.generator)

                    if compare_to_result.expression_type != result.content_type:
                        error_msg = f"El elemento a comparar en .contains() debe ser del mismo tipo que el vector." \
                                    f"({compare_to_result.expression_type.name} != {result.content_type.name})"
                        log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)

                    l_contains_element = gen.new_label()
                    l_true = gen.new_label()
                    l_false = gen.new_label()
                    gen.combine_with(result.generator)
                    gen.add_comment("---Pointer for value")

                    t_pointer = gen.new_temp()
                    gen.add_expression(t_pointer, result.value, "", "")

                    counter = gen.new_temp()
                    gen.add_get_heap(counter, t_pointer)

                    gen.add_expression(t_pointer, t_pointer, "2", "+")  # offsets to element

                    l_loop = gen.new_label()
                    l_arrived = gen.new_label()

                    gen.add_label([l_loop])
                    gen.add_if(counter, "0", "==", l_arrived)

                    if result.content_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                        from expressions.logic import logical_str_compare
                        l_str_true = gen.new_label()
                        l_str_false = gen.new_label()

                        value = gen.new_temp()
                        gen.add_get_heap(value, t_pointer)
                        logical_str_compare(gen, l_str_true, l_str_false, compare_to_result.value, value, "==")

                        gen.add_label([l_str_true])
                        gen.add_goto(l_contains_element)
                        gen.add_label([l_str_false])

                    else:
                        value = gen.new_temp()
                        gen.add_get_heap(value, t_pointer)
                        gen.add_if(value, compare_to_result.value, "==", l_contains_element)

                    gen.add_expression(t_pointer, t_pointer, "1", "+")  # offsets to ptr_next
                    gen.add_get_heap(t_pointer, t_pointer)
                    gen.add_expression(counter, counter, "1", "-")
                    gen.add_goto(l_loop)

                    gen.add_label([l_arrived])
                    gen.add_goto(l_false)

                    gen.add_label([l_contains_element])
                    gen.add_goto(l_true)

                    return ValueTuple(value="dont_use_me_boolean", expression_type=ExpressionType.BOOL, is_mutable=True,
                                      generator=gen, content_type=ExpressionType.BOOL, capacity=None,
                                      is_tmp=True, true_label=[l_true], false_label=[l_false])


            if result.expression_type == ExpressionType.ARRAY:
                if self.function_id == "to_string":
                    gen = Generator()
                    gen.combine_with(result.generator)
                    gen.add_comment("---Pointer for value")
                    ptr = gen.new_temp()
                    gen.add_expression(ptr, result.value, "", "")

                    backwards_dimensions = result.capacity[::-1]

                    string_result = gen.new_temp()
                    gen.add_expression(string_result, "H", "", "")

                    body_generator: Generator = Generator()

                    first = True

                    offset_for_none = 0  # for arrays without size, need to get it from array_stack_pos + n for n->n-dim

                    dims = []
                    if backwards_dimensions[0] is None:
                        # TODO reverse needed?
                        dims = get_dimensions_for_passed_non_fixed_array(gen, self.variable_id, environment)[::-1]

                    for dim in backwards_dimensions:
                        dim = str(dim)
                        t_max = gen.new_temp()
                        gen.add_comment("t_max = dim")
                        if dim == "None":
                            gen.add_comment("non-set size, gathering from stack")
                            dim = dims[offset_for_none]
                            offset_for_none += 1

                        gen.add_expression(t_max, dim, "", "")
                        if first:
                            body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, True)
                            first = False
                            continue
                        body_generator = traverse_loop_for_stringify(body_generator, result, ptr, t_max, False)

                    gen.add_comment("---Print:Array traverse")
                    gen.combine_with(body_generator)
                    gen.add_set_heap("H", "-1")
                    gen.add_next_heap()
                    return ValueTuple(value=string_result, expression_type=ExpressionType.STRING_CLASS, is_mutable=True,
                                      generator=gen, content_type=ExpressionType.STRING_CLASS, capacity=None,
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

            if self.function_id == "abs":
                if result.expression_type in [ExpressionType.INT, ExpressionType.FLOAT]:
                    t_abs = result.generator.new_temp()
                    l_positive = result.generator.new_label()
                    l_exit = result.generator.new_label()
                    result.generator.add_if(result.value, "0", ">=", l_positive)
                    result.generator.add_expression(t_abs, "0", result.value, "-")
                    result.generator.add_goto(l_exit)
                    result.generator.add_label([l_positive])
                    result.generator.add_expression(t_abs, result.value, "", "")
                    result.generator.add_label([l_exit])
                    result.value = t_abs
                    return result

            if self.function_id == "sqrt":
                if result.expression_type == ExpressionType.FLOAT:
                    gen: Generator = result.generator
                    x = result.value
                    tol = gen.new_temp()
                    x0 = gen.new_temp()
                    root_approx = gen.new_temp()
                    y_n = gen.new_temp()
                    dy_n = gen.new_temp()
                    tol_neg = gen.new_temp()
                    the_div = gen.new_temp()

                    l_while_loop = gen.new_label()
                    l_continue = gen.new_label()
                    l_stop = gen.new_label()

                    gen.add_expression(tol, "1.0", "1000000000000", "/")
                    gen.add_expression(x0, x, "2.0", "/")

                    gen.add_expression(root_approx, x0, "", "")
                    gen.add_expression(y_n, x0, x0, "*")
                    gen.add_expression(y_n, y_n, x, "-")

                    gen.add_expression(dy_n, "2", x0, "*")

                    gen.add_label([l_while_loop])
                    gen.add_expression(tol_neg, "0.0", tol, "-")
                    gen.add_if(tol_neg, y_n, ">=", l_continue)
                    gen.add_if(y_n, tol, ">=", l_continue)
                    gen.add_goto(l_stop)

                    gen.add_label([l_continue])
                    gen.add_expression(the_div, y_n, dy_n, "/")
                    gen.add_expression(root_approx, root_approx, the_div, "-")

                    gen.add_expression(y_n, root_approx, root_approx, "*")
                    gen.add_expression(y_n, y_n, x, "-")
                    gen.add_expression(dy_n, "2.0", x0, "*")
                    gen.add_goto(l_while_loop)

                    gen.add_label([l_stop])
                    gen.add_expression(root_approx, root_approx, "10000000", "*")
                    gen.add_casting(root_approx, root_approx, "int")
                    gen.add_expression(root_approx, root_approx, "10000000", "/")
                    result.value = root_approx
                    return result

            if self.function_id == "len":
                if result.expression_type not in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    error_msg = f".len() primitivo solo es valido para cadenas de texto"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)
                return self.value_len(self.variable_id, environment)

        elif isinstance(self.variable_id, Literal):
            if self.function_id == "to_string":
                r = self.variable_id.execute(environment)

                if r.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    r.expression_type = ExpressionType.STRING_CLASS
                    return r

                new_lit = Literal(str(r.value), ExpressionType.STRING_CLASS, self.line, self.column)
                return new_lit.execute(environment)

            if self.function_id == "len":
                if self.variable_id.expression_type not in\
                        [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    error_msg = f".len() primitivo solo es valido para cadenas de texto"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)
                return self.value_len(self.variable_id, environment)

            if self.function_id == "sqrt":
                result = self.variable_id.execute(environment)
                if result.expression_type == ExpressionType.FLOAT:
                    gen: Generator = result.generator
                    x = result.value
                    tol = gen.new_temp()
                    x0 = gen.new_temp()
                    root_approx = gen.new_temp()
                    y_n = gen.new_temp()
                    dy_n = gen.new_temp()
                    tol_neg = gen.new_temp()
                    the_div = gen.new_temp()

                    l_while_loop = gen.new_label()
                    l_continue = gen.new_label()
                    l_stop = gen.new_label()

                    gen.add_expression(tol, "1.0", "1000000000000", "/")
                    gen.add_expression(x0, x, "2.0", "/")

                    gen.add_expression(root_approx, x0, "", "")
                    gen.add_expression(y_n, x0, x0, "*")
                    gen.add_expression(y_n, y_n, x, "-")

                    gen.add_expression(dy_n, "2", x0, "*")

                    gen.add_label([l_while_loop])
                    gen.add_expression(tol_neg, "0.0", tol, "-")
                    gen.add_if(tol_neg, y_n, ">=", l_continue)
                    gen.add_if(y_n, tol, ">=", l_continue)
                    gen.add_goto(l_stop)

                    gen.add_label([l_continue])
                    gen.add_expression(the_div, y_n, dy_n, "/")
                    gen.add_expression(root_approx, root_approx, the_div, "-")

                    gen.add_expression(y_n, root_approx, root_approx, "*")
                    gen.add_expression(y_n, y_n, x, "-")
                    gen.add_expression(dy_n, "2.0", x0, "*")
                    gen.add_goto(l_while_loop)

                    gen.add_label([l_stop])
                    gen.add_expression(root_approx, root_approx, "10000000", "*")
                    gen.add_casting(root_approx, root_approx, "int")
                    gen.add_expression(root_approx, root_approx, "10000000", "/")
                    result.value = root_approx
                    return result

        # elif isinstance(self.variable_id, TypeCasting):
        #     r = self.variable_id.execute(environment)
        #     the_symbol = Symbol("type_casting_forced_symbol", r._type, r.value, True, False)

        elif isinstance(self.variable_id, ParameterFunctionCallE):
            # FIXME check resulting function type
            pass
            print("PARAMETER FUNC CALL::ParameterFunctionCallE INSTANCE NOT IMPLEMENTED YET")


        # TODO Check if is struct
        #  elif isinstance(the_symbol, struct_symbol):

        # TODO Check if present in struct
        print("missing stuff")
        error_msg = f"Acceso a parametro de variable invalido.."
        log_semantic_error(error_msg, self.line, self.column)
        raise SemanticError(error_msg, self.line, self.column)

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




