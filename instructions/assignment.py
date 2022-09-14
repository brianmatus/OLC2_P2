from abstract.instruction import Instruction
from returns.exec_return import ExecReturn
from returns.ast_return import ASTReturn
from elements.env import Environment
from abstract.expression import Expression
from element_types.element_type import ElementType

from global_config import get_unique_number


class Assigment(Instruction):
    def __init__(self, _id: str, expression: Expression, line: int, column: int):
        super().__init__(line, column)
        self._id: str = _id
        self.expression: Expression = expression
        print(f"Instance of assignment with id {_id}")

    def execute(self, env: Environment) -> ExecReturn:
        expr = self.expression.execute(env)
        env.set_variable(self._id, expr, self.line, self.column)
        return ExecReturn(_type=ElementType.BOOL, value=True,
                          propagate_break=False, propagate_continue=False, propagate_method_return=False)

    def ast(self) -> ASTReturn:
        father_ref = get_unique_number()
        id_ref = get_unique_number()
        expr_ast = self.expression.ast()

        result: str = f'{father_ref}[label="ASSIGNMENT"]\n' \
                      f'{id_ref}[label={self._id}]\n' \
                      f'{father_ref} -> {id_ref}\n' \
                      f'{expr_ast}\n' \
                      f'{father_ref} -> {expr_ast.head_ref}\n'

        return ASTReturn(value=result, head_ref=father_ref)
