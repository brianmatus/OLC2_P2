from element_types.element_type import ElementType


class ExecReturn:
    def __init__(self, _type: ElementType, value,
                 propagate_method_return: bool, propagate_break: bool, propagate_continue: bool):
        self._type: ElementType = _type
        self.value = value
        self.propagate_method_return = propagate_method_return
        self.propagate_break = propagate_break
        self.propagate_continue = propagate_continue
