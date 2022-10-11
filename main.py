import traceback

import analysis.lexer as lexer  # TODO for debug only

from typing import List, Union

from generator import Generator

import errors.custom_semantic
from analysis.parser import parser

from abstract.instruction import Instruction
from elements.c_env import Environment

from instructions.function_declaration import FunctionDeclaration
from instructions.function_call import FunctionCallI


from errors.lexic_error import LexicError
from errors.semantic_error import SemanticError
from errors.syntactic_error import SyntacticError


import global_config
import io



# TODO import: function decl, declaration, array declare, conditional, switch, while, for, logic


def start():  # FIXME this should be replaced with frontend sending the code
    # f = open("code.rs", "r", encoding='utf-8')
    # input_code: str = f.read()
    # f.close()

    input_code = ""

    with io.open('code.rs', 'r', encoding='utf8', newline='\n') as fin:
        input_code = fin.read()



    result: dict = parse_code(input_code)
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

    print(instruction_set)

    synthetic_call = FunctionCallI("main", [], -1, -1)

    # Register all functions and modules
    try:
        instruction: Instruction
        final_generator: Generator = Generator()
        main_start = final_generator.new_label()
        final_generator.add_goto(main_start)

        for instruction in instruction_set:
            if not isinstance(instruction, FunctionDeclaration):  # Or Module declaration
                error_msg = f"No se permiten declaraciones globales."
                global_config.log_semantic_error(error_msg, instruction.line, instruction.column)
                raise SemanticError(error_msg, instruction.line, instruction.column)
            a = instruction.execute(global_config.main_environment)
            final_generator.combine_with(a.generator)
            if a.propagate_continue or a.propagate_break:
                error_msg = f"break/continue colocado erróneamente"
                global_config.log_semantic_error(error_msg, instruction.line, instruction.column)
                raise SemanticError(error_msg, instruction.line, instruction.column)

            if a.propagate_method_return:
                break

        # TODO main_func: FunctionDeclaration = global_config.function_list.get("main")
        main_func = global_config.function_list.get("main")
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

        # TODO "Apartir de aqui todo vale madre"
        final_generator.add_label([main_start])
        final_generator.combine_with(synthetic_call.execute(global_config.main_environment).generator)
        final_generator.add_comment("<<<<<<<<<<<<<<<<<<<<End of program>>>>>>>>>>>>>>>>>>")

        _symbol_table = main_func.environment.symbol_table
        print(final_generator.set_as_final_code())
        # output_file = open('C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c', "w")
        # output_file.write(str(final_generator.get_code()))
        # output_file.close()

        path = 'C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c'
        with io.open(path, 'w', encoding='utf8', newline='\n') as fout:
            fout.write(final_generator.get_code())

        print("-------------------------------------------------------------------------------------------------------")

        # print("Resulting AST:")
        # print(generate_ast_tree(instruction_set))
        print("Resulting environment:")
        _symbol_table = main_func.environment.symbol_table  # TODO delete me, debug only
        _function_list = global_config.function_list  # TODO delete me, debug only
        print(global_config.main_environment)
        print("Resulting function list:")
        # print(function_list)
        # print("Resulting symbol table:")
        # print(global_config.generate_symbol_table(instruction_set, "Main"))
        print("Resulting console output:")
        print("-------------------------------------------------------------------------------------------------------")
        print(global_config.console_output)

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            # "symbol_table":
            # global_config.tmp_symbol_table + global_config.generate_symbol_table(instruction_set, "Main")
        }

        # return [global_config.lexic_error_list, global_config.syntactic_error_list,
        #                    global_config.semantic_error_list,
        #                    global_config.generate_symbol_table(instruction_set, "Main"),
        #                    global_config.console_output, ""]

    except Exception as err:
        traceback.print_exc()
        # print(err)

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
            # "symbol_table":
            # global_config.tmp_symbol_table + global_config.generate_symbol_table(instruction_set, "Main")
        }

        # return [global_config.lexic_error_list,
        #                    global_config.syntactic_error_list, global_config.semantic_error_list,
        #                    generate_ast_tree(instruction_set),
        #                    global_config.console_output,
        #                    global_config.generate_symbol_table(instruction_set, "Main")]


def newtons_method_sqrt(x, x0):
    tol = 1/100000000
    root_approx = x0
    y_n = x0 * x0 - x
    dy_n = 2*x0
    while -tol >= y_n or y_n >= tol:
        root_approx = root_approx - y_n/dy_n
        y_n = root_approx * root_approx - x
        dy_n = 2*x0
    return root_approx


if __name__ == '__main__':
    start()

    # x = 38
    # print(newtons_method_sqrt(x, x / 2))
