from element_types.c_expression_type import ExpressionType
from generator import Generator


class ExecReturn:
    def __init__(self, generator: Generator, propagate_method_return: bool, propagate_break: bool, propagate_continue: bool):
        self.generator: Generator = generator
        self.propagate_method_return: bool = propagate_method_return
        self.propagate_break: bool = propagate_break
        self.propagate_continue: bool = propagate_continue
