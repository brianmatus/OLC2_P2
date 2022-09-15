from typing import Union, List
from element_types.c_expression_type import ExpressionType


class ValueTuple:

    def __init__(self, value, expression_type: ExpressionType, is_mutable: bool, content_type: Union[ExpressionType, None],
                 capacity: Union[List[int], None], is_tmp: bool):
        self.expression_type: ExpressionType = expression_type
        self.value: ExpressionType = value
        self.is_mutable: bool = is_mutable
        self.content_type: ExpressionType = content_type
        self.capacity: List[int] = capacity
        self.is_tmp: bool = is_tmp
        self.true_label = ""
        self.false_label = ""

    def __str__(self):
        return f'ValTup(v:{self.value}, t:{self.expression_type})'

    def __repr__(self):
        return f'ValTup(v:{self.value}, t:{self.expression_type})'

