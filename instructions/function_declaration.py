from typing import List, Union

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
from elements.id_tuple import IDTuple

from errors.semantic_error import SemanticError
from global_config import log_semantic_error, function_list


class FunctionDeclaration(Instruction):
    def __init__(self, _id: str, params: List[IDTuple], return_type:  ElementType, instructions: List[Instruction],
                 line: int, column: int):
        super().__init__(line, column)
        self._id: str = _id
        self.params: List[IDTuple] = params
        self.return_type: ElementType = return_type
        self.instructions: List[Instruction] = instructions
        self.environment: Union[Environment, None] = None

        if function_list.get(self._id) is not None:
            error_msg = f"La función {self._id} ya esta definida. No esta permitido el sobrecargo de funciones."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        # Not necessary, as only functions are defined globally
        # if global_config.main_environment.recursive_get(self._id) is not None:
        #     error_msg = f"Ya existe una variable con el nombre {self._id}"
        #     log_semantic_error(error_msg, self.line, self.column)
        #     raise SemanticError(error_msg, self.line, self.column)

        global_config.function_list[self._id] = self
        print(f'Function {self._id} saved to main environment')

        self.environment = Environment(global_config.main_environment)  # Just in case, this should happen in every call

        # Constructor wasn't working correctly, just in case
        self.environment.parent_environment = global_config.main_environment

    def execute(self, env: Environment) -> ExecReturn:
        # nothing? idk
        return ExecReturn(ElementType.BOOL, True, False, False, False)
