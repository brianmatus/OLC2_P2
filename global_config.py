import secrets
from typing import List, Tuple

from element_types.c_expression_type import ExpressionType

from errors.lexic_error import LexicError
from errors.semantic_error import SemanticError
from errors.syntactic_error import SyntacticError

# from elements.value_tuple import ValueTuple
lexic_error_list: List[LexicError] = []
syntactic_error_list: List[SyntacticError] = []
semantic_error_list: List[SemanticError] = []
tmp_symbol_table = []
tmp_i = 0
label_i = 0


ALLOW_NESTED_VARIABLE_OVERRIDE = True
unique_counter = 0
console_output: str = ""
function_list: dict = {}  # func_name:str, func:func_decl

main_environment = None  # Type Environment. Due to circular import this is set in main

# def generate_symbol_table(instruction_set, env_name: str) -> List[List[str]]:
#     table: List[List[str]] = []
#
#     for instruction in instruction_set:
#         match type(instruction).__name__:
#             case "Declaration":
#                 if instruction.expression_type is not None:
#                     table.append([instruction.variable_id, "Variable", instruction.expression_type.name, env_name,
#                                   str(instruction.line), str(instruction.column)])
#                 else:
#                     table.append([instruction.variable_id, "Variable", "-", env_name,
#                                   str(instruction.line), str(instruction.column)])
#
#
#             case "ArrayDeclaration":
#                 if instruction.var_type is not None:
#
#                     table.append([instruction.variable_id, "Variable[]", instruction.var_type.name, env_name,
#                                   str(instruction.line), str(instruction.column)])
#                 else:
#                     table.append([instruction.variable_id, "Variable[]", "-", env_name,
#                                   str(instruction.line), str(instruction.column)])
#
#             case "VectorDeclaration":
#                 table.append([instruction.variable_id, "Variable Vec<>", instruction.var_type.name, env_name,
#                               str(instruction.line), str(instruction.column)])
#
#             case "FunctionDeclaration":
#                 table.append([instruction.variable_id, "Function Declaration", instruction.return_type.name, env_name,
#                               str(instruction.line), str(instruction.column)])
#                 function_table = generate_symbol_table(instruction.instructions, env_name + "->" + instruction.variable_id)
#                 table = table + function_table
#
#             case "Conditional":
#                 conditional_id = random_hex_color_code()
#                 for clause in instruction.clauses:
#                     random_id = random_hex_color_code()
#                     conditional_table = generate_symbol_table(clause.instructions,
#                                                               env_name+"Conditional"+conditional_id+":"+random_id)
#                     table = table + conditional_table
#
#             case "MatchI":
#                 conditional_id = random_hex_color_code()
#                 for clause in instruction.clauses:
#                     random_id = random_hex_color_code()
#                     conditional_table = generate_symbol_table(clause.instructions,
#                                                               env_name + "Match" + conditional_id + ":" + random_id)
#                     table = table + conditional_table
#
#             case "WhileI":
#                 while_id = random_hex_color_code()
#                 while_table = generate_symbol_table(instruction.instructions, env_name + "While"+while_id)
#                 table = table + while_table
#
#             case "LoopI":
#                 loop_id = random_hex_color_code()
#                 loop_table = generate_symbol_table(instruction.instructions, env_name + "While" + loop_id)
#                 table = table + loop_table
#
#             case "ForInI":
#                 for_id = random_hex_color_code()
#                 table.append([instruction.looper, "Variable", "-", env_name + "->For" + for_id,
#                               str(instruction.line), str(instruction.column)])
#                 for_table = generate_symbol_table(instruction.instructions, env_name + "While" + for_id)
#                 table = table + for_table
#
#
#     return table












def is_arithmetic_pure_literals(expr) -> bool:

    from expressions.literal import Literal
    from expressions.arithmetic import Arithmetic
    # from expressions.type_casting import TypeCasting
    if isinstance(expr, Literal):
        return True

    if isinstance(expr, Arithmetic):
        return is_arithmetic_pure_literals(expr.left) and is_arithmetic_pure_literals(expr.right)

    # if isinstance(expr, TypeCasting):
    #     return is_arithmetic_pure_literals(expr.expr)

    # Every other thing already has embedded type and cannot be taken into place
    # in for example (and the reason this is implemented) to allow usize arithmetic with literals

    return False


def log_lexic_error(foreign: str, row: int, column: int):
    global console_output
    lexic_error_list.append(str(LexicError(f'Signo <{foreign}> no reconocido', row, column)))
    print(f'Logged Lexic Error:{row}-{column} -> Signo <{foreign}> no reconocido')
    console_output += f'[row:{row},column:{column}]Error Lexico: <{foreign} no reconocido\n'


def log_syntactic_error(reason: str, row: int, column: int):
    global console_output
    syntactic_error_list.append(str(SyntacticError(reason, row, column)))
    print(f'Logged Syntactic Error:{row}-{column} -> {reason}')
    console_output += f'[row:{row},column:{column}]Error Sintáctico:{reason} \n'


def log_semantic_error(reason: str, row: int, column: int):
    global console_output
    semantic_error_list.append(str(SemanticError(reason, row, column)))
    print(f'Logged Semantic Error:{row}-{column} -> {reason}')
    console_output += f'[row:{row},column:{column}]Error Semántico:{reason}\n'


def get_unique_number() -> int:
    global unique_counter
    unique_counter += 1
    return unique_counter


def random_hex_color_code() -> str:
    return "#" + secrets.token_hex(2)
