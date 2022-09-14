from typing import Union

from errors.semantic_error import SemanticError
import global_config

from elements.value_tuple import ValueTuple

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from expressions.vector import VectorExpression
from element_types.element_type import ElementType

from elements.env import Environment

from element_types.vector_def_type import VectorDefType


class VectorDeclaration(Instruction):

    # TODO add array_reference and var_reference to expression type,
    def __init__(self, _id: str, vector_type: VectorDefType, expression: Union[VectorExpression, None],
                 is_mutable: bool, line: int, column: int):
        self._id = _id
        self.vector_type: VectorDefType = vector_type
        self.dimensions: int = -1
        self.expression = expression
        self.values = []
        self.is_mutable = is_mutable
        super().__init__(line, column)
        self.var_type = None

    def execute(self, env: Environment) -> ExecReturn:
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

        r = global_config.match_vector_deepness(level, expression_result.value)
        # print(f'Dimension match:{r}')
        if not r:
            error_msg = f'La definición del vector no concuerda con la expresión dada (dimensiones)'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        self.values = expression_result.value

        r = global_config.match_array_type(self.var_type, expression_result.value)
        # print(f'Type match:{r}')

        if not r:
            error_msg = f'Uno o mas elementos del vector no concuerdan en tipo con su definición'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        capacity = self.expression.capacity.execute(env)

        if capacity._type not in [ElementType.INT, ElementType.USIZE]:
            error_msg = f'La capacidad de un vector debe ser un numero entero (de ser negativo se tomara 0)'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        env.save_variable_vector(self._id, ElementType.VECTOR, the_type, level, self.values, self.is_mutable,
                                 [int(capacity.value)], self.line, self.column)

        return ExecReturn(ElementType.BOOL, True, False, False, False)





