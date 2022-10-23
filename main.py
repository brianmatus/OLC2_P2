import traceback

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

from optimizer import Optimizer, OptimizationReport
import re

from typing import Tuple

# TODO import: function decl, declaration, array declare, conditional, switch, while, for, logic


def start_opt():

    with io.open('opt_code.c', 'r', encoding='utf8', newline='\n') as fin:
        input_code = fin.read()
    f_opt, code = perform_optimization(input_code)
    pass

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

    # print(instruction_set)

    synthetic_call = FunctionCallI("main", [], -1, -1)

    # Register all functions and modules
    try:
        instruction: Instruction
        final_generator: Generator = Generator(global_config.main_environment)
        main_start = final_generator.new_label()
        # final_generator.add_goto(main_start)

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
        global_config.main_environment.is_function_env = True
        final_generator.combine_with(synthetic_call.execute(global_config.main_environment).generator)
        final_generator.add_comment("<<<<<<<<<<<<<<<<<<<<End of program>>>>>>>>>>>>>>>>>>")

        _symbol_table = main_func.environment.symbol_table
        final_generator.set_as_final_code()
        # print(final_generator.get_code())

        #
        # output_file = open('C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c', "w")
        # output_file.write(str(final_generator.get_code()))
        # output_file.close()
        path = 'C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c'
        with io.open(path, 'w', encoding='utf8', newline='\n') as fout:
            fout.write(final_generator.get_code())

        print("-------------------------------------------------------------------------------------------------------")

        # _symbol_table = main_func.environment.symbol_table  # TODO delete me, debug only
        # _function_list = global_config.function_list  # TODO delete me, debug only
        # print("Resulting function list:")
        # print(function_list)
        print("Resulting symbol table:")
        symbol_table = global_config.generate_symbol_table(instruction_set, "Main")

        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")
        print("--------------------------------------INITIAL COMPILING FINISHED---------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")

        global_config.console_output += "\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "------------------INITIAL COMPILING FINISHED-------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"

        # f_opt, code = perform_optimization(final_generator.get_code())

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table":
            global_config.tmp_symbol_table + global_config.generate_symbol_table(instruction_set, "Main"),
            # "optimization": f_opt
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


def perform_optimization(code) -> Tuple[list, str]:

    opt = Optimizer()

    opt_code = code
    func_names = re.findall(r'void fn_[^(]*(?=\(\))', opt_code)

    for func in func_names:
        mm = f'(?<={func}\(\){{)([^}}]*)(?=}})'
        print(mm)
        func_code = re.search(mm, opt_code).group(0)

        blocks = []
        while True:
            label = re.search(r'L[0-9]*:', func_code)
            jump = re.search(r'goto L[0-9]*;', func_code)
            if label is None and jump is None:
                blocks.append(func_code)
                break

            label_i, label_j = 0, 0
            jump_i, jump_j = 0, 0
            if label is not None:
                label_i, label_j = label.span()
            if jump is not None:
                jump_i, jump_j = jump.span()

            if label_i < jump_i and label is not None:
                blocks.append(func_code[:label_j])
                func_code = func_code[label_j:]
                continue

            blocks.append(func_code[:jump_j])
            func_code = func_code[jump_j:]

        optimized_blocks = []
        for block in blocks:
            block_result = opt.optimize_local_rule_1(block)



    return opt.reports, opt_code



if __name__ == '__main__':
    start()
    # start_opt()

    # x = 38
    # print(newtons_method_sqrt(x, x / 2))
