import secrets
from typing import List, Tuple

from element_types.c_expression_type import ExpressionType
from abstract.expression import Expression


from errors.lexic_error import LexicError
from errors.semantic_error import SemanticError
from errors.syntactic_error import SyntacticError
from expressions.array_expression import ArrayExpression

# from elements.value_tuple import ValueTuple
lexic_error_list: List[str] = []
syntactic_error_list: List[str] = []
semantic_error_list: List[str] = []
tmp_symbol_table = []

# t0 is reserved for the return value of functions
# t1 is reserved for program_exit_code
# t2 is reserved for func_has_returned
tmp_i = 3
label_i = 0


ALLOW_NESTED_VARIABLE_OVERRIDE = True
unique_counter = 0
console_output: str = ""
function_list: dict = {}  # func_name:str, func:func_decl
function_call_list: dict = {}

function_3ac_code = []


main_environment = None  # Type Environment. Due to circular import this is set in main

#


def array_type_to_dimension_dict_and_type(arr_type) -> Tuple[dict, ExpressionType]:

    from element_types.array_def_type import ArrayDefType
    from elements.c_env import Environment
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
    return ExpressionType.VOID, {}


def extract_dimensions_to_dict(arr) -> dict:
    if not isinstance(arr, list):  # Same deepness, so no array
        return {}
    r = {}
    i = 1
    layer = arr
    while True:
        from expressions.array_expression import ArrayExpression
        if isinstance(layer[0], ArrayExpression):
            if isinstance(layer[0].value, list):
                r[i] = len(layer)
                layer = layer[0].value
                i += 1
                continue
            r[i] = len(layer)
            break
        r[i] = len(layer)
        break
    return r


def match_dimensions(supposed: List, arr: List[Expression]) -> bool:
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

    from expressions.parameter_function_call import ParameterFunctionCallE
    if isinstance(arr[0], ParameterFunctionCallE):
        return True  # god forgive me

    for i in range(index):
        r: bool = match_dimensions(supposed[:], arr[i].value)
        if not r:
            # print(f'False:{i}th child returned False')
            return False

    # All children and self returned True
    return True


def match_array_type(supposed: ExpressionType, arr: List[Expression]) -> bool:

    if len(arr) == 0:
        return True

    # TODO does this break all of things? idk
    if not type(arr[0]) in [ArrayExpression]:
        for item in arr:
            if item.expression_type is not supposed and item.expression_type is not ExpressionType.VOID:  # god forgive me
                return False
        return True

    if not isinstance(arr[0].value, list):  # Reached last array
        for item in arr:
            if item.expression_type is not supposed:
                return False
        return True

    for i in range(len(arr)):
        r: bool = match_array_type(supposed, arr[i].value)
        if not r:
            return False

    # All children and self returned True
    return True


def flatten_array(arr: List[Expression]) -> List[Expression]:

    if len(arr) == 0: #TODO this breaks array? idk
        return []


    if not type(arr[0]) in [ArrayExpression]:
        return arr

    if not isinstance(arr[0].value, list):  # Reached last array
        return arr

    flat = []

    for i in range(len(arr)):
        flat = flat + flatten_array(arr[i].value)

    # All children flatenned
    return flat


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


def find_loop_break_type(instruction_set) -> ExpressionType:

    for instruction in instruction_set:
        a = type(instruction).__name__
        match a:
            case "BreakI":
                return instruction.expr.expression_type

            case "Conditional":
                for clause in instruction.clauses:
                    the_type = find_loop_break_type(clause.instructions)
                    if the_type is not None:
                        return the_type

            case "MatchI":
                for clause in instruction.clauses:
                    the_type = find_loop_break_type(clause.instructions)
                    if the_type is not None:
                        return the_type

    return None

def generate_symbol_table(instruction_set, env_name: str) -> List[List[str]]:
    table: List[List[str]] = []

    for instruction in instruction_set:
        match type(instruction).__name__:
            case "Declaration":
                if instruction.expression_type is not None:
                    table.append([instruction.variable_id, "Variable", instruction.expression_type.name, env_name,
                                  str(instruction.line), str(instruction.column)])
                else:
                    table.append([instruction.variable_id, "Variable", "-", env_name,
                                  str(instruction.line), str(instruction.column)])


            case "ArrayDeclaration":
                if instruction.var_type is not None:

                    table.append([instruction.variable_id, "Variable[]", instruction.var_type.name, env_name,
                                  str(instruction.line), str(instruction.column)])
                else:
                    table.append([instruction.variable_id, "Variable[]", "-", env_name,
                                  str(instruction.line), str(instruction.column)])

            case "VectorDeclaration":
                table.append([instruction.variable_id, "Variable Vec<>", instruction.var_type.name, env_name,
                              str(instruction.line), str(instruction.column)])

            case "FunctionDeclaration":
                table.append([instruction.function_id, "Function Declaration", instruction.return_type.name, env_name,
                              str(instruction.line), str(instruction.column)])
                function_table = generate_symbol_table(instruction.instructions, env_name + "->" + instruction.function_id)
                table = table + function_table

            case "Conditional":
                conditional_id = random_hex_color_code()
                for clause in instruction.clauses:
                    random_id = random_hex_color_code()
                    conditional_table = generate_symbol_table(clause.instructions,
                                                              env_name + "->" + "Conditional" + conditional_id+random_id)
                    table = table + conditional_table

            case "MatchI":
                conditional_id = random_hex_color_code()
                for clause in instruction.clauses:
                    random_id = random_hex_color_code()
                    conditional_table = generate_symbol_table(clause.instructions,
                                                              env_name + "->" + "Match" + conditional_id + random_id)
                    table = table + conditional_table

            case "WhileI":
                while_id = random_hex_color_code()
                while_table = generate_symbol_table(instruction.instructions, env_name + "->" + "While"+while_id)
                table = table + while_table

            case "LoopI":
                loop_id = random_hex_color_code()
                loop_table = generate_symbol_table(instruction.instructions, env_name + "->" + "Loop" + loop_id)
                table = table + loop_table

            case "ForInI":
                for_id = random_hex_color_code()
                table.append([instruction.looper, "Variable", "-", env_name + "->" + "->For" + for_id,
                              str(instruction.line), str(instruction.column)])
                for_table = generate_symbol_table(instruction.instructions, env_name + "->" + "For" + for_id)
                table = table + for_table

    return table