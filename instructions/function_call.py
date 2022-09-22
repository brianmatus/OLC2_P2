from typing import List, Union

import global_config
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.func_call_arg import FuncCallArg
from element_types.c_expression_type import ExpressionType

from abstract.expression import Expression
from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from errors.semantic_error import SemanticError

from global_config import function_list, log_semantic_error, main_environment
from instructions.function_declaration import FunctionDeclaration
from generator import Generator


class FunctionCallI(Instruction):

    def __init__(self, function_id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)
        self.function_id: str = function_id
        self.params: List[FuncCallArg] = params

        if function_id not in global_config.function_call_list.keys():
            global_config.function_call_list[function_id] = []

        self.turn = len(global_config.function_call_list[function_id])

        self.comeback_label = Generator().new_label()
        global_config.function_call_list[function_id].append(self.comeback_label)
        pass

    def execute(self, env: Environment) -> ExecReturn:

        func: FunctionDeclaration = function_list.get(self.function_id)

        if func is None:
            error_msg = f"No existe una función con el nombre {self.function_id}"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # print("------------------------------------FUNC CALL------------------------------------")
        #
        # print(len(self.params))
        # print(len(func.params))

        if len(self.params) != len(func.params):
            error_msg = f"La función {self.function_id} fue llamada con un numero incorrecto de argumentos"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        intermediate_env = Environment(main_environment)
        intermediate_env.parent_environment = main_environment

        final_generator = Generator()
        final_generator.add_comment(f"-------------------------------Function Call of {self.function_id}"
                                    f"-------------------------------")

        for i in range(len(self.params)):

            param = func.params[i]
            given = self.params[i].expr.execute(env)

            final_generator.combine_with(given.generator)

            if param.expression_type != given.expression_type:
                error_msg = f"La función {self.function_id} fue llamada con un tipo incorrecto de argumento. " \
                            f"Arg #{i + 1}" \
                            f"({param.expression_type.name} <-> {given.expression_type.name})"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            c = param.is_array and not self.params[i].as_reference
            d = not param.is_array and self.params[i].as_reference
            if c or d:
                error_msg = f"La función {self.function_id} fue llamada con un array sin ser usado como referencia." \
                            f" Usa el operador & para pasar un array (ej.: &array)"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            # Non mutable array was passed as mutable using &mut
            if given.expression_type == ExpressionType.ARRAY:
                if param.is_mutable and not given.is_mutable:
                    print(f'u r not actually mutable, liar!')
                    error_msg = f"La función {self.function_id} fue llamada con un array no mutable, como mutable"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

            final_generator.add_comment(f"-----Arg #{i}-----")
            arg_position = final_generator.new_temp()
            final_generator.add_expression(arg_position, "P", str(i), "+")
            final_generator.add_set_stack(arg_position, given.value)

        final_generator.add_comment(f"-----Where should the func return once completed? To {self.comeback_label}-----")
        final_generator.add_expression("t1", str(self.turn), "", "")
        final_generator.add_goto(func.start_label)

        final_generator.add_label([self.comeback_label])
        return ExecReturn(final_generator, False, False, False)





