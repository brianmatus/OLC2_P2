import traceback

import analysis.lexer as lexer  # TODO for debug only

from typing import List

import errors.custom_semantic
from returns.parse_result import ParseResult
from analysis.parser import parser

from instructions.instruction import Instruction
from instructions.function_declaration import FunctionDeclaration
from elements.env import Environment

from errors.lexic_error import LexicError
from errors.semantic_error import SemanticError
from errors.syntactic_error import SyntacticError


import global_config



# TODO import: function decl, declaration, array declare, conditional, switch, while, for, logic


def start():  # FIXME this should be replaced with frontend sending the code
    f = open("code.rs", "r")
    input_code: str = f.read()
    f.close()

    result: ParseResult = parse_code(input_code)
    return result
    # print("code result:")
    # print(result)


def parse_code(code_string: str) -> dict:  # -> ParseResult
    # Debug tokenizer
    # lexer.lexer.input(code_string)
    # # Tokenize
    # while True:
    #     tok = lexer.lexer.token()
    #     if not tok:
    #         return
    #     print(tok)

    code_string += "\n"
    global_config.main_environment = Environment(None)

    global_config.lexic_error_list = []
    global_config.syntactic_error_list = []
    global_config.semantic_error_list = []
    global_config.tmp_symbol_table = []
    # global_config.function_list = {}
    # func list
    global_config.console_output = ""
    try:
        instruction_set = parser.parse(code_string, tracking=True)

    except errors.custom_semantic.CustomSemanticError as err:
        traceback.print_exc()
        print(err)
        print("Unhandled semantic error?, custom semantic?")
        # already logged, do nothing

        global_config.main_environment = Environment(None)


        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table": []
        }


        # return [str(global_config.lexic_error_list),
        #                    str(global_config.syntactic_error_list), str(global_config.semantic_error_list),
        #                    'digraph G {\na[label="PARSE ERROR :( (semantic)"]\n}',
        #                    global_config.console_output, []]

    except SyntacticError as err:
        print("SYNTACTIC ERROR:")
        print(err)

        global_config.main_environment = Environment(None)

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table": []
        }

        # return [global_config.lexic_error_list,
        #                    global_config.syntactic_error_list, global_config.semantic_error_list,
        #                    'digraph G {\na[label="PARSE ERROR :( (syntactic)"]\n}',
        #                    global_config.console_output, []]


    except Exception as err:
        print("Unhandled (lexic?)/semantic error?")
        traceback.print_exc()
        print(err)

        # TODO implement semantic differentiation for missing token / unexpected one (in case i missed one)

        global_config.main_environment = Environment(None)

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table": []
        }

        # return [global_config.lexic_error_list,
        #                    global_config.syntactic_error_list, global_config.semantic_error_list,
        #                    'digraph G {\na[label="PARSE ERROR :( (syntactic)"]\n}',
        #                    global_config.console_output, []]

    # print("#############################################################################")
    # print("#############################################################################")
    # print("#############################################################################")
    # print("#############################################################################")


    # print(instruction_set)

    # Register all functions and modules
    try:
        instruction: Instruction
        for instruction in instruction_set:

            if not isinstance(instruction, FunctionDeclaration):  # Or Module declaration
                error_msg = f"No se permiten declaraciones globales."
                global_config.log_semantic_error(error_msg, instruction.line, instruction.column)
                raise SemanticError(error_msg, instruction.line, instruction.column)

            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            instruction.execute(global_config.main_environment)

        main_func: FunctionDeclaration = global_config.function_list.get("main")
        if main_func is None:
            error_msg = f"No se definió una función main"
            global_config.log_semantic_error(error_msg, -1, -1)
            raise SemanticError(error_msg, -1, -1)

        # print(main_func.params)
        if len(main_func.params) != 0:
            error_msg = f"ADVERTENCIA: La función main debe llamarse sin argumentos. Estos serán ignorados"
            global_config.log_semantic_error(error_msg, -1, -1)
            # No need to raise, they will only get ignored
            # raise SemanticError(error_msg, -1, -1)

        # "Abandonen la esperanza todos los que entren aquí"
        for instruction in main_func.instructions:
            instruction.execute(main_func.environment)
            _symbol_table = main_func.environment.symbol_table

        print("-------------------------------------------------------------------------------------------------------")

        # print("Resulting AST:")
        # print(generate_ast_tree(instruction_set))
        print("Resulting environment:")
        _symbol_table = main_func.environment.symbol_table  # TODO delete me, debug only
        _function_list = global_config.function_list  # TODO delete me, debug only
        print(global_config.main_environment)
        print("Resulting function list:")
        # print(function_list)
        print("Resulting symbol table:")
        print(global_config.generate_symbol_table(instruction_set, "Main"))
        print("Resulting console output:")
        print("-------------------------------------------------------------------------------------------------------")
        print(global_config.console_output)

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table": global_config.tmp_symbol_table + global_config.generate_symbol_table(instruction_set, "Main")
        }

        # return [global_config.lexic_error_list, global_config.syntactic_error_list,
        #                    global_config.semantic_error_list, global_config.generate_symbol_table(instruction_set, "Main"),
        #                    global_config.console_output, ""]

    except Exception as err:
        traceback.print_exc()
        print(err)

        print("#####################Errores Lexicos:###################")
        lexic: LexicError
        for lexic in global_config.lexic_error_list:
            print(lexic)
            # print("[row:%s,column:%s]Error Lexico: <%s> no reconocido", lexic.row, lexic.column, lexic.reason)

        print("#####################Errores Sintactico:###################")
        syntactic: SyntacticError
        for syntactic in global_config.syntactic_error_list:
            print(syntactic)
            # print("[row:%s,column:%s]ERROR:%s", syntactic.row, syntactic.column, syntactic.reason)

        print("#####################Errores Semantico:###################")
        semantic: SemanticError
        for semantic in global_config.semantic_error_list:
            print(semantic)
            # print("[row:%s,column:%s]ERROR:%s", semantic.row, semantic.column, semantic.reason)


        print(global_config.console_output)

        global_config.main_environment = Environment(None)

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table": global_config.tmp_symbol_table + global_config.generate_symbol_table(instruction_set, "Main")
        }

        # return [global_config.lexic_error_list,
        #                    global_config.syntactic_error_list, global_config.semantic_error_list,
        #                    generate_ast_tree(instruction_set),
        #                    global_config.console_output,
        #                    global_config.generate_symbol_table(instruction_set, "Main")]






def generate_ast_tree(instruction_set: List[Instruction]) -> str:
    return ""  # TODO this project doesn't require it
    # instructions_father_ref = global_config.get_unique_number()
    # ast_tree: str = f'digraph{{\n{instructions_father_ref}[label="Instructions"]\n'
    #
    # instructions_ast: str = generate_instruction_set_ast(instruction_set, instructions_father_ref)
    #
    # ast_tree += f'{instructions_ast}\n}}'
    # return ast_tree


def generate_instruction_set_ast(instruction_set: List[Instruction], father_ref: int) -> str :
    _str = ''
    instruction: Instruction
    for instruction in instruction_set:
        instruction_ast = instruction.ast()
        _str += f'{instruction_ast.value}\n' \
                f'{father_ref} -> {instruction_ast.head_ref}\n'

    return _str


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()
