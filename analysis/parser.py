import global_config
import ply.yacc as yacc
import analysis.lexer as lexer

from errors.syntactic_error import SyntacticError

from element_types.c_expression_type import ExpressionType
from elements.condition_clause import ConditionClause
from elements.condition_expression_clause import ConditionExpressionClause
from elements.match_clause import MatchClause
from elements.match_expression_clause import MatchExpressionClause
from elements.c_env import Environment
from elements.id_tuple import IDTuple
from element_types.array_def_type import ArrayDefType

# ################################INSTRUCTIONS#########################################
from instructions.declaration import Declaration
from instructions.assignment import Assigment

from instructions.array_declaration import ArrayDeclaration
from instructions.array_assignment import ArrayAssignment

from instructions.function_declaration import FunctionDeclaration
# ################################EXPRESSIONS#########################################
from element_types.arithmetic_type import ArithmeticType
from element_types.logic_type import LogicType
from expressions.literal import Literal
from expressions.arithmetic import Arithmetic
from expressions.logic import Logic
from expressions.array_expression import ArrayExpression


tokens = lexer.tokens


start = 'marian'

# start = 'array_type'

precedence = (
    # TODO uncomment respectively
    ('left', 'LOGIC_OR'),
    ('left', 'LOGIC_AND'),
    # needs parenthesis according to rust
    ('nonassoc', 'OPE_EQUAL', 'OPE_NEQUAL', 'OPE_LESS', 'OPE_MORE', 'OPE_LESS_EQUAL', 'OPE_MORE_EQUAL'),
    ('left', 'SUB', 'SUM'),
    ('left', 'MULT', 'DIV', 'MOD'),
    # ('left', 'AS'),
    ('nonassoc', 'UMINUS', "LOGIC_NOT"),  # nonassoc according to rust, i think 'right'
    # ('nonassoc', 'PREC_VAR_REF'),
    # ('nonassoc', 'DOT'),
    # ('nonassoc', 'PREC_FUNC_CALL'),
    # ('nonassoc', 'PREC_METHOD_CALL'),
    # ('nonassoc', 'PREC_ARRAY_REF')

)


def p_marian(p):  # M&B ♥
    """marian : instructions"""
    p[0] = p[1]


def p_instructions_rec(p):
    """instructions : instructions instruction"""
    p[0] = p[1] + [p[2]]


def p_instructions(p):
    """instructions : instruction"""
    p[0] = [p[1]]


def p_instruction(p):  # since all here are p[0] = p[1] (except void_inst) add all productions here
    """
    instruction : var_declaration SEMICOLON
    | var_assignment SEMICOLON
    | array_declaration SEMICOLON
    | function_declaration
    | array_assignment SEMICOLON
    """
    p[0] = p[1]


# ###########################################SIMPLE VARIABLE DECLARATION ###############################################
def p_var_declaration_1(p):
    """var_declaration : LET MUTABLE ID COLON variable_type EQUAL expression"""
    p[0] = Declaration(p[3], p[5], p[7], True, p.lineno(1), -1)


def p_var_declaration_2(p):
    """var_declaration : LET MUTABLE ID EQUAL expression"""
    p[0] = Declaration(p[3], None, p[5], True, p.lineno(1), -1)


def p_var_declaration_3(p):
    """var_declaration : LET ID COLON variable_type EQUAL expression"""
    p[0] = Declaration(p[2], p[4], p[6], False, p.lineno(1), -1)


def p_var_declaration_4(p):
    """var_declaration : LET ID EQUAL expression"""
    p[0] = Declaration(p[2], None, p[4], False, p.lineno(1), -1)


# ################################################Variable Assignment###################################################
def p_var_assignment(p):
    """var_assignment : ID EQUAL expression"""
    p[0] = Assigment(p[1], p[3], p.lineno(1), -1)


# ###########################################ARRAY VARIABLE DECLARATION ###############################################
def p_array_declaration_1(p):
    """array_declaration : LET MUTABLE ID COLON array_type EQUAL expression"""
    p[0] = ArrayDeclaration(p[3], p[5], p[7], True, p.lineno(1), -1)
    # print("p_array_declaration_1")


def p_array_declaration_2(p):
    """array_declaration : LET MUTABLE ID COLON array_type"""
    p[0] = ArrayDeclaration(p[3], p[5], None, True, p.lineno(1), -1)


def p_array_declaration_3(p):
    """array_declaration : LET ID COLON array_type EQUAL expression"""
    p[0] = ArrayDeclaration(p[2], p[4], p[6], False, p.lineno(1), -1)


def p_array_declaration_4(p):
    """array_declaration : LET ID COLON array_type"""
    p[0] = ArrayDeclaration(p[2], p[4], None, False, p.lineno(1), -1)


########################################
def p_array_type_r(p):
    """array_type : BRACKET_O array_type SEMICOLON expression BRACKET_C"""
    p[0] = ArrayDefType(True, p[2], p[4])
    # print("p_array_type_r")


def p_array_type(p):
    """array_type : BRACKET_O variable_type SEMICOLON expression BRACKET_C"""
    p[0] = ArrayDefType(False, p[2], p[4])
    # print("p_array_type")


########################################

def p_array_expression_list(p):
    """array_expression : BRACKET_O expression_list BRACKET_C"""
    p[0] = ArrayExpression(p[2], False, None, p.lineno(1), -1)
    # print("p_array_expression_list")


def p_array_expression_expansion(p):
    """array_expression : BRACKET_O expression SEMICOLON expression BRACKET_C"""
    p[0] = ArrayExpression(p[2], True, p[4], p.lineno(1), -1)
    # print("p_array_expression_expansion")


def p_expression_list_r(p):
    """expression_list : expression_list COMMA expression
    | expression_list COMMA array_expression"""
    p[1].append(p[3])
    p[0] = p[1]
    # print("p_expression_list_r")


def p_expression_list(p):
    """expression_list : expression
    | array_expression"""
    p[0] = [p[1]]
    # print("p_expression_list")


# ###################################################ARRAY ASSIGNMENT###################################################
def p_total_array_assignment(p):
    """array_assignment : ID EQUAL expression
    | ID EQUAL array_expression"""
    p[0] = ArrayAssignment(p[1], [], p[3], p.lineno(1), -1)


def p_array_assignment(p):
    """array_assignment : ID array_indexes EQUAL expression
    | ID array_indexes EQUAL array_expression"""
    p[0] = ArrayAssignment(p[1], p[2], p[4], p.lineno(1), -1)


def p_array_indexes_r(p):
    """array_indexes : array_indexes BRACKET_O expression BRACKET_C"""
    p[1].append(p[3])
    p[0] = p[1]


def p_array_indexes(p):
    """array_indexes : BRACKET_O expression BRACKET_C"""
    p[0] = [p[2]]


# ###############################################FUNCTION DECLARATION###################################################
def p_function_declaration_1(p):
    """function_declaration : FN ID PARENTH_O func_decl_args PARENTH_C KEY_O instructions KEY_C"""
    p[0] = FunctionDeclaration(p[2], p[4], ExpressionType.VOID, p[7], p.lineno(1), -1)


def p_function_declaration_2(p):
    """function_declaration : FN ID PARENTH_O func_decl_args PARENTH_C SUB OPE_MORE variable_type KEY_O instructions KEY_C"""
    p[0] = FunctionDeclaration(p[2], p[4], p[8], p[10], p.lineno(1), -1)


def p_func_decl_args_r(p):
    """func_decl_args : func_decl_args COMMA func_var"""
    p[0] = p[1] + [p[3]]


def p_func_decl_args(p):
    """func_decl_args : func_var"""
    p[0] = [p[1]]


def p_func_decl_args_epsilon(p):
    """func_decl_args : epsilon"""
    p[0] = []


def p_func_var_1(p):
    """func_var : ID COLON variable_type"""
    p[0] = IDTuple(p[1], p[3], False, False, {}, None)


def p_func_var_2(p):
    """func_var : ID COLON MUTABLE variable_type"""
    p[0] = IDTuple(p[1], p[4], True, False, {}, None)


# def p_func_var_3(p):  # Should only be used in arrays (and vectors??)
#     """func_var : ID COLON AMPERSAND func_decl_array_var_type"""
#     p[0] = IDTuple(p[1], p[4][0], False, True, p[4][1], None)


# def p_func_var_4(p):
#     """func_var : ID COLON AMPERSAND vector_type"""
#     tmp = p[4]
#     i = 1
#     while (tmp.is_nested_vector):
#         i += 1
#         tmp = tmp.content_type
#     p[0] = IDTuple(p[1], ExpressionType.VECTOR, False, True, i, tmp.content_type)

#
# def p_func_var_5(p):
#     """func_var : ID COLON AMPERSAND MUTABLE vector_type"""
#     tmp = p[5]
#     i = 1
#     while (tmp.is_nested_vector):
#         i += 1
#         tmp = tmp.content_type
#     p[0] = IDTuple(p[1], ExpressionType.VECTOR, True, True, i, tmp.content_type)


# def p_func_var_6(p):  # Should only be used in arrays (and vectors??)
#     """func_var : ID COLON AMPERSAND MUTABLE func_decl_array_var_type"""
#
#     p[0] = IDTuple(p[1], p[5]["embedded_type"], True, True, p[5], None)
#
#
# def p_func_var_7(p):  # Should only be used in arrays
#     """func_var : ID COLON AMPERSAND array_type"""
#
#     dic, _type = global_config.array_type_to_dimension_dict_and_type(p[4])
#     p[0] = IDTuple(p[1], _type, False, True, dic, None)
#
#
# def p_func_var_8(p):  # Should only be used in arrays
#     """func_var : ID COLON AMPERSAND MUTABLE array_type"""
#
#     dic, _type = global_config.array_type_to_dimension_dict_and_type(p[5])
#     p[0] = IDTuple(p[1], _type, True, True, dic, None)


# ##################################################Variable Types######################################################


def p_variable_type_i64(p):
    """variable_type : TYPE_I64"""
    p[0] = ExpressionType.INT


def p_variable_type_usize(p):
    """variable_type : TYPE_USIZE"""
    p[0] = ExpressionType.USIZE


def p_variable_type_f64(p):
    """variable_type : TYPE_F64"""
    p[0] = ExpressionType.FLOAT


def p_variable_type_bool(p):
    """variable_type : TYPE_BOOL"""
    p[0] = ExpressionType.BOOL


def p_variable_type_char(p):
    """variable_type : TYPE_CHAR"""
    p[0] = ExpressionType.CHAR


def p_variable_type_amper_str(p):
    """variable_type : AMPERSAND TYPE_AMPER_STR"""
    p[0] = ExpressionType.STRING_PRIMITIVE


def p_variable_type_string(p):
    """variable_type : TYPE_STRING"""
    p[0] = ExpressionType.STRING_CLASS
#######################################################################################################################


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


# Will this break the parser?
def p_expression_array_expression(p):
    """expression : array_expression"""
    p[0] = p[1]


#######################################################################################################################
def p_expression_integer(p):
    """expression : INTEGER"""
    p[0] = Literal(p[1], ExpressionType.INT, p.lineno(1), -1)


def p_expression_float(p):
    """expression : FLOAT"""
    p[0] = Literal(p[1], ExpressionType.FLOAT, p.lineno(1), -1)


def p_expression_string(p):
    """expression : STRING_TEXT"""
    p[0] = Literal(p[1], ExpressionType.STRING_PRIMITIVE, p.lineno(1), -1)


def p_expression_char(p):
    """expression : CHAR"""
    p[0] = Literal(p[1], ExpressionType.CHAR, p.lineno(1), -1)


def p_expression_true(p):
    """expression : BOOL_TRUE"""
    p[0] = Literal(1, ExpressionType.BOOL, p.lineno(1), -1)


def p_expression_false(p):
    """expression : BOOL_FALSE"""
    p[0] = Literal(0, ExpressionType.BOOL, p.lineno(1), -1)


def p_expression_plus(p):
    """expression : expression SUM expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.SUM, p[1].expression_type, p.lineno(2), -1)


def p_expression_minus(p):
    """expression : expression SUB expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.SUB, p[1].expression_type, p.lineno(2), -1)


def p_expression_mult(p):
    """expression : expression MULT expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.MULT, p[1].expression_type, p.lineno(2), -1)


def p_expression_div(p):
    """expression : expression DIV expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.DIV, ExpressionType.FLOAT, p.lineno(2), -1)


def p_expression_pow_int(p):
    """expression : TYPE_I64 COLON COLON POW PARENTH_O expression COMMA expression PARENTH_C"""
    p[0] = Arithmetic(p[6], p[8], ArithmeticType.POW_INT, ExpressionType.INT, p.lineno(2), -1)


def p_expression_pow_float(p):
    """expression : TYPE_F64 COLON COLON POWF PARENTH_O expression COMMA expression PARENTH_C"""
    p[0] = Arithmetic(p[6], p[8], ArithmeticType.POW_FLOAT, ExpressionType.FLOAT, p.lineno(2), -1)


def p_expression_mod(p):
    """expression : expression MOD expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.MOD, ExpressionType.INT, p.lineno(2), -1)


def p_expression_uminus(p):
    """expression : SUB expression %prec UMINUS"""
    p[0] = Arithmetic(p[2], p[2], ArithmeticType.NEG, p[2].expression_type, p.lineno(1), -1)


def p_expression_parenthesis(p):
    """expression : PARENTH_O expression PARENTH_C"""
    p[0] = p[2]


# RELATIONAL

def p_expression_ope_equal(p):
    """expression : expression OPE_EQUAL expression"""
    p[0] = Logic(p[1], p[3], LogicType.OPE_EQUAL, p.lineno(2), -1)


def p_expression_ope_nequal(p):
    """expression : expression OPE_NEQUAL expression"""
    p[0] = Logic(p[1], p[3], LogicType.OPE_NEQUAL, p.lineno(2), -1)


def p_expression_ope_less(p):
    """expression : expression OPE_LESS expression"""
    p[0] = Logic(p[1], p[3], LogicType.OPE_LESS, p.lineno(2), -1)


def p_expression_ope_less_equal(p):
    """expression : expression OPE_LESS_EQUAL expression"""
    p[0] = Logic(p[1], p[3], LogicType.OPE_LESS_EQUAL, p.lineno(2), -1)


def p_expression_ope_more(p):
    """expression : expression OPE_MORE expression"""
    p[0] = Logic(p[1], p[3], LogicType.OPE_MORE, p.lineno(2), -1)


def p_expression_ope_more_equal(p):
    """expression : expression OPE_MORE_EQUAL expression"""
    p[0] = Logic(p[1], p[3], LogicType.OPE_MORE_EQUAL, p.lineno(2), -1)


# LOGICAL
def p_expression_logic_or(p):
    """expression : expression LOGIC_OR expression"""
    p[0] = Logic(p[1], p[3], LogicType.LOGIC_OR, p.lineno(2), -1)


def p_expression_logic_and(p):
    """expression : expression LOGIC_AND expression"""
    p[0] = Logic(p[1], p[3], LogicType.LOGIC_AND, p.lineno(2), -1)


def p_expression_logic_not(p):
    """expression : LOGIC_NOT expression"""
    p[0] = Logic(p[2], p[2], LogicType.LOGIC_NOT, p.lineno(1), -1)


def p_epsilon(p):
    """epsilon :"""
    pass


def p_error(p):
    reason = f'Token <{p.value}> inesperado'
    global_config.log_syntactic_error(reason, p.lineno, -1)

    print(f"next token is {parser.token()}")
    print(f"2nd next token is {parser.token()}")

    raise SyntacticError(reason, p.lineno, -1)


parser = yacc.yacc()  # los increíbles

#
#                                        (                          )
#                                         \                        /
#                                        ,' ,__,___,__,-._         )
#                                        )-' ,    ,  , , (        /
#                                        ;'"-^-.,-''"""\' \       )
#                                       (      (        ) /  __  /
#                                        \o,----.  o  _,'( ,.^. \
#                                        ,'`.__  `---'    `\ \ \ \_
#                                 ,.,. ,'                   \    ' )
#                                 \ \ \\__  ,------------.  /     /
# UN COMPILADOR NO TERMINADO     ( \ \ \( `---.-`-^--,-,--\:     :
#                                 \       (   (""""""`----'|     :
#                                  \   `.  \   `.          |      \
#                                   \   ;  ;     )      __ _\      \
#                                   /     /    ,-.,-.'"Y  Y  \      `.
#                                  /     :    ,`-'`-'`-'`-'`-'\       `.
#                                 /      ;  ,'  /              \        `
#                                /      / ,'   /                \
