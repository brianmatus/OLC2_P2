from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from elements.env import Environment
from returns.ast_return import ASTReturn

class Expression:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
        self._type: ElementType = None

        if line == 0:
            print("LA LINEA ES 0")
        # Should have execute(environment: Environment) -> ValueTuple
        # Should have ast() -> ASTReturn

    def execute(self, environment: Environment) -> ValueTuple:
        print("ABSTRACT EXPRESSION EXECUTE CALLED, CHECK LMAO")
        return ValueTuple(None, None, is_mutable=False)

    def ast(self) -> ASTReturn:
        print("ABSTRACT EXPRESSION EXECUTE CALLED, CHECK LMAO")
        return ASTReturn('error super class', -420)
