from typing import List, Union

import global_config
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.func_call_arg import FuncCallArg
from element_types.element_type import ElementType

from abstract.expression import Expression
from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from errors.semantic_error import SemanticError

from global_config import function_list, log_semantic_error, main_environment

from instructions.function_declaration import FunctionDeclaration

class FunctionCallI(Instruction):

    def __init__(self, _id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)
        self._id: str = _id
        self.params: List[FuncCallArg] = params


    def execute(self, env: Environment) -> ExecReturn:

        func: FunctionDeclaration = function_list.get(self._id)

        if func is None:
            error_msg = f"No existe una función con el nombre {self._id}"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # print("------------------------------------FUNC CALL------------------------------------")
        #
        # print(len(self.params))
        # print(len(func.params))

        if len(self.params) != len(func.params):
            error_msg = f"La función {self._id} fue llamada con un numero incorrecto de argumentos"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)


        intermediate_env = Environment(main_environment)
        intermediate_env.parent_environment = main_environment

        for i in range(len(self.params)):

            param = func.params[i]
            given = self.params[i].expr.execute(env)

            # print("aqui? piti")
            # print(param._type)
            # print(given._type)

            if param._type == ElementType.VECTOR:

                if not global_config.match_pure_vector_deepness(param.dimensions, given.value):
                    error_msg = f"La función {self._id} fue llamada con un tamaño incorrecto de vector. Arg #{i + 1}"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                if given.content_type != param.content_type:
                    error_msg = f"La función {self._id} fue llamada con un tipo incorrecto de argumento (vector)." \
                                f" Arg #{i + 1}"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                c = param.is_array and not self.params[i].as_reference
                d = not param.is_array and self.params[i].as_reference

                if c or d:
                    error_msg = f"La función {self._id} fue llamada con un array sin ser usado como referencia." \
                                f" Usa el operador & para pasar un array (ej.: &array)"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                # Non mutable array was passed as mutable using &mut
                if param.is_mutable and not given.is_mutable:
                    print(f'u r not actually mutable, liar!')
                    error_msg = f"La función {self._id} fue llamada con un array no mutable, como mutable"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                intermediate_env.save_variable_vector(param._id, param._type, param.content_type, param.dimensions,
                                                      given.value, param.is_mutable, given.capacity,
                                                      self.line, self.column)
                continue

            if param.is_array:

                to_m = param.dimensions.copy()
                to_m.pop("embedded_type")
                match_expr = False
                # print(param.dimensions[1])
                if param.dimensions[1] is None:
                    match_expr = global_config.match_deepness(len(list(to_m.values())), given.value)
                    # print("not given")
                    # print(match_expr)

                else:
                    match_expr = global_config.match_dimensions(list(to_m.values()), given.value)

                if not match_expr:
                    error_msg = f"La función {self._id} fue llamada con un tamaño incorrecto de array. Arg #{i + 1}"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)


            if param._type != given._type:
                error_msg = f"La función {self._id} fue llamada con un tipo incorrecto de argumento. Arg #{i+1}" \
                            f"({param._type.name} <-> {given._type})"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            a = param.is_array and not isinstance(given.value, list)
            b = not param.is_array and isinstance(given.value, list)
            if a or b:
                error_msg = f"La función {self._id} fue llamada con un tipo incorrecto de argumento (array). Arg #{i+1}"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            c = param.is_array and not self.params[i].as_reference
            d = not param.is_array and self.params[i].as_reference

            # print(f"as reference check:{c} | {d}")
            if c or d:
                error_msg = f"La función {self._id} fue llamada con un array sin ser usado como referencia." \
                            f" Usa el operador & para pasar un array (ej.: &array)"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)


            # Non mutable array was passed as mutable using &mut
            if isinstance(given.value, list):
                if param.is_mutable and not given.is_mutable:
                    print(f'u r not actually mutable, liar!')
                    error_msg = f"La función {self._id} fue llamada con un array no mutable, como mutable"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)


                calculated = global_config.extract_dimensions_to_dict(global_config.value_tuple_array_to_array(given.value))

                intermediate_env.save_variable_array(param._id, param._type,
                                                     calculated, given.value,
                                                     param.is_mutable, True, self.line, self.column)
                continue

            intermediate_env.save_variable(param._id, param._type, given.value, param.is_mutable, True, False,
                                           self.line, self.column)

        instruction: Instruction
        for instruction in func.instructions:
            result = instruction.execute(intermediate_env)

            if result.propagate_break or result.propagate_continue:
                print("Missplaced break/continue")
                error_msg = f"Se ha hecho un break/continue sin ámbito al cual aplicarlo"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            if result.propagate_method_return:
                if result._type != func.return_type:
                    print("Return mismatch")
                    error_msg = f'La función <{self._id}> ha retornado un valor de tipo erróneo: {result._type.name}'
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                return ExecReturn(result._type, result.value, False, False, False)

        return ExecReturn(ElementType.VOID, None, False, False, False)
