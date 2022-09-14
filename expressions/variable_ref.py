from abstract.expression import Expression
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from returns.ast_return import ASTReturn

from errors.semantic_error import SemanticError

from elements.vector_symbol import VectorSymbol
from elements.array_symbol import ArraySymbol
from elements.symbol import Symbol

import global_config


class VariableReference(Expression):

    def __init__(self, _id: str, line: int, column: int):
        super().__init__(line, column)
        self._id = _id

    def execute(self, environment: Environment) -> ValueTuple:
        the_symbol: Symbol = environment.recursive_get(self._id)
        if the_symbol is None:
            print("Variable not defined in scope")
            error_msg = f'Variable {self._id} no esta definida en el ambito actual'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if isinstance(the_symbol, VectorSymbol):
            return ValueTuple(value=the_symbol.value, _type=the_symbol._type, is_mutable=the_symbol.is_mutable,
                              content_type=the_symbol.content_type, capacity=the_symbol.capacity)

        return ValueTuple(value=the_symbol.value, _type=the_symbol._type, is_mutable=the_symbol.is_mutable,
                          content_type=None, capacity=None)

    def ast(self) -> ASTReturn:
        return ASTReturn("", -1)

