import secrets
from typing import List, Tuple

from element_types.element_type import ElementType

from errors.lexic_error import LexicError
from errors.semantic_error import SemanticError
from errors.syntactic_error import SyntacticError

from elements.value_tuple import ValueTuple
lexic_error_list: List[LexicError] = []
syntactic_error_list: List[SyntacticError] = []
semantic_error_list: List[SemanticError] = []

tmp_symbol_table = []


ALLOW_NESTED_VARIABLE_OVERRIDE = True
unique_counter = 0
console_output: str = ""
function_list: dict = {}  # func_name:str, func:func_decl

main_environment = None  # Type Environment. Due to circular import this is set in main

def generate_symbol_table(instruction_set, env_name: str) -> List[List[str]]:
    table: List[List[str]] = []

    for instruction in instruction_set:
        match type(instruction).__name__:
            case "Declaration":
                if instruction._type is not None:
                    table.append([instruction._id, "Variable", instruction._type.name, env_name,
                                  str(instruction.line), str(instruction.column)])
                else:
                    table.append([instruction._id, "Variable", "-", env_name,
                                  str(instruction.line), str(instruction.column)])


            case "ArrayDeclaration":
                if instruction.var_type is not None:

                    table.append([instruction._id, "Variable[]", instruction.var_type.name, env_name,
                                  str(instruction.line), str(instruction.column)])
                else:
                    table.append([instruction._id, "Variable[]", "-", env_name,
                                  str(instruction.line), str(instruction.column)])

            case "VectorDeclaration":
                table.append([instruction._id, "Variable Vec<>", instruction.var_type.name, env_name,
                              str(instruction.line), str(instruction.column)])

            case "FunctionDeclaration":
                table.append([instruction._id, "Function Declaration", instruction.return_type.name, env_name,
                              str(instruction.line), str(instruction.column)])
                function_table = generate_symbol_table(instruction.instructions, env_name + "->" + instruction._id)
                table = table + function_table

            case "Conditional":
                conditional_id = random_hex_color_code()
                for clause in instruction.clauses:
                    random_id = random_hex_color_code()
                    conditional_table = generate_symbol_table(clause.instructions,
                                                              env_name+"Conditional"+conditional_id+":"+random_id)
                    table = table + conditional_table

            case "MatchI":
                conditional_id = random_hex_color_code()
                for clause in instruction.clauses:
                    random_id = random_hex_color_code()
                    conditional_table = generate_symbol_table(clause.instructions,
                                                              env_name + "Match" + conditional_id + ":" + random_id)
                    table = table + conditional_table

            case "WhileI":
                while_id = random_hex_color_code()
                while_table = generate_symbol_table(instruction.instructions, env_name + "While"+while_id)
                table = table + while_table

            case "LoopI":
                loop_id = random_hex_color_code()
                loop_table = generate_symbol_table(instruction.instructions, env_name + "While" + loop_id)
                table = table + loop_table

            case "ForInI":
                for_id = random_hex_color_code()
                table.append([instruction.looper, "Variable", "-", env_name + "->For" + for_id,
                              str(instruction.line), str(instruction.column)])
                for_table = generate_symbol_table(instruction.instructions, env_name + "While" + for_id)
                table = table + for_table


    return table












def is_arithmetic_pure_literals(expr) -> bool:

    from expressions.literal import Literal
    from expressions.arithmetic import Arithmetic
    from expressions.type_casting import TypeCasting
    if isinstance(expr, Literal):
        return True

    if isinstance(expr, Arithmetic):
        return is_arithmetic_pure_literals(expr.left) and is_arithmetic_pure_literals(expr.right)

    if isinstance(expr, TypeCasting):
        return is_arithmetic_pure_literals(expr.expr)

    # Every other thing already has embedded type and cannot be taken into place
    # in for example (and the reason this is implemented) to allow usize arithmetic with literals

    return False


def array_type_to_dimension_dict_and_type(arr_type) -> Tuple[dict, ElementType]:

    from element_types.array_def_type import ArrayDefType
    from elements.env import Environment
    dic = {}
    i = 1
    tmp: ArrayDefType = arr_type

    while True:
        if isinstance(tmp.content_type, ArrayDefType):
            # FIXME Because of env, should happened at runtime? It's safe cause always literal?
            dic[i] = tmp.size_expr.execute(Environment(None)).value
            i += 1
            tmp = tmp.content_type
            continue

        dic[i] = tmp.size_expr.execute(Environment(None)).value

        dic["embedded_type"] = tmp.content_type  # For backwards compatibility
        return dic, tmp.content_type

    # print("aqui la wea")
    # print(arr_type)
    return ElementType.VOID, {}


def match_deepness(supposed: int, arr: List[ValueTuple]):

    i = 0
    tmp = arr
    while True:

        if not isinstance(tmp, list):
            return i == supposed
        tmp = tmp[0].value
        i += 1


def match_pure_vector_deepness(supposed: int, vec) -> bool:
    if not isinstance(vec, list):  # Reached end of vec
        if supposed != 0:  # But chain is not completed
            # print("False: end of array but not chain")
            return False
        # print("True: end of array and chain")
        return True

    else:  # Array is still nested

        if supposed == 0:  # But chain is empty
            # print("False:end of chain but not array")
            return False
        # dont you dare return true :P Keep checking more nested levels

    for i in range(len(vec)):
        r: bool = match_vector_deepness(supposed-1, vec[i])
        if not r:
            # print(f'False:{i}th child returned False')
            return False

    # All children and self returned True
    return True


def match_vector_deepness(supposed: int, vec: List[ValueTuple]) -> bool:
    if not isinstance(vec, list):  # Reached end of vec
        if supposed != 0:  # But chain is not completed
            # print("False: end of array but not chain")
            return False
        # print("True: end of array and chain")
        return True

    else:  # Array is still nested

        if supposed == 0:  # But chain is empty
            # print("False:end of chain but not array")
            return False
        # dont you dare return true :P Keep checking more nested levels

    for i in range(len(vec)):
        r: bool = match_vector_deepness(supposed-1, vec[i].value)
        if not r:
            # print(f'False:{i}th child returned False')
            return False

    # All children and self returned True
    return True


def match_dimensions(supposed: List, arr: List[ValueTuple]) -> bool:
    if not isinstance(arr, list):  # Reached end of array
        if len(supposed) != 0:  # But chain is not completed
            # print("False: end of array but not chain")
            return False
        # print("True: end of array and chain")
        return True

    else:  # Array is still nested

        if len(supposed) == 0:  # But chain is empty
            # print("False:end of chain but not array")
            return False
        # dont you dare return true :P Keep checking more nested levels

    if len(arr) is not supposed[0]:
        # print(f'False: supposed-array mismatch: {len(arr)}->{supposed[0]}')
        return False

    index = supposed.pop(0)

    for i in range(index):
        r: bool = match_dimensions(supposed[:], arr[i].value)
        if not r:
            # print(f'False:{i}th child returned False')
            return False

    # All children and self returned True
    return True


def match_array_type(supposed: ElementType, arr: List[ValueTuple]) -> bool:

    if len(arr) == 0: #TODO this breaks array? idk
        return True

    if not isinstance(arr[0].value, list):  # Reached last array
        for item in arr:
            if item._type is not supposed:
                return False
        return True

    for i in range(len(arr)):
        r: bool = match_array_type(supposed, arr[i].value)
        if not r:
            return False

    # All children and self returned True
    return True


def get_vector_deepness(vec) -> int:
    i = 0
    tmp = vec

    while isinstance(tmp, list):
        i += 1
        tmp = tmp[0].value

    return i


def extract_dimensions_to_dict(arr) -> dict:
    if not isinstance(arr, list):  # Same deepness, so no array
        return {}

    r = {}
    i = 1

    layer = arr
    while True:

        if isinstance(layer[0], list):
            r[i] = len(layer)
            layer = layer[0]
            i += 1
            continue

        r[i] = len(layer)
        break

    return r



def value_tuple_vector_to_array(arr) -> list:

    r = []
    element: ValueTuple
    for element in arr:
        if isinstance(element.value, list):
            r.append(value_tuple_array_to_array(element.value))
            continue
        r.append(element.value)

    return r


def value_tuple_array_to_array(arr) -> list:

    r = []
    element: ValueTuple
    for element in arr:
        if isinstance(element.value, list):
            r.append(value_tuple_array_to_array(element.value))
            continue
        r.append(element.value)

    return r


def log_to_console(txt: str):
    global console_output
    console_output += txt


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
