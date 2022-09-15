from errors.semantic_error import SemanticError
import global_config
from abstract.instruction import Instruction
from returns.ast_return import ASTReturn
from returns.exec_return import ExecReturn
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment
from abstract.expression import Expression
from elements.value_tuple import ValueTuple
from elements.c_env import Symbol
from generator import Generator


class Declaration(Instruction):

    def __init__(self, variable_id: str, expression_type: ExpressionType, expression: Expression, is_mutable: bool, line: int, column: int):
        super().__init__(line, column)
        self.variable_id = variable_id
        self.expression_type: ExpressionType = expression_type
        self.expression: Expression = expression
        self.is_mutable = is_mutable

        # if self._type is None:
        #     print(f'Instance of declaration with id:{self._id} type:inferred')
        # else:
        #     print(f'Instance of declaration with id:{self._id} type:{self._type.name}')

    def execute(self, env: Environment) -> ExecReturn:


        # Using not_init instead
        if self.expression is None:
            env.save_variable(self.variable_id, self.expression_type, None,
                              is_mutable=self.is_mutable, is_init=False, is_array=False,
                              line=self.line, column=self.column)

            return ExecReturn(ExpressionType.BOOL, True, False, False, False)

        expr: Expression = self.expression
        # print(expr)

        # Infer if not explicitly specified
        if self.expression_type is None:
            self.expression_type = expr.expression_type

        # Check same type

        if expr.expression_type == self.expression_type:


            generator = Generator()

            result: ValueTuple = expr.execute(env)
            tmp_var: Symbol = env.save_variable(self.variable_id, self.expression_type,
                                                self.is_mutable, True, self.line, self.column)

            generator.add_set_stack(str(tmp_var.position), str(result.value))
            return ExecReturn(generator=generator,
                              propagate_method_return=False, propagate_continue=False, propagate_break=False)

        # Exceptions of same type:

        # char var_type with str expr_type
        if self.expression_type == ExpressionType.CHAR and expr.expression_type == ExpressionType.STRING_PRIMITIVE:
            env.save_variable(self.variable_id, self.expression_type, expr.value,
                              is_mutable=self.is_mutable, is_init=True, is_array=False,
                              line=self.line, column=self.column)

            return ExecReturn(ExpressionType.BOOL, True, False, False, False)


        # usize var_type with int expr_type


        if self.expression_type == ExpressionType.USIZE and expr.expression_type == ExpressionType.INT:

            if global_config.is_arithmetic_pure_literals(self.expression):
                # if expr.value < 0:
                #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                #     global_config.log_semantic_error(error_msg, self.line, self.column)
                #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                env.save_variable(self.variable_id, self.expression_type, expr.value,
                                  is_mutable=self.is_mutable, is_init=True, is_array=False,
                                  line=self.line, column=self.column)

                return ExecReturn(ExpressionType.BOOL, True, False, False, False)





        # Error:
        error_msg = f'Asignacion de tipo {expr.expression_type.name} a variable <{self.variable_id}> de tipo {self.expression_type.name}'
        global_config.log_semantic_error(error_msg, self.line, self.column)
        raise SemanticError(error_msg, self.line, self.column)


