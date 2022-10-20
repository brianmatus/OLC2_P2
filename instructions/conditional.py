from typing import List

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
# from expressions.expression import Expression
# from elements.value_tuple import ValueTuple
from elements.condition_clause import ConditionClause

from global_config import log_semantic_error
from errors.semantic_error import SemanticError
from generator import Generator


class Conditional(Instruction):

    def __init__(self, clauses: List[ConditionClause], line: int, column: int):
        super().__init__(line, column)
        self.clauses: List[ConditionClause] = clauses
        # print("conditional detected")

    def execute(self, env: Environment) -> ExecReturn:

        final_generator: Generator = Generator()
        final_generator.add_comment(f"<<<-------------------------------If/Elseif/Else"
                                    f"------------------------------->>>")

        final_generator.add_comment("-----Update P for a new environment-----")
        final_generator.add_expression("P", "P", env.size, "+")

        exit_label = final_generator.new_label()

        clause: ConditionClause
        for clause in self.clauses:
            clause.environment = Environment(env)

            # Reached Else Clause
            if clause.condition is None:

                for instruction in clause.instructions:
                    a = instruction.execute(clause.environment)
                    final_generator.combine_with(a.generator)
                final_generator.add_goto(exit_label)  # actually not needed for default/else but idk, just in case
                break  # 'continue' instead? idk, should be the last element anyways

            from elements.value_tuple import ValueTuple

            clause_exit = final_generator.new_label()

            result: ValueTuple = clause.condition.execute(clause.environment)

            final_generator.combine_with(result.generator)

            if result.expression_type is not ExpressionType.BOOL:
                error_msg = f"La expresión de un if debe ser de tipo booleano." \
                            f"(Se obtuvo ->{result.expression_type})."
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            final_generator.add_label(result.false_label)
            final_generator.add_goto(clause_exit)

            final_generator.add_label(result.true_label)

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
