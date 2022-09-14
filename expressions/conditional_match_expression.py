from typing import List

from elements.value_tuple import ValueTuple
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
# from expressions.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause
from elements.match_expression_clause import MatchExpressionClause
from abstract.expression import Expression

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class MatchExpression(Expression):

    def __init__(self, compare_to: Expression, clauses: List[MatchExpressionClause], line: int, column: int):
        super().__init__(line, column)
        self.compare_to = compare_to
        self.clauses: List[MatchExpressionClause] = clauses
        # print("match conditional detected")

    def execute(self, environment: Environment) -> ValueTuple:

        compare_to_result = self.compare_to.execute(environment)

        r_type = None
        for clause in self.clauses:
            res = clause.expr.execute(environment)
            if r_type is None:
                r_type = res._type

            if res._type != r_type:
                error_msg = f"Todas las expresiones de un match-expr deben devolver el mismo tipo." \
                            f"({res._type.name} != {r_type.name})"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)


        for clause in self.clauses:
            # print("evaluating clauss")

            environment.remove_child(clause.environment)
            clause.environment = Environment(environment)
            environment.children_environment.append(clause.environment)

            # Reached Else Clause
            if clause.condition is None:
                return clause.expr.execute(environment)

            for condition in clause.condition:
                result = condition.execute(clause.environment)
                if result._type is not compare_to_result._type:
                    error_msg = f"La expresión de un match debe ser del mismo tipo que la variable a evaluar"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                # Clause accepted
                if result.value is compare_to_result.value:
                    return clause.expr.execute(environment)

        # No execution
        return ValueTuple(ElementType.VOID, None, is_mutable=False)
