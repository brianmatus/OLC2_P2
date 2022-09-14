from typing import List

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
# from expressions.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause
from elements.match_clause import MatchClause
from abstract.expression import Expression

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class MatchI(Instruction):

    def __init__(self, compare_to: Expression, clauses: List[MatchClause], line: int, column: int):
        super().__init__(line, column)
        self.compare_to = compare_to
        self.clauses: List[MatchClause] = clauses
        # print("match conditional detected")

    def execute(self, env: Environment) -> ExecReturn:

        compare_to_result = self.compare_to.execute(env)

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

            for condition in clause.condition:
                result = condition.execute(clause.environment)

                if result._type is not compare_to_result._type:
                    error_msg = f"La expresión de un match debe ser del mismo tipo que la variable a evaluar"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                # Clause accepted
                if result.value is compare_to_result.value:
                    for instruction in clause.instructions:
                        result = instruction.execute(clause.environment)
                        if result.propagate_break or result.propagate_continue or result.propagate_method_return:
                            return result

                    return ExecReturn(ElementType.BOOL, True, False, False, False)

        # No execution
        return ExecReturn(ElementType.BOOL, False, False, False, False)
