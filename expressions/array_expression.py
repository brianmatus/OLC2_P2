from typing import Union, List

from errors.semantic_error import SemanticError
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from returns.ast_return import ASTReturn
from element_types.arithmetic_type import ArithmeticType


import global_config


class ArrayExpression(Expression):

    def __init__(self, value, is_expansion: bool, expansion_size: Union[Expression, None], line: int, column: int):  # values:ArrayExpresion, Expression[]
        super().__init__(line, column)
        self.value = value
        self.is_expansion = is_expansion
        self.expansion_size = expansion_size

    def execute(self, environment: Environment) -> ValueTuple:

        # Definition by expansion
        if self.is_expansion:
            # expr: ValueTuple = self.values.execute(environment)
            # repetitions: ValueTuple = self.expansion_size.execute(environment)
            #
            # if repetitions._type is not ExpressionType.INT:
            #     error_msg = f"La expansion de arrays debe tener como cantidad un numero entero." \
            #                 f"(Se obtuvo {repetitions._type})"
            #     global_config.log_semantic_error(error_msg, self.line, self.column)
            #     raise SemanticError(error_msg, self.line, self.column)
            #
            # return ValueTuple(value=[expr]*int(repetitions.value), _type=ExpressionType.ARRAY_EXPRESSION, is_mutable=False)
            pass
            # TODO implement
            for i in range(20):
                print(f"array_expression.py::({i}/20 warnings) as expansion, to be implemented")

        from generator import Generator

        # Definition by list
        return ValueTuple(value=self.value, expression_type=ExpressionType.ARRAY, is_mutable=False,
                          content_type=ExpressionType.VOID, capacity=None, false_label=[], true_label=[], is_tmp=False,
                          generator=Generator())

