from errors.semantic_error import SemanticError
import global_config
from abstract.instruction import Instruction
from returns.ast_return import ASTReturn
from returns.exec_return import ExecReturn
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from abstract.expression import Expression
from elements.value_tuple import ValueTuple


class ExpressionAsInstruction(Instruction):

    def __init__(self, expr: Expression, line: int, column: int):
        super().__init__(line, column)
        self.expr = expr

    def execute(self, env: Environment) -> ExecReturn:
        r: ValueTuple = self.expr.execute(env)

        return ExecReturn(r.generator, False, False, False)
    