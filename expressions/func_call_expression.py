from typing import List, Tuple

import global_config
from elements.c_env import Environment
from element_types.func_call_arg import FuncCallArg
from element_types.c_expression_type import ExpressionType
from elements.value_tuple import ValueTuple

from abstract.expression import Expression
from returns.exec_return import ExecReturn
from errors.semantic_error import SemanticError

from expressions.array_expression import ArrayExpression

from global_config import function_list, log_semantic_error
from instructions.function_declaration import FunctionDeclaration

from instructions.function_call import FunctionCallI

from generator import Generator


class FunctionCallE(Expression):

    def __init__(self, function_id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)
        self.function_id: str = function_id
        self.params: List[FuncCallArg] = params

        self.delegate = FunctionCallI(function_id, params, line, column)

        # if function_id not in global_config.function_call_list.keys():
        #     global_config.function_call_list[function_id] = []

        # self.turn = len(global_config.function_call_list[function_id])

        # self.comeback_label = Generator().new_label()
        # global_config.function_call_list[function_id].append(self.comeback_label)
        pass

    def execute(self, environment: Environment) -> ValueTuple:

        result: ExecReturn = self.delegate.execute(environment)
        fn: FunctionDeclaration = function_list.get(self.function_id)
        return ValueTuple("t0", fn.return_type, True, result.generator, fn.return_content_type, capacity=fn.return_capacity,
                          is_tmp=True, true_label=fn.return_true_label, false_label=fn.return_false_label)
