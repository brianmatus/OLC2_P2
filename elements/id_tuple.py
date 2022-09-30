from element_types.c_expression_type import ExpressionType


class IDTuple:
    def __init__(self, variable_id: str, expression_type: ExpressionType, is_mutable: bool, is_array: bool,
                 dimensions: dict, content_type: ExpressionType):
        self.variable_id = variable_id
        self.expression_type = expression_type
        self.is_array: bool = is_array
        self.is_mutable: bool = is_mutable
        self.dimensions: dict = dimensions
        self.content_type = content_type

        # print("ya parsed")
        # print(self.dimensions)
