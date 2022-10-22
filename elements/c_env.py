from typing import Union, List, Tuple

import global_config

from errors.semantic_error import SemanticError
from element_types.c_expression_type import ExpressionType
from elements.value_tuple import ValueTuple

from enum import Enum

# class Value:
#     def __init__(self, value: str, is_tmp: bool, e_type: ExpressionType) -> None:
#         self.value = value
#         self.is_tmp = is_tmp
#         self.e_type = e_type
#         self.trueLabel = ""
#         self.falseLabel = ""


class Symbol:
    def __init__(self, symbol_id: str, expression_type: ExpressionType, heap_position, is_init: bool, is_mutable: bool):
        self.heap_position = heap_position
        self.symbol_id = symbol_id
        self.symbol_type = expression_type
        self.is_init = is_init
        self.is_mutable = is_mutable


class ArraySymbol:
    def __init__(self, symbol_id: str, symbol_type: ExpressionType, dimensions: dict, heap_position,
                 is_init: bool, is_mutable: bool):
        self.heap_position = heap_position
        self.symbol_id = symbol_id
        self.symbol_type = symbol_type
        self.is_init = is_init
        self.is_mutable = is_mutable
        if "embedded_type" in dimensions.keys():
            dimensions.pop("embedded_type")
        self.dimensions: {} = dimensions



class VectorSymbol:
    def __init__(self, symbol_id: str, vector_type: ExpressionType, deepness: int, heap_position, is_mutable: bool):
        self.heap_position = heap_position
        self.symbol_id: str = symbol_id
        self.symbol_type: ExpressionType = vector_type
        self.is_mutable: bool = is_mutable
        self.deepness: int = deepness


TransferType = Enum('ElementType',
                    ' '.join([
                        'BREAK',
                        'CONTINUE',
                        'RETURN',
                        'DEFAULT_INVALID'
                    ]))


class TransferInstruction:
    def __init__(self, transfer_type: TransferType, label_to_jump: str, with_value: bool):
        self.transfer_type = transfer_type
        self.label_to_jump = label_to_jump
        self.with_value = with_value


class Environment:
    def __init__(self, parent_environment, return_type: ExpressionType = ExpressionType.VOID):

        self.parent_environment: Environment = parent_environment  # TODO weak ref?
        self.symbol_table: dict = {}
        self.size = 0
        self.children_environment = []

        self.transfer_control: List[TransferInstruction] = []
        self.return_type: ExpressionType = return_type

        self.associated_tmps = []
        self.is_function_env = False

        if self.parent_environment is not None:
            pass
            # self.size = parent_environment.size  #TODO wtf is this?

    def save_variable(self, variable_id: str, expression_type: ExpressionType, is_mutable: bool, is_init: bool,
                      line: int, column: int):
        the_symbol: Union[Symbol, None] = self.symbol_table.get(variable_id)
        if the_symbol is not None:
            error_msg = f"Variable <{variable_id}> ya definida en el ámbito actual." \
                        f"ALLOW_NESTED_VARIABLE_OVERRIDE={global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}"
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        the_symbol = Symbol(symbol_id=variable_id, expression_type=expression_type,
                            heap_position=self.size, is_init=is_init, is_mutable=is_mutable)

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

    def save_variable_vector(self, variable_id: str, content_type: ExpressionType, deepness, is_mutable: bool,
                             line: int, column: int):

        the_symbol: Union[VectorSymbol, None] = self.symbol_table.get(variable_id)

        if the_symbol is not None:
            error_msg = f'Variable <{variable_id}> ya esta definida en el ámbito actual. ' \
                        f'ALLOW_NESTED_VARIABLE_OVERRIDE =' \
                        f'{global_config.ALLOW_NESTED_VARIABLE_OVERRIDE}>'

            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        the_symbol = VectorSymbol(variable_id, content_type, deepness, self.size, is_mutable)
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

    # TODO case for same env is correct?
    def get_variable_p_deepness(self, _id: str, r) -> int:
        t: ArraySymbol = self.symbol_table.get(_id)
        if t is not None:
            if r == 0:
                return 0-t.heap_position  # TODO check if correct???
                # return t.heap_position  # TODO check if correct???
            return r - t.heap_position

        # hit top
        if self.parent_environment is None:
            return -99999
        return self.parent_environment.get_variable_p_deepness(_id, r+self.parent_environment.size)

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
            for i in range(20):
                print(f"c_env.py::({i}/20 warnings) set_variable for array detected, this should not happen")

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

    def get_transfer_control_label(self, transfer_type: TransferType, with_value: bool, line: int, column: int,
                                   p_revert=0, first=True, a=None)\
            -> Tuple[str, ExpressionType, int, List[str]]:
        a = []

        for trans in self.transfer_control:
            if trans.transfer_type == transfer_type:
                if trans.with_value == with_value:
                    if transfer_type == TransferType.RETURN:
                        if first:
                            a = self.get_tmps_from_function()
                            return trans.label_to_jump, self.return_type, p_revert, a
                        return trans.label_to_jump, self.return_type, p_revert+self.size, a

                    if first:
                        return trans.label_to_jump, self.return_type, p_revert, a
                    return trans.label_to_jump, self.return_type, p_revert+self.size, a
                error_msg = f'Instrucción {transfer_type.name} con retorno de valor no valido'
                global_config.log_semantic_error(error_msg, line, column)
                raise SemanticError(error_msg, line, column)

        # hit top
        if self.parent_environment is None:
            error_msg = f'Instrucción {transfer_type.name} colocada erróneamente'
            global_config.log_semantic_error(error_msg, line, column)
            raise SemanticError(error_msg, line, column)

        if first:
            return self.parent_environment.get_transfer_control_label(transfer_type, with_value, line, column,
                                                                      p_revert, first=False, a=a)

        return self.parent_environment.get_transfer_control_label(transfer_type, with_value,
                                                                  line, column, p_revert + self.size, first=False, a=a)

    def add_tmp_to_function(self, tmp):
        if self.is_function_env:
            self.associated_tmps.append(tmp)
            return
        # hit top
        if self.parent_environment is None:
            print("NO FUNCTION ENV FOUND, CHECK")
            input()
            return []
        self.parent_environment.add_tmp_to_function(tmp)

    def get_tmps_from_function(self) -> List[str]:
        return []  # TODO fixme
        if self.is_function_env:
            return self.associated_tmps
        # hit top
        if self.parent_environment is None:
            print("NO FUNCTION ENV FOUND, CHECK")
            input()
            return []
        return self.parent_environment.get_tmps_from_function()


    def remove_child(self, child):  # child: Environment
        self.children_environment = list(filter(lambda p: p is not child, self.children_environment))
