from typing import Union, List
from element_types.element_type import ElementType


class ValueTuple:

    def __init__(self, value, _type: ElementType, is_mutable: bool, content_type: Union[ElementType, None],
                 capacity: Union[List[int], None]):
        self._type: ElementType = _type
        self.value: ElementType = value
        self.is_mutable: bool = is_mutable
        self.content_type: ElementType = content_type
        self.capacity: List[int] = capacity

    def __str__(self):
        return f'ValTup(v:{self.value}, t:{self._type})'

    def __repr__(self):
        return f'ValTup(v:{self.value}, t:{self._type})'

