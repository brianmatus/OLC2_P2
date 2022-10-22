from typing import List, Union

from abstract.expression import Expression
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from elements.match_expression_clause import MatchExpressionClause

from global_config import log_semantic_error
from errors.semantic_error import SemanticError
from generator import Generator


class MatchExpression(Expression):

    def __init__(self, compare_to: Expression, clauses: List[MatchExpressionClause], line: int, column: int):
        super().__init__(line, column)
        self.compare_to = compare_to
        self.clauses: List[MatchExpressionClause] = clauses
        # print("match conditional detected")

    def execute(self, environment: Environment) -> ValueTuple:

        final_generator: Generator = Generator(environment)
        final_generator.add_comment(f"<<<-------------------------------Match Expr------------------------------->>>")

        compare_to_result = self.compare_to.execute(environment)
        final_generator.combine_with(compare_to_result.generator)

        final_generator.add_comment("-----Update P for a new environment-----")
        final_generator.add_expression("P", "P", environment.size, "+")

        t_result = final_generator.new_temp()
        expr_result: Union[ValueTuple, None] = None

        exit_label = final_generator.new_label()

        clause: MatchExpressionClause
        for clause in self.clauses:
            clause.environment = Environment(environment)

            final_generator.add_comment("--------------CLAUSE--------------")

            # Reached Default Clause
            if clause.condition is None:

                expr_result = clause.expr.execute(clause.environment)
                final_generator.combine_with(expr_result.generator)
                final_generator.add_expression(t_result, expr_result.value, "", "")

                final_generator.add_goto(exit_label)  # actually not needed for default/else but idk, just in case
                break  # 'continue' instead? idk, should be the last element anyways
            #  Every other clause
            clause_accept = final_generator.new_label()
            clause_exit = final_generator.new_label()
            for cond in clause.condition:
                result: ValueTuple = cond.execute(clause.environment)

                final_generator.combine_with(result.generator)

                if result.expression_type is ExpressionType.BOOL:
                    error_msg = f"La expresión de un match no debe ser de tipo booleano." \
                                f"(Se obtuvo {result.value}->{result.expression_type})."

                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                final_generator.add_if(compare_to_result.value, result.value, "==", clause_accept)
            final_generator.add_goto(clause_exit)

            final_generator.add_label([clause_accept])
            expr_result = clause.expr.execute(clause.environment)
            final_generator.combine_with(expr_result.generator)
            final_generator.add_expression(t_result, expr_result.value, "", "")
            final_generator.add_goto(exit_label)
            final_generator.add_label([clause_exit])

        final_generator.add_label([exit_label])
        final_generator.add_comment("-----Revert P for a previous environment-----")
        final_generator.add_expression("P", "P", environment.size, "-")

        return ValueTuple(value=t_result, expression_type=expr_result.expression_type, is_mutable=False,
                          generator=final_generator, content_type=expr_result.content_type,
                          capacity=expr_result.capacity, is_tmp=True,
                          true_label=expr_result.true_label, false_label=expr_result.false_label)
