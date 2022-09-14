from typing import Union

from errors.semantic_error import SemanticError
import global_config

from elements.value_tuple import ValueTuple

from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from expressions.array_expression import ArrayExpression
from element_types.element_type import ElementType

from elements.env import Environment

from element_types.array_def_type import ArrayDefType


class ArrayDeclaration(Instruction):

    # TODO add array_reference and var_reference to expression type,
    def __init__(self, _id: str, array_type: ArrayDefType, expression: Union[ArrayExpression, None], is_mutable: bool,
                 line: int, column: int):
        self._id = _id
        self.array_type = array_type
        self.dimensions: int = -1
        self.expression = expression
        self.values = []
        self.is_mutable = is_mutable
        super().__init__(line, column)
        self.var_type = None

    def execute(self, env: Environment) -> ExecReturn:
        # Find out what dimension should I be
        level = 1
        sizes = {}
        arr_def_type = self.array_type
        while True:

            the_size = arr_def_type.size_expr.execute(env)
            if the_size._type is not ElementType.INT:
                error_msg = f'Tamaño de array debe ser una expresion entera'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            sizes[level] = int(the_size.value)

            if not arr_def_type.is_nested_array:
                # print(f'Inner most type:{arr_def_type.content_type}')
                self.var_type = arr_def_type.content_type
                break

            arr_def_type = arr_def_type.content_type
            level += 1

        # Not initialized
        if self.expression is None:
            env.save_variable_array(self._id, self.var_type, self.dimensions, None, self.is_mutable, False,
                                    self.line, self.column)

            return ExecReturn(ElementType.BOOL, True, False, False, False)

        # Get my supposed values and match dimensions
        expression_result: ValueTuple = self.expression.execute(env)
        r = global_config.match_dimensions(list(sizes.values()), expression_result.value)
        # print(f'Dimension match:{r}')
        if not r:
            error_msg = f'Uno o mas elementos del array no concuerdan en tamaño con su definición'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        self.values = expression_result.value
        self.dimensions = sizes

        r = global_config.match_array_type(self.var_type, expression_result.value)
        # print(f'Type match:{r}')

        if not r:
            error_msg = f'Uno o mas elementos del array no concuerdan en tipo con su definición'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        env.save_variable_array(self._id, self.var_type, self.dimensions, self.values, self.is_mutable, True,
                                self.line, self.column)

        return ExecReturn(ElementType.BOOL, True, False, False, False)





