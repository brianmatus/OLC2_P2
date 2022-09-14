from abstract.expression import Expression


class ArrayDefType:

    # Content should only be var_type(ElementType) or ArrayDefType
    def __init__(self, is_nested_array: bool, content_type, size_expr: Expression):
        self.is_nested_array = is_nested_array
        self.content_type = content_type
        self.size_expr = size_expr
