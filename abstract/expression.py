from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from returns.ast_return import ASTReturn


class Expression:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
        self.expression_type: ExpressionType = None
        self.expression_type: ExpressionType = None
        self.true_label = ""
        self.false_label = ""

        if line == 0:
            print("LA LINEA ES 0")
        # Should have execute(environment: Environment) -> ValueTuple
        # Should have ast() -> ASTReturn

    def execute(self, environment: Environment) -> ValueTuple:
        print("ABSTRACT EXPRESSION EXECUTE CALLED, CHECK LMAO")
        return ValueTuple(None, None, is_mutable=False, content_type=None, capacity=[])

    def ast(self) -> ASTReturn:
        print("ABSTRACT EXPRESSION EXECUTE CALLED, CHECK LMAO")
        return ASTReturn('error super class', -420)
