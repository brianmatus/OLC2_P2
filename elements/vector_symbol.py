from typing import List
from element_types.element_type import ElementType


class VectorSymbol:
    def __init__(self, _id: str, _type: ElementType, content_type: ElementType, deepness: int, value,
                 is_mutable: bool, capacity: List[int]):
        self.value = value
        self._id: str = _id
        self._type: ElementType = _type
        self.is_mutable: bool = is_mutable
        self.deepness: int = deepness
        # FIXME List[int] instead of int: for passing as reference to func (or other envs in general)
        self.capacity: List[int] = capacity
        self.content_type: ElementType = content_type
