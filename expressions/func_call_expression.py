from typing import List

from elements.c_env import Environment
from element_types.func_call_arg import FuncCallArg
from elements.value_tuple import ValueTuple

from abstract.expression import Expression
from returns.exec_return import ExecReturn

from global_config import function_list
from instructions.function_declaration import FunctionDeclaration

from instructions.function_call import FunctionCallI


class FunctionCallE(Expression):

    def __init__(self, function_id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)
        self.delegate = FunctionCallI(function_id, params, line, column)

    def execute(self, environment: Environment) -> ValueTuple:

        result: ExecReturn = self.delegate.execute(environment)
        fn: FunctionDeclaration = function_list.get(self.delegate.function_id)
        return ValueTuple("t0", fn.return_type, True, result.generator, fn.return_content_type,
                          capacity=fn.return_capacity, is_tmp=True,
                          true_label=fn.return_true_label, false_label=fn.return_false_label)
