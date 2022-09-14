from typing import List

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
# from expressions.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class Conditional(Instruction):

    def __init__(self, clauses: List[ConditionClause], line: int, column: int):
        super().__init__(line, column)
        self.clauses: List[ConditionClause] = clauses
        # print("conditional detected")

    def execute(self, env: Environment) -> ExecReturn:
        for clause in self.clauses:
            # print("evaluating class")

            env.remove_child(clause.environment)
            clause.environment = Environment(env)
            env.children_environment.append(clause.environment)

            # Reached Else Clause
            if clause.condition is None:
                # print("reached else")
                instruction: Instruction
                for instruction in clause.instructions:
                    result = instruction.execute(clause.environment)
                    if result.propagate_break or result.propagate_continue or result.propagate_method_return:
                        return result

                return ExecReturn(ElementType.BOOL, True, False, False, False)

            result = clause.condition.execute(clause.environment)

            if result._type is not ElementType.BOOL:
                error_msg = f"La expresión de un if debe ser de tipo booleano." \
                            f"(Se obtuvo {result.value}->{result._type})."

                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            # Clause accepted
            if result.value is True:
                for instruction in clause.instructions:
                    result = instruction.execute(clause.environment)
                    if result.propagate_break or result.propagate_continue or result.propagate_method_return:
                        return result

                return ExecReturn(ElementType.BOOL, True, False, False, False)

        # No execution
        return ExecReturn(ElementType.BOOL, False, False, False, False)
