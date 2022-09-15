from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from generator import Generator


class Literal(Expression):

    def __init__(self, value, expression_type: ExpressionType, line: int, column: int):
        super().__init__(line, column)
        self.value = value
        self.expression_type: ExpressionType = expression_type

    def execute(self, environment: Environment) -> ValueTuple:

        if self.expression_type in [ExpressionType.INT, ExpressionType.FLOAT, ExpressionType.CHAR]:

            return ValueTuple(value=self.value, expression_type=self.expression_type, is_mutable=False,
                              content_type=self.expression_type, capacity=None, is_tmp=False)

        if self.expression_type == ExpressionType.STRING_PRIMITIVE:
            generator = Generator()
            t = generator.new_temp()
            generator.add_expression(t, "H", "", "")

            for char in self.value:
                generator.add_set_heap("H", str(ord(char)))
                generator.add_next_heap()

            generator.add_set_heap("H", "-1")

            return ValueTuple(value=t, expression_type=self.expression_type, is_mutable=False,
                              content_type=self.expression_type, capacity=None, is_tmp=True)

        print("literal.py::ERROR! Unknown literal type")

    def __str__(self):
        return f'LITERAL(val={self.value} type={self.expression_type})'
