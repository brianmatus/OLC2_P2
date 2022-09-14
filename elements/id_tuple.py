from element_types.element_type import ElementType


class IDTuple:
    def __init__(self, _id: str, _type: ElementType, is_mutable: bool, is_array: bool, dimensions: dict,
                 content_type: ElementType):
        self._id = _id
        self._type = _type
        self.is_array: bool = is_array
        self.is_mutable: bool = is_mutable
        self.dimensions: dict = dimensions
        self.content_type = content_type

        # print("ya parsed")
        # print(self.dimensions)

