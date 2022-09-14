from typing import Union

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.env import Environment
from element_types.element_type import ElementType
from abstract.expression import Expression


class ReturnI(Instruction):
    def __init__(self, expr: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)
        self.expr = expr


    def execute(self, env: Environment) -> ExecReturn:

        if self.expr is None:
            return ExecReturn(ElementType.VOID, None, True, False, False)

        result = self.expr.execute(env)

        # WTF? python wasn't adding ._type to it, idk man I'm tired.
        r = ExecReturn(_type=result._type, value=result.value, propagate_method_return=True,
                       propagate_continue=False, propagate_break=False)
        r._type = result._type
        #print(r._type)
        return r
