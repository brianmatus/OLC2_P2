from element_types.element_type import ElementType


class ArraySymbol:
    def __init__(self, _id: str, _type: ElementType, dimensions: dict, value, is_init: bool, is_mutable: bool):
        self.value = value
        self._id = _id
        self._type = _type
        self.is_init = is_init
        self.is_mutable = is_mutable
        self.dimensions: {} = dimensions
