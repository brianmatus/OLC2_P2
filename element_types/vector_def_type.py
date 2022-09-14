from abstract.expression import Expression

class VectorDefType:

    # Content should only be var_type(ElementType) or ArrayDefType
    def __init__(self, is_nested_vector: bool, content_type):
        self.is_nested_vector = is_nested_vector
        self.content_type = content_type
