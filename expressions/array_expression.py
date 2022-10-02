from typing import Union

# from errors.semantic_error import SemanticError
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
# from element_types.arithmetic_type import ArithmeticType


# import global_config


class ArrayExpression(Expression):

    # values:ArrayExpression, Expression[]
    def __init__(self, value, is_expansion: bool, expansion_size: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)
        self.value = value
        self.is_expansion = is_expansion
        self.expansion_size = expansion_size

    def execute(self, environment: Environment) -> ValueTuple:

        # Definition by expansion
        if self.is_expansion:
            # TODO implement
            for i in range(20):
                print(f"array_expression.py::({i}/20 warnings) as expansion, to be implemented")

        from generator import Generator

        # Definition by list
        return ValueTuple(value=self.value, expression_type=ExpressionType.ARRAY, is_mutable=True,
                          content_type=ExpressionType.VOID, capacity=None, false_label=[], true_label=[], is_tmp=False,
                          generator=Generator())
