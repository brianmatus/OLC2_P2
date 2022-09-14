from typing import Union
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.env import Environment
from element_types.element_type import ElementType
from abstract.expression import Expression


class BreakI(Instruction):
    def __init__(self, expr: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)
        self.expr = expr

    def execute(self, env: Environment) -> ExecReturn:

        if self.expr is None:
            # print("breaking with none")
            return ExecReturn(ElementType.VOID, None, False, True, False)

        result = self.expr.execute(env)
        # print(f'breaking with v:{result.value} t:{result._type}')
        return ExecReturn(result._type, result.value, False, True, False)
