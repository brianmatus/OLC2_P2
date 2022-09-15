from typing import List
from element_types.c_expression_type import ExpressionType


class VectorSymbol:
    def __init__(self, _id: str, _type: ExpressionType, content_type: ExpressionType, deepness: int, value,
                 is_mutable: bool, capacity: List[int]):
        self.value = value
        self._id: str = _id
        self._type: ExpressionType = _type
        self.is_mutable: bool = is_mutable
        self.deepness: int = deepness
        # FIXME List[int] instead of int: for passing as reference to func (or other envs in general)
        self.capacity: List[int] = capacity
        self.content_type: ExpressionType = content_type
