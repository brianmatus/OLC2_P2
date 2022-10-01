from typing import List

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
# from expressions.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.match_clause import MatchClause
from abstract.expression import Expression

from global_config import log_semantic_error
from errors.semantic_error import SemanticError

from generator import Generator


class MatchI(Instruction):

    def __init__(self, compare_to: Expression, clauses: List[MatchClause], line: int, column: int):
        super().__init__(line, column)
        self.compare_to = compare_to
        self.clauses: List[MatchClause] = clauses
        # print("match conditional detected")

    def execute(self, env: Environment) -> ExecReturn:

        final_generator: Generator = Generator()
        final_generator.add_comment(f"<<<-------------------------------Match------------------------------->>>")

        compare_to_result = self.compare_to.execute(env)
        final_generator.combine_with(compare_to_result.generator)

        final_generator.add_comment("-----Update P for a new environment-----")
        final_generator.add_expression("P", "P", env.size, "+")

        exit_label = final_generator.new_label()

        clause: MatchClause
        for clause in self.clauses:
            clause.environment = Environment(env)

            # Reached Default Clause
            if clause.condition is None:
                for instruction in clause.instructions:
                    a = instruction.execute(clause.environment)
                    final_generator.combine_with(a.generator)
                final_generator.add_goto(exit_label)  # actually not needed for default but idk, just in case
                break  # 'continue' instead? idk, should be the last element anyways

            from elements.value_tuple import ValueTuple

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
            for instruction in clause.instructions:
                a = instruction.execute(clause.environment)
                final_generator.combine_with(a.generator)
            final_generator.add_goto(exit_label)
            final_generator.add_label([clause_exit])

        final_generator.add_label([exit_label])
        final_generator.add_comment("-----Revert P for a previous environment-----")
        final_generator.add_expression("P", "P", env.size, "-")

        return ExecReturn(generator=final_generator,
                          propagate_method_return=False, propagate_break=False, propagate_continue=False)
