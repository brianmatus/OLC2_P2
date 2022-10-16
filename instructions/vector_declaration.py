from typing import Union

from errors.semantic_error import SemanticError
import global_config

from elements.value_tuple import ValueTuple

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from expressions.vector import VectorExpression
from element_types.c_expression_type import ExpressionType

from elements.c_env import Environment

from element_types.vector_def_type import VectorDefType
from generator import Generator


class VectorDeclaration(Instruction):

    # TODO add array_reference and var_reference to expression type,
    def __init__(self, variable_id: str, vector_type: Union[VectorDefType, None],
                 expression: Union[VectorExpression, None],
                 is_mutable: bool, line: int, column: int):
        self.variable_id = variable_id
        self.vector_type: Union[VectorDefType, None] = vector_type
        self.dimensions: int = -1
        self.expression = expression
        self.values = []
        self.is_mutable = is_mutable
        super().__init__(line, column)
        self.var_type = None

    def execute(self, env: Environment) -> ExecReturn:

        gen = Generator()
        gen.add_comment(f"-------------------------------Vector Declaration of {self.variable_id}"
                        f"-------------------------------")

        # Find out what dimension should I be
        level = 0
        the_type: VectorDefType = self.vector_type
        while True:
            if not isinstance(the_type, VectorDefType):
                self.var_type = the_type
                break

            the_type = the_type.content_type
            level += 1

        # Get my supposed values and match dimensions
        expression_result: ValueTuple = self.expression.execute(env)
        gen.combine_with(expression_result.generator)

        # Defined without type
        if level == 0:
            level = len(expression_result.capacity)

        # print(f'Dimension match:{r}')
        if len(expression_result.capacity) != level:
            error_msg = f'La definición del vector no concuerda con la expresión dada (dimensiones)'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if expression_result.expression_type not in [ExpressionType.VECTOR, ExpressionType.ARRAY]:
            error_msg = f'Variable {self.variable_id} de tipo {ExpressionType.VECTOR.name} no puede ser ' \
                        f'asignada valor de tipo {expression_result.expression_type.name}'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if expression_result.content_type is None:
            if the_type is None:
                error_msg = f'Un vector declarado con Vec::new() o Vec::with_capacity() debe tener un tipo especificado'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)
            expression_result.content_type = the_type


        if the_type is None:
            the_type = expression_result.content_type

        if expression_result.content_type != the_type:
            error_msg = f'El vector no concuerdan en tipo con su definición ' \
                        f'({the_type.name} != {expression_result.content_type.name})'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        the_symbol = env.save_variable_vector(self.variable_id, the_type, level, self.is_mutable,
                                              self.line, self.column)

        place = gen.new_temp()
        gen.add_expression(place, "P", the_symbol.heap_position, "+")
        gen.add_set_stack(place, expression_result.value)

        return ExecReturn(generator=gen, propagate_method_return=False, propagate_break=False, propagate_continue=False)





