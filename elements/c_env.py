from typing import Union

import global_config

from errors.semantic_error import SemanticError
from element_types.c_expression_type import ExpressionType
from elements.value_tuple import ValueTuple


# class Value:
#     def __init__(self, value: str, is_tmp: bool, e_type: ExpressionType) -> None:
#         self.value = value
#         self.is_tmp = is_tmp
#         self.e_type = e_type
#         self.trueLabel = ""
#         self.falseLabel = ""


class Symbol:
    def __init__(self, symbol_id: str, expression_type: ExpressionType, stack_position,
                 is_init: bool, is_mutable: bool):
        self.stack_position = stack_position
        self.symbol_id = symbol_id
        self.symbol_type = expression_type
        self.is_init = is_init
        self.is_mutable = is_mutable


class ArraySymbol:
    def __init__(self, symbol_id: str, symbol_type: ExpressionType, dimensions: dict, stack_position,
                 is_init: bool, is_mutable: bool):
        self.stack_position = stack_position
        self.symbol_id = symbol_id
        self.symbol_type = symbol_type
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
        the_symbol: Union[Symbol, None] = self.symbol_table.get(variable_id)
        if the_symbol is not None:
            error_msg = f"Variable <{variable_id}> ya definida en el ambito actual." \
                        f"ALLOW_NESTED_VARIABLE_OVERRIDE={global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}"
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        the_symbol = Symbol(symbol_id=variable_id, expression_type=expression_type,
                            stack_position=self.size, is_init=is_init, is_mutable=is_mutable)

        self.symbol_table[variable_id] = the_symbol

        self.size += 1
        return the_symbol

    def save_variable_array(self, variable_id: str, content_type: ExpressionType, dimensions,
                            is_mutable: bool, is_init: bool, line: int, column: int):

        the_symbol: Union[ArraySymbol, None] = self.symbol_table.get(variable_id)

        if the_symbol is not None:
            error_msg = f'Variable <{variable_id}> ya esta definida en el ámbito actual. ' \
                        f'ALLOW_NESTED_VARIABLE_OVERRIDE =' \
                        f'{global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}>'

            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        the_symbol = ArraySymbol(variable_id, content_type, dimensions, self.size,
                                 is_init, is_mutable)
        self.symbol_table[variable_id] = the_symbol
        self.size += 1

        return the_symbol

    def get_variable(self, _id: str) -> Union[Symbol, ArraySymbol, None]:
        t = self.symbol_table.get(_id)
        if t is not None:
            return t

        # hit top
        if self.parent_environment is None:
            return None

        return self.parent_environment.get_variable(_id)

    def set_variable(self, _id: str, result: ValueTuple, line: int, column: int) -> Union[Symbol, ArraySymbol]:
        the_symbol: Union[Symbol, ArraySymbol] = self.get_variable(_id)

        # Non-existing check
        if the_symbol is None:
            error_msg = f'Variable {_id} no esta definida en el ámbito actual'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        # "Mutable"(const) check
        if not the_symbol.is_mutable and the_symbol.is_init:
            error_msg = f'Variable <{_id}> es constante y no puede ser asignado un valor nuevo'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        # Exclusions to type mismatch before:
        # var_t:usize expr_t:i64

        if the_symbol.symbol_type == ExpressionType.USIZE and result.expression_type == ExpressionType.INT:
            # the_symbol.value = result.value
            the_symbol.is_init = True
            return the_symbol

        if isinstance(the_symbol, ArraySymbol):
            # if result._type != ElementType.ARRAY_EXPRESSION:
            #     error_msg = f'Variable {_id} de tipo {the_symbol._type.name}(array' \
            #                 f'no puede ser asignada valor de tipo {result._type.name}(no array)'
            #     global_config.log_semantic_error(error_msg, line, column)
            #     raise SemanticError(error_msg, line, column)
            #
            # the_symbol.value = result.value
            # the_symbol.is_init = True
            # return
            # TODO implement
            for i in range(20):
                print(f"c_env.py::({i}/20 warnings) set_variable for array detected, to be implemented")

        # Type mismatch check
        if the_symbol.symbol_type != result.expression_type:
            error_msg = f'Variable {_id} de tipo {the_symbol.symbol_type.name} no puede ser asignada valor de tipo ' \
                        f'{result.expression_type.name}'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        # Allowed
        # the_symbol.value = result.value
        the_symbol.is_init = True

        return the_symbol

    def remove_child(self, child):  # child: Environment
        self.children_environment = list(filter(lambda p: p is not child, self.children_environment))
