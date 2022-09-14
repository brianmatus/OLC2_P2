import global_config
import ply.yacc as yacc
import analysis.lexer as lexer

from errors.syntactic_error import SyntacticError

from element_types.element_type import ElementType
from elements.condition_clause import ConditionClause
from elements.condition_expression_clause import ConditionExpressionClause
from elements.match_clause import MatchClause
from elements.match_expression_clause import MatchExpressionClause
from elements.env import Environment
from element_types.func_call_arg import FuncCallArg
from elements.id_tuple import IDTuple
from instructions.for_in_i import ForInRanged
from element_types.vector_def_type import VectorDefType

# ################################INSTRUCTIONS#########################################
from element_types.array_def_type import ArrayDefType
from instructions.declaration import Declaration
from instructions.array_declaration import ArrayDeclaration
from instructions.print_ln import PrintLN
from instructions.assignment import Assigment
from instructions.array_assignment import ArrayAssignment
from instructions.conditional import Conditional
from instructions.conditional_match import MatchI
from instructions.function_declaration import FunctionDeclaration
from instructions.function_call import FunctionCallI
from instructions.while_i import WhileI
from instructions.loop_i import LoopI
from instructions.return_i import ReturnI
from instructions.continue_i import ContinueI
from instructions.break_i import BreakI
from instructions.for_in_i import ForInI
from instructions.vector_declaration import VectorDeclaration
from instructions.expression_as_instruction import ExpressionAsInstruction
# ################################EXPRESSIONS#########################################
from element_types.arithmetic_type import ArithmeticType
from element_types.logic_type import LogicType
from expressions.literal import Literal
from expressions.arithmetic import Arithmetic
from expressions.logic import Logic
from expressions.variable_ref import VariableReference
from expressions.array_reference import ArrayReference
from expressions.array_expression import ArrayExpression
from expressions.conditional_expression import ConditionalExpression
from expressions.conditional_match_expression import MatchExpression
from expressions.function_call_expression import FunctionCallE
from expressions.type_casting import TypeCasting
from expressions.parameter_function_call import ParameterFunctionCallE
from expressions.loop_e import LoopE

from expressions.vector import VectorExpression

tokens = lexer.tokens


start = 'marian'

# start = 'array_type'

precedence = (

    ('left', 'LOGIC_OR'),
    ('left', 'LOGIC_AND'),
    # needs parenthesis according to rust
    ('nonassoc', 'OPE_EQUAL', 'OPE_NEQUAL', 'OPE_LESS', 'OPE_MORE', 'OPE_LESS_EQUAL', 'OPE_MORE_EQUAL'),
    ('left', 'SUB', 'SUM'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('left', 'AS'),
    ('nonassoc', 'UMINUS', "LOGIC_NOT"),  # nonassoc according to rust, i think 'right'
    ('nonassoc', 'PREC_VAR_REF'),
    ('nonassoc', 'DOT'),
    ('nonassoc', 'PREC_FUNC_CALL'),
    ('nonassoc', 'PREC_METHOD_CALL'),
    ('nonassoc', 'PREC_ARRAY_REF')

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
    | array_declaration SEMICOLON
    | println_inst SEMICOLON
    | var_assignment SEMICOLON
    | array_assignment SEMICOLON
    | if_else_elseif
    | match_statement
    | function_declaration
    | function_call_i SEMICOLON
    | return_i SEMICOLON
    | continue_i SEMICOLON
    | break_i SEMICOLON
    | while_i
    | loop_i
    | for_in_i
    | vector_declaration SEMICOLON
    """
    p[0] = p[1]


def p_expr_as_inst(p):
    """instruction : expression SEMICOLON"""
    if isinstance(p[1], ParameterFunctionCallE):
        p[0] = ExpressionAsInstruction(p[1], p.lineno(2), -1)
        return
    reason = f'Expression-as-instruction inesperada.'
    global_config.log_syntactic_error(reason, p.lineno, -1)

    print(f"next token is {parser.token()}")
    print(f"2nd next token is {parser.token()}")
    raise SyntacticError(reason, p.lineno, -1)



def p_no_semicolon_instruction(p):  # TODO all added to p_instruction should be added here
    """
    no_semicolon_instruction : var_declaration
    | array_declaration
    | println_inst
    | var_assignment
    | array_assignment
    | if_else_elseif
    | match_statement
    | function_declaration
    | function_call_i
    | return_i
    | continue_i
    | break_i
    | while_i
    | loop_i
    | for_in_i
    | vector_declaration
    """
    p[0] = p[1]


# ###########################################VECTOR VARIABLE DECLARATION ###############################################
def p_vec_declaration_1(p):
    """vector_declaration : LET MUTABLE ID COLON vector_type EQUAL expression"""
    p[0] = VectorDeclaration(p[3], p[5], p[7], True, p.lineno(1), -1)


def p_vec_declaration_2(p):
    """vector_declaration : LET ID COLON vector_type EQUAL expression"""
    p[0] = VectorDeclaration(p[2], p[4], p[6], False, p.lineno(1), -1)


def p_vector_type_r(p):
    """vector_type : TYPE_VEC OPE_LESS vector_type OPE_MORE"""
    p[0] = VectorDefType(True, p[3])


def p_vector_type(p):
    """vector_type : TYPE_VEC OPE_LESS variable_type OPE_MORE"""
    p[0] = VectorDefType(False, p[3])


def p_vector_expr_1(p):
    """expression : VEC LOGIC_NOT array_expression"""
    p[0] = VectorExpression(p[3], None, p.lineno(1), -1)


def p_vector_expr_2(p):
    """expression : TYPE_VEC COLON COLON NEW PARENTH_O PARENTH_C"""
    p[0] = VectorExpression(None, None, p.lineno(1), -1)


def p_vector_expr_3(p):
    """expression : TYPE_VEC COLON COLON WITH_CAPACITY PARENTH_O expression PARENTH_C"""
    p[0] = VectorExpression(None, p[6], p.lineno(1), -1)


# ###############################################LOOP STATEMENT#########################################################
def p_for_in_i_1(p):
    """for_in_i : FOR ID IN expression KEY_O instructions KEY_C"""
    p[0] = ForInI(p[2], p[4], p[6], p.lineno(1), -1)


def p_for_in_i_2(p):
    """for_in_i : FOR ID IN expression DOT DOT expression KEY_O instructions KEY_C"""
    p[0] = ForInI(p[2], ForInRanged(p[4], p[7]), p[9], p.lineno(1), -1)


# ###############################################LOOP STATEMENT#########################################################
def p_loop_i(p):
    """loop_i : LOOP KEY_O instructions KEY_C"""
    p[0] = LoopI(p[3], p.lineno(1), -1)


# ##############################################WHILE STATEMENT#########################################################
def p_while_i(p):
    """while_i : WHILE expression KEY_O instructions KEY_C"""
    p[0] = WhileI(p[2], p[4], p.lineno(1), -1)


# ###############################################BREAK STATEMENT########################################################
def p_break_i_1(p):
    """break_i : BREAK expression"""
    p[0] = BreakI(p[2], p.lineno(1), -1)


def p_break_i_2(p):
    """break_i : BREAK"""
    p[0] = p[0] = BreakI(None, p.lineno(1), -1)


# #################################################CONTINUE STATEMENT###################################################
def p_continue_i_1(p):
    """continue_i : CONTINUE expression"""
    p[0] = ContinueI(p[2], p.lineno(1), -1)


def p_continue_i_2(p):
    """continue_i : CONTINUE"""
    p[0] = ContinueI(None, p.lineno(1), -1)


# #############################################RETURN STATEMENT#########################################################
def p_return_i_1(p):
    """return_i : RETURN expression"""
    p[0] = ReturnI(p[2], p.lineno(1), -1)


def p_return_i_2(p):
    """return_i : RETURN"""
    p[0] = ReturnI(None, p.lineno(1), -1)


# ################################################FUNCTION CALL I#######################################################
def p_function_call_i(p):
    """function_call_i : ID PARENTH_O func_call_args PARENTH_C"""
    p[0] = FunctionCallI(p[1], p[3], p.lineno(1), -1)


def p_func_call_args_r(p):
    """func_call_args : func_call_args COMMA func_call_arg"""
    p[0] = p[1] + [p[3]]


def p_func_call_args_1(p):
    """func_call_args : func_call_arg"""
    p[0] = [p[1]]


def p_func_call_args_2(p):
    """func_call_args : epsilon"""
    p[0] = list()


def p_func_call_arg_1(p):
    """func_call_arg : expression"""
    p[0] = FuncCallArg(p[1], False, False)


def p_func_call_arg_2(p):
    """func_call_arg : AMPERSAND expression"""
    p[0] = FuncCallArg(p[2], True, False)


def p_func_call_arg_3(p):
    """func_call_arg : AMPERSAND MUTABLE expression"""
    p[0] = FuncCallArg(p[3], True, True)


# ###############################################FUNCTION DECLARATION###################################################
def p_function_declaration_1(p):
    """function_declaration : FN ID PARENTH_O func_decl_args PARENTH_C KEY_O instructions KEY_C"""
    p[0] = FunctionDeclaration(p[2], p[4], ElementType.VOID, p[7], p.lineno(1), -1)


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


def p_func_var_3(p):  # Should only be used in arrays (and vectors??)
    """func_var : ID COLON AMPERSAND func_decl_array_var_type"""
    p[0] = IDTuple(p[1], p[4][0], False, True, p[4][1], None)


def p_func_var_4(p):
    """func_var : ID COLON AMPERSAND vector_type"""
    tmp = p[4]
    i = 1
    while (tmp.is_nested_vector):
        i += 1
        tmp = tmp.content_type
    p[0] = IDTuple(p[1], ElementType.VECTOR, False, True, i, tmp.content_type)


def p_func_var_5(p):
    """func_var : ID COLON AMPERSAND MUTABLE vector_type"""
    tmp = p[5]
    i = 1
    while (tmp.is_nested_vector):
        i += 1
        tmp = tmp.content_type
    p[0] = IDTuple(p[1], ElementType.VECTOR, True, True, i, tmp.content_type)


def p_func_var_6(p):  # Should only be used in arrays (and vectors??)
    """func_var : ID COLON AMPERSAND MUTABLE func_decl_array_var_type"""

    p[0] = IDTuple(p[1], p[5]["embedded_type"], True, True, p[5], None)


def p_func_var_7(p):  # Should only be used in arrays
    """func_var : ID COLON AMPERSAND array_type"""

    dic, _type = global_config.array_type_to_dimension_dict_and_type(p[4])
    p[0] = IDTuple(p[1], _type, False, True, dic, None)


def p_func_var_8(p):  # Should only be used in arrays
    """func_var : ID COLON AMPERSAND MUTABLE array_type"""

    dic, _type = global_config.array_type_to_dimension_dict_and_type(p[5])
    p[0] = IDTuple(p[1], _type, True, True, dic, None)


def p_func_call_array_var_type_r(p):
    """func_decl_array_var_type : BRACKET_O func_decl_array_var_type BRACKET_C"""
    p[2][len(p[2])] = None

    p[0] = p[2]  # further elements don't need to propagate type


def p_func_call_array_var_type(p):
    """func_decl_array_var_type : BRACKET_O variable_type BRACKET_C"""
    p[0] = {1:  None}
    p[0]["embedded_type"] = p[2]


# #################################################MATCH CLAUSES########################################################
def p_match_statement(p):
    """match_statement : MATCH expression KEY_O match_conditions KEY_C"""
    p[0] = MatchI(p[2], p[4], p.lineno(1), -1)


def p_match_conditions_1(p):
    """match_conditions : cases default_case"""
    p[0] = p[1] + p[2]


def p_match_conditions_2(p):
    """match_conditions : cases"""
    p[0] = p[1]


def p_match_conditions_3(p):
    """match_conditions : default_case"""
    p[0] = p[1]


def p_switch_cases_r_1(p):
    """cases : cases match_expr_list EQUAL OPE_MORE KEY_O instructions KEY_C"""
    p[0] = p[1] + [MatchClause(p[2], p[6], Environment(None))]


def p_switch_cases_r_2(p):
    """cases : cases match_expr_list EQUAL OPE_MORE no_semicolon_instruction COMMA"""
    p[0] = p[1] + [MatchClause(p[2], [p[5]], Environment(None))]


def p_switch_cases_1(p):
    """cases : match_expr_list EQUAL OPE_MORE KEY_O instructions KEY_C"""
    p[0] = [MatchClause(p[1], p[5], Environment(None))]


def p_switch_cases_2(p):
    """cases : match_expr_list EQUAL OPE_MORE no_semicolon_instruction COMMA"""
    p[0] = [MatchClause(p[1], [p[4]], Environment(None))]


def p_default_case_1(p):
    """default_case : UNDERSCORE_NULL EQUAL OPE_MORE KEY_O instructions KEY_C"""
    p[0] = [MatchClause(None, [p[5]], Environment(None))]


def p_default_case_2(p):
    """default_case : UNDERSCORE_NULL EQUAL OPE_MORE no_semicolon_instruction"""
    p[0] = [MatchClause(None, [p[4]], Environment(None))]


def p_match_expr_list_r(p):
    """match_expr_list : match_expr_list OR_STICK expression"""
    p[0] = p[1] + [p[3]]


def p_match_expr_list(p):
    """match_expr_list : expression"""
    p[0] = [p[1]]


# ##########################################IF CLAUSES##################################################################
def p_if_else_elseif_statement_1(p):
    """if_else_elseif : if_s"""
    p[0] = Conditional(p[1], p.lineno(1), -1)


def p_if_else_elseif_statement_2(p):
    """if_else_elseif : if_s else_s"""
    p[0] = Conditional(p[1] + p[2], p.lineno(1), -1)


def p_if_else_elseif_statement_3(p):
    """if_else_elseif : if_s else_ifs"""
    p[0] = Conditional(p[1] + p[2], p.lineno(1), -1)


def p_if_else_elseif_statement_4(p):
    """if_else_elseif : if_s else_ifs else_s"""
    p[0] = Conditional(p[1] + p[2] + p[3], p.lineno(1), -1)


def p_if_statement(p):
    """if_s : IF expression KEY_O instructions KEY_C"""
    p[0] = [ConditionClause(p[2], p[4], Environment(None))]


def p_elseifs_r(p):
    """else_ifs : else_ifs else_if"""
    p[0] = p[1] + p[2]


def p_elseifs(p):
    """else_ifs :  else_if"""
    p[0] = p[1]


def p_elseif(p):
    """else_if : ELSE IF expression KEY_O instructions KEY_C"""
    p[0] = [ConditionClause(p[3], p[5], Environment(None))]


def p_else(p):
    """else_s : ELSE KEY_O instructions KEY_C"""
    p[0] = [ConditionClause(None, p[3], Environment(None))]


# ###########################################PRINTLN####################################################################
def p_print_inst(p):
    """println_inst : PRINT LOGIC_NOT PARENTH_O expression_list PARENTH_C"""
    p[0] = PrintLN(p[4], False, p.lineno(1), -1)


# ###########################################PRINTLN####################################################################
def p_println_inst(p):
    """println_inst : PRINTLN LOGIC_NOT PARENTH_O expression_list PARENTH_C"""
    p[0] = PrintLN(p[4], True, p.lineno(1), -1)


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


# ###########################################VARIABLE ASSIGNMENT ###############################################

def p_var_assignment(p):
    """var_assignment : ID EQUAL expression"""
    p[0] = Assigment(p[1], p[3], p.lineno(1), -1)


# ###########################################ARRAY ASSIGNMENT ###############################################
def p_total_array_assignment(p):
    """array_assignment : ID EQUAL expression
    | ID EQUAL array_expression"""
    p[0] = ArrayAssignment(p[1], [], p[3], p.lineno(1), -1)
    # print("total_p_array_assignment")


def p_array_assignment(p):
    """array_assignment : ID array_indexes EQUAL expression
    | ID array_indexes EQUAL array_expression"""
    p[0] = ArrayAssignment(p[1], p[2], p[4], p.lineno(1), -1)
    # print("p_array_assignment")


# ###########################################ARRAY VARIABLE DECLARATION ###############################################
def p_array_declaration_1(p):    # TODO array_expression instead of expression
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

#######################################################################################################################


def p_variable_type_i64(p):
    """variable_type : TYPE_I64"""
    p[0] = ElementType.INT


def p_variable_type_usize(p):
    """variable_type : TYPE_USIZE"""
    p[0] = ElementType.USIZE


def p_variable_type_f64(p):
    """variable_type : TYPE_F64"""
    p[0] = ElementType.FLOAT


def p_variable_type_bool(p):
    """variable_type : TYPE_BOOL"""
    p[0] = ElementType.BOOL


def p_variable_type_char(p):
    """variable_type : TYPE_CHAR"""
    p[0] = ElementType.CHAR


def p_variable_type_amper_str(p):
    """variable_type : AMPERSAND TYPE_AMPER_STR"""
    p[0] = ElementType.STRING_PRIMITIVE


def p_variable_type_string(p):
    """variable_type : TYPE_STRING"""
    p[0] = ElementType.STRING_CLASS
#######################################################################################################################


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def p_loop_as_expression(p):
    """expression : LOOP KEY_O instructions KEY_C"""
    p[0] = LoopE(p[3], p.lineno(1), -1)


def p_parameter_func_call(p):
    """expression : ID DOT ID PARENTH_O func_call_args PARENTH_C %prec PREC_METHOD_CALL"""
    p[0] = ParameterFunctionCallE(p[1], p[3], p[5], p.lineno(1), -1)


def p_parameter_func_call_array_ref(p):
    """expression : expression DOT ID PARENTH_O func_call_args PARENTH_C %prec PREC_METHOD_CALL"""
    p[0] = ParameterFunctionCallE(p[1], p[3], p[5], p.lineno(2), -1)


def p_casting(p):
    """expression : expression AS variable_type"""
    p[0] = TypeCasting(p[3], p[1], p.lineno(2), -1)


def p_function_call_e(p):
    """expression : ID PARENTH_O func_call_args PARENTH_C %prec PREC_FUNC_CALL"""
    p[0] = FunctionCallE(p[1], p[3], p.lineno(1), -1)


# Will this break the parser?
def p_expression_array_expression(p):
    """expression : array_expression"""
    p[0] = p[1]


def p_expression_integer(p):
    """expression : INTEGER"""
    p[0] = Literal(p[1], ElementType.INT, p.lineno(1), -1)


def p_expression_float(p):
    """expression : FLOAT"""
    p[0] = Literal(p[1], ElementType.FLOAT, p.lineno(1), -1)


def p_expression_string(p):
    """expression : STRING_TEXT"""
    p[0] = Literal(p[1], ElementType.STRING_PRIMITIVE, p.lineno(1), -1)


def p_expression_char(p):
    """expression : CHAR"""
    p[0] = Literal(p[1], ElementType.CHAR, p.lineno(1), -1)


def p_expression_true(p):
    """expression : BOOL_TRUE"""
    p[0] = Literal(True, ElementType.BOOL, p.lineno(1), -1)


def p_expression_false(p):
    """expression : BOOL_FALSE"""
    p[0] = Literal(False, ElementType.BOOL, p.lineno(1), -1)


def p_expression_plus(p):
    """expression : expression SUM expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.SUM, p.lineno(2), -1)


def p_expression_minus(p):
    """expression : expression SUB expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.SUB, p.lineno(2), -1)


def p_expression_mult(p):
    """expression : expression MULT expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.MULT, p.lineno(2), -1)


def p_expression_div(p):
    """expression : expression DIV expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.DIV, p.lineno(2), -1)


def p_expression_pow_int(p):
    """expression : TYPE_I64 COLON COLON POW PARENTH_O expression COMMA expression PARENTH_C"""
    p[0] = Arithmetic(p[6], p[8], ArithmeticType.POW_INT, p.lineno(1), -1)


def p_expression_pow_float(p):
    """expression : TYPE_F64 COLON COLON POWF PARENTH_O expression COMMA expression PARENTH_C"""
    p[0] = Arithmetic(p[6], p[8], ArithmeticType.POW_FLOAT, p.lineno(1), -1)


def p_expression_mod(p):
    """expression : expression MOD expression"""
    p[0] = Arithmetic(p[1], p[3], ArithmeticType.MOD, p.lineno(2), -1)


def p_expression_uminus(p):
    """expression : SUB expression %prec UMINUS"""
    p[0] = Arithmetic(p[2], p[2], ArithmeticType.NEG, p.lineno(1), -1)


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


# VAR REF
def p_var_ref_e(p):
    """expression : ID %prec PREC_VAR_REF"""
    p[0] = VariableReference(p[1], p.lineno(1), -1)


# ARRAY REF
def p_array_ref(p):
    """expression : ID array_indexes %prec PREC_ARRAY_REF"""
    p[0] = ArrayReference(p[1], p[2], p.lineno(1), -1)


def p_array_indexes_r(p):
    """array_indexes : array_indexes BRACKET_O expression BRACKET_C"""
    p[1].append(p[3])
    p[0] = p[1]


def p_array_indexes(p):
    """array_indexes : BRACKET_O expression BRACKET_C"""
    p[0] = [p[2]]


# Match as expression
def p_match_as_expr(p):
    """expression : match_expr"""
    p[0] = p[1]


# If as expression
def p_if_expr(p):
    """expression : if_else_elseif_expr"""
    p[0] = p[1]


# ############################################MATCH CLAUSES AS EXPR (NEEDS TESTING)#####################################
def p_match_expr(p):
    """match_expr : MATCH expression KEY_O match_expr_conditions KEY_C"""
    p[0] = MatchExpression(p[2], p[4], p.lineno(1), -1)


def p_match_expr_conditions_1(p):
    """match_expr_conditions : cases_expr default_case_expr"""
    p[0] = p[1] + p[2]


def p_match_expr_conditions_2(p):
    """match_expr_conditions : cases_expr"""
    p[0] = p[1]


def p_match_expr_conditions_3(p):
    """match_conditions : default_case_expr"""
    p[0] = p[1]


def p_switch_expr_cases_r(p):
    """cases_expr : cases_expr match_expr_list EQUAL OPE_MORE expression COMMA"""
    p[0] = p[1] + [MatchExpressionClause(p[2], p[5], Environment(None))]


def p_switch_cases_expr(p):
    """cases_expr : match_expr_list EQUAL OPE_MORE expression COMMA"""
    p[0] = [MatchExpressionClause(p[1], p[4], Environment(None))]


def p_default_case_expr(p):
    """default_case_expr : UNDERSCORE_NULL EQUAL OPE_MORE expression"""
    p[0] = [MatchExpressionClause(None, p[4], Environment(None))]


# Already defined, reused
# def p_match_expr_list_r(p):
#     """match_expr_list : match_expr_list OR_STICK expression"""
#     p[0] = p[1] + [p[2]]
#
#
# def p_match_expr_list(p):
#     """match_expr_list : expression"""
#     p[0] = p[1]

# #####################################################IF CLAUSES EXPRESSION############################################
def p_if_else_elseif_statement_1_expr(p):
    """if_else_elseif_expr : if_s_expr"""
    p[0] = ConditionalExpression(p[1], p.lineno(1), -1)
    # print("cond expr 1")


def p_if_else_elseif_statement_2_expr(p):
    """if_else_elseif_expr : if_s_expr else_s_expr"""
    p[0] = ConditionalExpression(p[1] + p[2], p.lineno(1), -1)
    # print("cond expr 2")


def p_if_else_elseif_statement_3_expr(p):
    """if_else_elseif_expr : if_s_expr else_ifs_expr"""
    p[0] = ConditionalExpression(p[1] + p[2], p.lineno(1), -1)
    # print("cond expr 3")


def p_if_else_elseif_statement_4_expr(p):
    """if_else_elseif_expr : if_s_expr else_ifs_expr else_s_expr"""
    p[0] = ConditionalExpression(p[1] + p[2] + p[3], p.lineno(1), -1)
    # print("cond expr 4")


def p_if_statement_expr_1(p):
    """if_s_expr : IF expression KEY_O expression KEY_C"""
    p[0] = [ConditionExpressionClause(p[2], [], p[4], Environment(None))]


def p_if_statement_expr_2(p):
    """if_s_expr : IF expression KEY_O instructions expression KEY_C"""
    p[0] = [ConditionExpressionClause(p[2], p[4], p[5], Environment(None))]

    a = global_config.generate_symbol_table(p[4], "Expr:IF" + global_config.random_hex_color_code())
    global_config.tmp_symbol_table = global_config.tmp_symbol_table + a


def p_elseifs_r_expr(p):
    """else_ifs_expr : else_ifs_expr else_if_expr"""
    p[0] = p[1] + p[2]


def p_elseifs_expr(p):
    """else_ifs_expr :  else_if_expr"""
    p[0] = p[1]


def p_elseif_expr_1(p):
    """else_if_expr : ELSE IF expression KEY_O expression KEY_C"""
    p[0] = [ConditionExpressionClause(p[3], [], p[5], Environment(None))]


def p_elseif_expr_2(p):
    """else_if_expr : ELSE IF expression KEY_O instructions expression KEY_C"""
    p[0] = [ConditionExpressionClause(p[3], p[5], p[6], Environment(None))]
    a = global_config.generate_symbol_table(p[5], "Expr:ELSE-IF" + global_config.random_hex_color_code())
    global_config.tmp_symbol_table = global_config.tmp_symbol_table + a


def p_else_expr_1(p):
    """else_s_expr : ELSE KEY_O expression KEY_C"""
    p[0] = [ConditionExpressionClause(None, [], p[3], Environment(None))]


def p_else_expr_2(p):
    """else_s_expr : ELSE KEY_O instructions expression KEY_C"""
    p[0] = [ConditionExpressionClause(None, p[3], p[4], Environment(None))]

    a = global_config.generate_symbol_table(p[3], "Expr:ELSE" + global_config.random_hex_color_code())
    global_config.tmp_symbol_table = global_config.tmp_symbol_table + a



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
