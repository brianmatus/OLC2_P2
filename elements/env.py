from typing import Union, List

from errors.semantic_error import SemanticError
import global_config
from elements.symbol import Symbol
from elements.array_symbol import ArraySymbol
from elements.vector_symbol import VectorSymbol
from element_types.element_type import ElementType
from elements.value_tuple import ValueTuple


class Environment:
    def __init__(self, parent_environment):

        self.parent_environment: Environment = parent_environment
        self.symbol_table: dict = {}
        self.children_environment = []

    def save_variable(self, _id: str, _type: ElementType, value, is_mutable: bool, is_init: bool, is_array: bool,
                      line: int, column: int):
        the_symbol: Union[Symbol, None]

        if global_config.ALLOW_NESTED_VARIABLE_OVERRIDE:
            the_symbol = self.symbol_table.get(_id)

            if the_symbol is not None:
                error_msg = f"Variable <{_id }> ya definida en el ambito actual." \
                            f"ALLOW_NESTED_VARIABLE_OVERRIDE={global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}"
                global_config.log_semantic_error(error_msg, line, column)
                raise SemanticError(error_msg, line, column)

        else:
            the_symbol = self.recursive_get(_id)
            if the_symbol is not None:
                error_msg = f"Variable <{_id }> ya definida en el ambito actual." \
                            f"ALLOW_NESTED_VARIABLE_OVERRIDE={global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}"
                global_config.log_semantic_error(error_msg, line, column)
                raise Exception(error_msg)

        self.symbol_table[_id] = Symbol(_id, _type, value, is_init, is_mutable)

    def save_variable_array(self, _id: str, _type: ElementType, dimensions: dict, value, is_mutable: bool, is_init: bool,
                            line: int, column: int):

        the_symbol: Union[ArraySymbol, None]

        if global_config.ALLOW_NESTED_VARIABLE_OVERRIDE:
            the_symbol = self.symbol_table.get(_id)

            if the_symbol is not None:
                error_msg = f'Variable <{_id}> ya esta definida en el ámbito actual. ALLOW_NESTED_VARIABLE_OVERRIDE =' \
                            f'{global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}>'

                global_config.log_semantic_error(error_msg, line, column)
                raise SemanticError(error_msg, line, column)

        else:
            the_symbol = self.recursive_get(_id)
            if the_symbol is not None:
                error_msg = "Variable <" + _id + "> ya definida en el ambito actual. ALLOW_NESTED_VARIABLE_OVERRIDE="\
                            + global_config.ALLOW_NESTED_VARIABLE_OVERRIDE

                global_config.log_semantic_error(error_msg, line, column)
                raise Exception(error_msg)

        self.symbol_table[_id] = ArraySymbol(_id, _type, dimensions, value, is_init, is_mutable)

    def save_variable_vector(self, _id: str, _type: ElementType, content_type: ElementType, deepness: int, value,
                             is_mutable: bool, capacity: List[int],
                             line: int, column: int):

        the_symbol: Union[VectorSymbol, None]

        if global_config.ALLOW_NESTED_VARIABLE_OVERRIDE:
            the_symbol = self.symbol_table.get(_id)
            if the_symbol is not None:
                error_msg = f'Variable <{_id}> ya esta definida en el ámbito actual. ALLOW_NESTED_VARIABLE_OVERRIDE =' \
                            f'{global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}>'

                global_config.log_semantic_error(error_msg, line, column)
                raise SemanticError(error_msg, line, column)
        else:
            the_symbol = self.recursive_get(_id)
            if the_symbol is not None:
                error_msg = "Variable <" + _id + "> ya definida en el ambito actual. ALLOW_NESTED_VARIABLE_OVERRIDE="\
                            + global_config.ALLOW_NESTED_VARIABLE_OVERRIDE
                global_config.log_semantic_error(error_msg, line, column)
                raise Exception(error_msg)

        the_capacity = capacity
        if the_capacity[0] == -1:
            the_capacity[0] = len(value)

        self.symbol_table[_id] = VectorSymbol(_id, _type, content_type, deepness, value, is_mutable, the_capacity)


    def set_variable(self, _id: str, result: ValueTuple, line: int, column: int):
        the_symbol: Union[Symbol, ArraySymbol] = self.recursive_get(_id)

        # Non-existing check
        if the_symbol is None:
            error_msg = f'Variable {_id} no esta definida en el ambito actual'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        # "Mutable"(const) check
        if not the_symbol.is_mutable and the_symbol.is_init:
            error_msg = f'Variable <{_id}> es constante y no puede ser asignado un valor nuevo'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)


        #Exclusions to type mismatch before:
        # var_t:usize expr_t:i64

        if the_symbol._type == ElementType.USIZE and result._type == ElementType.INT:
            the_symbol.value = result.value
            the_symbol.is_init = True
            return

        if isinstance(the_symbol, ArraySymbol):
            if result._type != ElementType.ARRAY_EXPRESSION:
                error_msg = f'Variable {_id} de tipo {the_symbol._type.name}(array' \
                            f'no puede ser asignada valor de tipo {result._type.name}(no array)'
                global_config.log_semantic_error(error_msg, line, column)
                raise SemanticError(error_msg, line, column)

            the_symbol.value = result.value
            the_symbol.is_init = True
            return

        # Type mismatch check
        if the_symbol._type != result._type:
            error_msg = f'Variable {_id} de tipo {the_symbol._type.name} no puede ser asignada valor de tipo {result._type.name}'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        # Allowed
        the_symbol.value = result.value
        the_symbol.is_init = True

    # TODO set array variable

    def recursive_get(self, _id: str) -> Union[Symbol, ArraySymbol, None]:
        if self.symbol_table.get(_id) is not None:
            return self.symbol_table.get(_id)

        # hit top
        if self.parent_environment is None:
            return None

        return self.parent_environment.recursive_get(_id)

    def remove_child(self, child):  # child: Environment
        self.children_environment = list(filter(lambda p: p is not child, self.children_environment))


