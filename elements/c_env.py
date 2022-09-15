from typing import Union, List

import global_config

from errors.semantic_error import SemanticError
from element_types.c_expression_type import ExpressionType
from elements.value_tuple import ValueTuple


class Value:
    def __init__(self, value: str, is_tmp: bool, e_type: ExpressionType) -> None:
        self.value = value
        self.is_tmp = is_tmp
        self.e_type = e_type
        self.trueLabel = ""
        self.falseLabel = ""


class Symbol:
    def __init__(self, symbol_id: str, expression_type: ExpressionType, dimensions: dict, position,
                 is_init: bool, is_mutable: bool):
        self.position = position
        self.symbol_id = symbol_id
        self.symbol_type = expression_type
        self.is_init = is_init
        self.is_mutable = is_mutable
        self.dimensions: {} = dimensions


class Environment:
    def __init__(self, parent_environment):

        self.parent_environment: Environment = parent_environment
        self.symbol_table: dict = {}
        self.size = 0
        self.children_environment = []

        if self.parent_environment is not None:
            pass
            # self.size = parent_environment.size  #TODO wtf is this?

    def save_variable(self, variable_id: str, expression_type: ExpressionType, is_mutable: bool, is_init: bool,
                      line: int, column: int):
        the_symbol: Union[Symbol, None]
        the_symbol = self.symbol_table.get(variable_id)
        if the_symbol is not None:
            error_msg = f"Variable <{variable_id}> ya definida en el ambito actual." \
                        f"ALLOW_NESTED_VARIABLE_OVERRIDE={global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}"
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        the_symbol = Symbol(symbol_id=variable_id, expression_type=expression_type, position=self.size, is_init=is_init,
                            is_mutable=is_mutable, dimensions={})

        self.size += 1
        return the_symbol

    def get_variable(self, _id: str) -> Union[Symbol, None]:
        t = self.symbol_table.get(_id)
        if t is not None:
            return t

        # hit top
        if self.parent_environment is None:
            return None

        return self.parent_environment.get_variable(_id)

    def remove_child(self, child):  # child: Environment
        self.children_environment = list(filter(lambda p: p is not child, self.children_environment))
