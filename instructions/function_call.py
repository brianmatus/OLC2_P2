from typing import List, Tuple

import global_config
from elements.c_env import Environment
from element_types.func_call_arg import FuncCallArg
from element_types.c_expression_type import ExpressionType

from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from errors.semantic_error import SemanticError

from expressions.array_expression import ArrayExpression

import global_config
from instructions.function_declaration import FunctionDeclaration
from generator import Generator


class FunctionCallI(Instruction):

    def __init__(self, function_id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)
        self.function_id: str = function_id
        self.params: List[FuncCallArg] = params

        if function_id not in global_config.function_call_list.keys():
            global_config.function_call_list[function_id] = []

        # self.turn = len(global_config.function_call_list[function_id])

        # self.comeback_label = Generator().new_label()
        # global_config.function_call_list[function_id].append(self.comeback_label)
        pass

    def execute(self, env: Environment) -> ExecReturn:

        func: FunctionDeclaration = global_config.function_list.get(self.function_id)

        if func is None:
            error_msg = f"No existe una función con el nombre {self.function_id}"
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # print("------------------------------------FUNC CALL------------------------------------")
        #
        # print(len(self.params))
        # print(len(func.params))

        if len(self.params) != len(func.params):
            error_msg = f"La función {self.function_id} fue llamada con un numero incorrecto de argumentos"
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # intermediate_env = Environment(main_environment)
        # intermediate_env.parent_environment = main_environment

        final_generator = Generator(env)
        final_generator.add_comment(f"-------------------------------Function Call of {self.function_id}"
                                    f"-------------------------------")

        arg_position = ""



        if len(self.params) != 0:
            final_generator.add_comment("-----f_call:Temporal new P for setting up func args in new env-----")
            delta_p = final_generator.new_temp()
            final_generator.add_expression(delta_p, "P", env.size, "+")
            arg_position = final_generator.new_temp()
        else:
            final_generator.add_comment("Function has no args, no temporal new P needed")

        given_params = []
        for i in range(len(self.params)):
            given_params.append(self.params[i].expr.execute(env))

        # Get them, but not add them yet!
        # Only necessary for args future positions
        # But given params are still found in current P
        # So add them after all args are passed
        fn_used_tmps = env.get_tmps_from_function()
        offset = len(fn_used_tmps)  # For arrays with no size set

        for i in range(len(self.params)):
            param = func.params[i]
            given = given_params[i]

            final_generator.combine_with(given.generator)

            if param.expression_type != given.expression_type:
                error_msg = f"La función {self.function_id} fue llamada con un tipo incorrecto de argumento. " \
                            f"Arg #{i + 1}" \
                            f"({param.expression_type.name} <-> {given.expression_type.name})"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            # c = param.is_array and not self.params[i].as_reference
            # d = not param.is_array and self.params[i].as_reference
            # if c or d:
            #     error_msg = f"La función {self.function_id} fue llamada con un array sin ser usado como referencia." \
            #                 f" Usa el operador & para pasar un array (ej.: &array). Arg #{i + 1}"
            #     log_semantic_error(error_msg, self.line, self.column)
            #     raise SemanticError(error_msg, self.line, self.column)

            if given.expression_type == ExpressionType.VECTOR:
                if param.content_type != given.content_type:
                    error_msg = f"La función {self.function_id} fue llamada con un tipo incorrecto de argumento. " \
                                f"Arg #{i + 1}" \
                                f"({param.content_type.name} <-> {given.content_type.name})"
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

            # Non mutable array was passed as mutable using &mut
            if given.expression_type == ExpressionType.ARRAY:
                if param.is_mutable and not given.is_mutable:
                    print(f'u r not actually mutable, liar!')
                    error_msg = f"La función {self.function_id} fue llamada con un array no mutable, como mutable. " \
                                f"Arg #{i + 1}"
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                if isinstance(self.params[i].expr, ArrayExpression):
                    if not global_config.match_array_type(param.content_type, given.value):
                        error_msg = f"La función {self.function_id} fue llamada con un tipo incorrecto de argumento. " \
                                    f"Arg #{i + 1} Array "\
                                    f"({param.content_type.name} <-> {given.content_type.name})"
                        global_config.log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)

                else:
                    if param.content_type != given.content_type:
                        error_msg = f"La función {self.function_id} fue llamada con un tipo incorrecto de argumento. " \
                                    f"Arg #{i + 1}" \
                                    f"({param.content_type.name} <-> {given.content_type.name})"
                        global_config.log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)

            final_generator.add_comment(f"-----Arg #{i}-----")
            # arg_position = final_generator.new_temp()  # replaced by one globally, for easier optimization
            final_generator.add_expression(arg_position, delta_p, str(i+offset), "+")

            if isinstance(self.params[i].expr, ArrayExpression):
                gen, ptr = func_call_custom_array_expr(self.params[i].expr.value, env)
                final_generator.combine_with(gen)
                final_generator.add_set_stack(arg_position, ptr)
            else:
                final_generator.add_set_stack(arg_position, given.value)

            if given.expression_type == ExpressionType.ARRAY:
                if param.dimensions[1] is None:
                    if isinstance(self.params[i].expr, ArrayExpression):
                        the_dims = list(global_config.extract_dimensions_to_dict(given.value).values())
                        for key in param.dimensions.keys():
                            offset += 1
                            final_generator.add_expression(arg_position, delta_p, str(i + offset), "+")
                            final_generator.add_set_stack(arg_position, str(the_dims[key - 1]))
                    else:
                        # Needs to offset
                        for key in param.dimensions.keys():
                            offset += 1
                            final_generator.add_expression(arg_position, delta_p, str(i + offset), "+")
                            final_generator.add_set_stack(arg_position, str(given.capacity[key-1]))

        final_generator.add_comment("-----f_call:Update P for a new environment-----")
        final_generator.add_expression("P", "P", env.size, "+")

        final_generator.add_comment("-----f_call:P offset of tmps used in this function-----")
        for tmp in fn_used_tmps:
            final_generator.add_set_stack("P", tmp)
            final_generator.add_expression("P", "P", "1", "+")

        # final_generator.add_comment(f"-----f_call:Where should the func return once completed? To {self.comeback_label}-----")
        # final_generator.add_expression("t1", str(self.turn), "", "")

        # final_generator.add_goto(func.start_label)
        final_generator.add_func_call(func.function_id)

        l_not_error = final_generator.new_label()
        final_generator.add_if("t1", "0", "==", l_not_error)
        if self.function_id == "main":
            # final_generator.code.append("return t1;")
            final_generator.add_print_message("Program finished with exit code:")
            final_generator.add_printf("i", "t1")
            final_generator.add_printf("c", str(ord("\n")))
            final_generator.code.append("return 0;")
        else:
            final_generator.add_error_return("")
        final_generator.add_label([l_not_error])

        final_generator.add_comment("-----f_call:Revert P for a previous environment-----")
        final_generator.add_expression("P", "P", env.size, "-")
        # final_generator.add_expression("P", "P", str(len(fn_used_tmps)), "-")  # TODO fixme
        final_generator.add_comment("-----f_call:Revert func_has_returned-----")
        final_generator.add_expression("t2", "0", "", "")
        return ExecReturn(final_generator, False, False, False)


def func_call_custom_array_expr(the_array_expr, env: Environment) -> Tuple[Generator, str]:
    flat_array = global_config.flatten_array(the_array_expr)
    generator = Generator(env)
    generator.add_comment(f"-------------------------------Array Expr passed as arg-------------------------------")

    values = []
    for expr in flat_array:
        r = expr.execute(env)
        generator.combine_with(r.generator)
        values.append(str(r.value))

    t = generator.new_temp()
    generator.add_expression(t, "H", "", "")
    generator.add_set_stack(t, "H")

    for val in values:
        generator.add_set_heap("H", val)
        generator.add_next_heap()

    return generator, t

