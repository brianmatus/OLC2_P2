from typing import Union, List

import global_config
from returns.ast_return import ASTReturn
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from elements.env import Environment
from abstract.expression import Expression
from expressions.array_expression import ArrayExpression
from elements.array_symbol import ArraySymbol
from element_types.element_type import ElementType
from elements.value_tuple import ValueTuple

from errors.semantic_error import SemanticError
from global_config import log_semantic_error


class ArrayAssignment(Instruction):

    def __init__(self, _id: str, indexes: List[Expression], expr: Union[Expression, ArrayExpression],
                 line: int, column: int):
        super().__init__(line, column)
        self._id = _id
        self.indexes: List[Expression] = indexes
        self.expr: Expression = expr

    def execute(self, env: Environment) -> ExecReturn:

        expr = self.expr.execute(env)

        the_symbol: ArraySymbol = env.recursive_get(self._id)

        if the_symbol is None:
            error_msg = f'Variable {self._id} no esta definida en el ambito actual'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if not isinstance(the_symbol, ArraySymbol):
            error_msg = f'Variable {self._id} no es de tipo array y no puede ser indexada'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if not the_symbol.is_mutable and the_symbol.is_init:
            error_msg = f'Variable {self._id} es constante y no puede ser asignado un valor nuevo'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        dimensions = []
        ind: Expression
        for ind in self.indexes:
            result: ValueTuple = ind.execute(env)

            if result._type not in [ElementType.INT, ElementType.USIZE] or isinstance(result.value, list):
                error_msg = f'El acceso a array debe de ser con tipo entero/usize'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            dimensions.append(result.value)

        if not isinstance(expr.value, list):
            if the_symbol._type != expr._type:
                error_msg = f'El elemento del array no concuerda en tipo con su definición'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

        else:
            r = global_config.match_array_type(the_symbol._type, expr.value)
            # print(f'Type match:{r}')

            if not r:
                error_msg = f'Uno o mas elementos del array no concuerdan en tipo con su definición'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

        # print(the_symbol.dimensions)
        # print(dimensions)

        # Too much dimensions?
        if len(dimensions) > len(the_symbol.dimensions):
            error_msg = f'La profundidad del array es menor a la ingresada' \
                        f'({len(dimensions)} > {len(the_symbol.dimensions)})'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)




        resulting = the_symbol
        for i in range(len(dimensions)):
            # print(f"requested:{dimensions[i]} existing:{the_symbol.dimensions[i + 1]}")
            if dimensions[i] > the_symbol.dimensions[i + 1]:
                error_msg = f'Las dimensiones del array son menores a las ingresadas'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            resulting = resulting.value[dimensions[i]]



        # print(resulting)

        # Same dimensions?

        to_match = global_config.extract_dimensions_to_dict(resulting)

        # print("aqui xd")
        # print(to_match)
        # print(expr.value)

        match = global_config.match_dimensions(list(to_match.keys()), expr.value)
        # print(match)

        # print('aqui 2')
        # print("to be replaced:")
        # print(resulting)
        # print("the replacement:")
        # print(expr)

        resulting.value = expr.value

        return ExecReturn(ElementType.BOOL, True, False, False, False)

        # No dimensions?





