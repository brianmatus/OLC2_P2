from expressions.expression import Expression
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from returns.ast_return import ASTReturn

from elements.array_symbol import ArraySymbol
from elements.vector_symbol import VectorSymbol

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class ArrayReference(Expression):

    def __init__(self, _id: str, indexes: list, line: int, column: int):
        super().__init__(line, column)
        self._id = _id
        self.indexes = indexes

    def execute(self, environment: Environment) -> ValueTuple:
        the_symbol: ArraySymbol = environment.recursive_get(self._id)

        if the_symbol is None:
            error_msg = f'Variable {self._id} no esta definida en el ambito actual'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        dimensions = []

        # print(f'Indexes:{self.indexes}')

        index: Expression
        for index in self.indexes:
            result = index.execute(environment)

            if result._type not in [ElementType.INT, ElementType.USIZE] or isinstance(result.value, list):
                error_msg = f'El acceso a array debe de ser con tipo entero/usize (Se obtuvo {result._type.name})'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            dimensions.append(result.value)

        # print(f'Evaluated indexes:{dimensions}')
        # print(f'Symbol indexes:{the_symbol.dimensions}')

        if isinstance(the_symbol, VectorSymbol):
            print("vect, not array lmao")
            if the_symbol.deepness < len(dimensions):
                error_msg = f'La profundidad del vector es menor a la ingresada'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            returning = the_symbol.value
            aux = the_symbol.deepness
            for i in range(len(dimensions)):
                # print(f"requested:{dimensions[i]} existing:{the_symbol.dimensions[i+1]}")
                if dimensions[i] > len(returning):
                    error_msg = f'Las dimensiones del vector son menores a las ingresadas'
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                returning = returning[dimensions[i]].value

            if isinstance(returning, ValueTuple):
                return ValueTuple(_type=returning._type, value=returning.value, is_mutable=the_symbol.is_mutable,
                                  content_type=the_symbol.content_type, capacity=the_symbol.capacity)

            if isinstance(returning, list):
                return ValueTuple(_type=the_symbol._type, value=returning, is_mutable=the_symbol.is_mutable,
                                  content_type=the_symbol.content_type, capacity=the_symbol.capacity)

            return ValueTuple(_type=the_symbol.content_type, value=returning, is_mutable=the_symbol.is_mutable,
                              content_type=the_symbol.content_type, capacity=the_symbol.capacity)

        # ARRAY:

        if len(the_symbol.dimensions.keys()) < len(dimensions):
            error_msg = f'La profundidad del array es menor a la ingresada'
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        returning = the_symbol.value
        for i in range(len(dimensions)):
            # print(f"requested:{dimensions[i]} existing:{the_symbol.dimensions[i+1]}")
            if dimensions[i] > the_symbol.dimensions[i+1]:
                error_msg = f'Las dimensiones del array son menores a las ingresadas'
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            returning = returning[dimensions[i]].value

        if isinstance(returning, ValueTuple):
            return ValueTuple(_type=returning._type, value=returning.value, is_mutable=the_symbol.is_mutable,
                              content_type=None, capacity=None)
        return ValueTuple(_type=the_symbol._type, value=returning, is_mutable=the_symbol.is_mutable,
                          content_type=None, capacity=None)




