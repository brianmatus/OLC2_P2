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

    def execute(self, environment: Environment, forced_string=False) -> ValueTuple:

        if self.expression_type in [ExpressionType.INT, ExpressionType.FLOAT]:

            return ValueTuple(value=self.value, expression_type=self.expression_type, is_mutable=False,
                              content_type=self.expression_type, capacity=None, is_tmp=False, generator=Generator(),
                              true_label=[], false_label=[])

        if self.expression_type == ExpressionType.CHAR:
            return ValueTuple(value=str(ord(self.value)), expression_type=self.expression_type, is_mutable=False,
                              content_type=self.expression_type, capacity=None, is_tmp=False, generator=Generator(),
                              true_label=[], false_label=[])

        if self.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
            generator = Generator()

            if forced_string:
                return ValueTuple(value=None, expression_type=self.expression_type, is_mutable=False,
                                  content_type=self.expression_type, capacity=None, is_tmp=True, generator=generator,
                                  true_label=[self.value], false_label=[])


            generator.add_comment(f"-----String: {self.value}-----")
            t = generator.new_temp()
            generator.add_expression(t, "H", "", "")
            for char in self.value:
                generator.add_set_heap("H", str(ord(char)))
                generator.add_next_heap()
            generator.add_set_heap("H", "-1")
            generator.add_next_heap()

            return ValueTuple(value=t, expression_type=self.expression_type, is_mutable=False,
                              content_type=self.expression_type, capacity=None, is_tmp=True, generator=generator,
                              true_label=[self.value], false_label=[])

        if self.expression_type == ExpressionType.BOOL:
            generator = Generator()
            the_label = generator.new_label()
            generator.add_goto(the_label)
            if self.value == 0:
                return ValueTuple(value=generator, expression_type=self.expression_type, is_mutable=False,
                                  content_type=self.expression_type, capacity=None, is_tmp=True, generator=generator,
                                  true_label=[], false_label=[the_label])

            return ValueTuple(value=generator, expression_type=self.expression_type, is_mutable=False,
                              content_type=self.expression_type, capacity=None, is_tmp=True, generator=generator,
                              true_label=[the_label], false_label=[])

        print("literal.py::ERROR! Unknown literal type")

    def __str__(self):
        return f'LITERAL(val={self.value} type={self.expression_type})'
