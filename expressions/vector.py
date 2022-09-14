from typing import Union, List

from errors.semantic_error import SemanticError
from abstract.expression import Expression
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from returns.ast_return import ASTReturn
from element_types.arithmetic_type import ArithmeticType
from expressions.literal import Literal


import global_config


class VectorExpression(Expression):
    # expr: ArrayExpression (to clone lol) | None
    def __init__(self, expr, capacity: Union[Expression, None], line: int, column: int):
        super().__init__(line, column)

        if expr is None:  # Vec::new()
            self.values = []
            self.is_expansion = False
            self.expansion_size = None
            if capacity is not None:
                self.capacity: expr = capacity
            else:
                self.capacity: Expression = Literal(0, ElementType.INT, self.line, self.column)

        else:
            self.values = expr.values
            self.is_expansion = expr.is_expansion
            self.expansion_size = expr.expansion_size
            if capacity is not None:
                self.capacity: expr = capacity
            else:
                self.capacity: Expression = Literal(-1, ElementType.INT, self.line, self.column)

    def execute(self, environment: Environment) -> ValueTuple:

        # Definition by expansion
        if self.is_expansion:
            expr: ValueTuple = self.values.execute(environment)
            repetitions: ValueTuple = self.expansion_size.execute(environment)

            if repetitions._type is not ElementType.INT:
                error_msg = f"La expansion de vector debe tener como cantidad un numero entero." \
                            f"(Se obtuvo {repetitions._type})"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            if repetitions.value < 1:
                error_msg = f"La expansion de vector debe ser como minimo 1 (Se obtuvo {repetitions.value})"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            # FIX ME, should check if last 2 Nones are correct
            return ValueTuple(value=[expr]*int(repetitions.value), _type=ElementType.VECTOR, is_mutable=False,
                              content_type=None, capacity=None)


        # Definition by list (or by new() which is handled in this constructor)
        content_type = None
        expr_result = None
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

        cont_t = None
        if expr_result is None:
            cont_t = None
        else:
            if expr_result._type is not ElementType.VECTOR:
                cont_t = expr_result._type
            else:
                cont_t = expr_result.content_type

        return ValueTuple(value=result, _type=ElementType.VECTOR, is_mutable=False, content_type=cont_t,
                          capacity=[self.capacity])  # TODO fixme

