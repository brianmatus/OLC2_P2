from abstract.expression import Expression
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from returns.ast_return import ASTReturn
import global_config


class Literal(Expression):

    def __init__(self, value, _type: ElementType, line: int, column: int):
        super().__init__(line, column)
        self.value = value
        self._type = _type

    def execute(self, environment: Environment) -> ValueTuple:
        return ValueTuple(self.value, self._type, is_mutable=False, content_type=self._type, capacity=None)

    def ast(self) -> ASTReturn:
        father_ref = global_config.get_unique_number()
        value_ref = global_config.get_unique_number()

        value = f'{father_ref}[label="LITERAL\\n{self._type.name}"]\n' \
                f'{value_ref}[label="{self.value}"]\n' \
                f'{father_ref} -> {value_ref}\n'

        return ASTReturn(value=value, head_ref=father_ref)

    def __str__(self):
        return f'LITERAL(val={self.value} type={self._type})'

