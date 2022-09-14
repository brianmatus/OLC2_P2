from typing import Union
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.env import Environment
from element_types.element_type import ElementType
from abstract.expression import Expression


class ContinueI(Instruction):
    def __init__(self, expr: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)
        self.expr = expr

    def execute(self, env: Environment) -> ExecReturn:

        if self.expr is None:
            return ExecReturn(ElementType.VOID, None, False, False, True)

        result = self.expr.execute(env)
        return ExecReturn(result._type, result.value, False, False, True)

