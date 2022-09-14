from typing import Union, List

from errors.semantic_error import SemanticError
from abstract.expression import Expression
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from returns.ast_return import ASTReturn
from element_types.arithmetic_type import ArithmeticType


import global_config


class ArrayExpression(Expression):

    def __init__(self, values, is_expansion: bool, expansion_size: Union[Expression, None], line: int, column: int):  # values:ArrayExpresion, Expression[]
        super().__init__(line, column)
        self.values = values
        self.is_expansion = is_expansion
        self.expansion_size = expansion_size

    def execute(self, environment: Environment) -> ValueTuple:

        # Definition by expansion
        if self.is_expansion:
            expr: ValueTuple = self.values.execute(environment)
            repetitions: ValueTuple = self.expansion_size.execute(environment)

            if repetitions._type is not ElementType.INT:
                error_msg = f"La expansion de arrays debe tener como cantidad un numero entero." \
                            f"(Se obtuvo {repetitions._type})"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            return ValueTuple(value=[expr]*int(repetitions.value), _type=ElementType.ARRAY_EXPRESSION, is_mutable=False)

        # Definition by list
        result: List[ValueTuple] = []
        for value in self.values:

            # if isinstance(value, Expression):  # Most nested iteration without expansion
            #     result.append(value.execute(environment))
            #     continue
            #
            # if isinstance(value, ArrayExpression):
            #     result.append(value.execute(environment))
            #     continue

            expr_result = value.execute(environment)
            result.append(expr_result)

        return ValueTuple(value=result, _type=ElementType.ARRAY_EXPRESSION, is_mutable=False,
                          content_type=None, capacity=None)

