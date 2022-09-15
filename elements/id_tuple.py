from element_types.c_expression_type import ExpressionType


class IDTuple:
    def __init__(self, _id: str, _type: ExpressionType, is_mutable: bool, is_array: bool, dimensions: dict,
                 content_type: ExpressionType):
        self._id = _id
        self._type = _type
        self.is_array: bool = is_array
        self.is_mutable: bool = is_mutable
        self.dimensions: dict = dimensions
        self.content_type = content_type

        # print("ya parsed")
        # print(self.dimensions)

