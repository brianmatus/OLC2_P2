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

    path = 'C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c'
    with io.open(path, 'r', encoding='utf8', newline='\n') as fin:
        input_code = fin.read()

    f_opt, code = perform_optimization(input_code)
    path = 'C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main-o.c'
    with io.open(path, 'w', encoding='utf8', newline='\n') as fout:
        fout.write(code)

    print("---------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------")
    for opted in f_opt:
        a, b, c, d = opted.split("<->")
        print(f'{a}::{b}            {c}      -> {d}')



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
        # final_generator.add_label([main_start])
        global_config.main_environment.is_function_env = True
        # final_generator.combine_with(synthetic_call.execute(global_config.main_environment).generator)
        final_generator.add_comment("<<<<<<<<<<<<<<<<<<<<End of program>>>>>>>>>>>>>>>>>>")

        _symbol_table = main_func.environment.symbol_table
        pp = Generator(None)
        pp.set_as_final_code()
        final_generator.combine_with(pp)
        # final_generator.set_as_final_code()
        # print(final_generator.get_code())

        #
        # output_file = open('C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c', "w")
        # output_file.write(str(final_generator.get_code()))
        # output_file.close()
        path = 'C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main.c'
        with io.open(path, 'w', encoding='utf8', newline='\n') as fout:
            fout.write(final_generator.get_code().replace("+ -", "- "))

        with io.open('opt_code.c', 'w', encoding='utf8', newline='\n') as fout:
            fout.write(final_generator.get_code().replace("+ -", "- "))

        print("-------------------------------------------------------------------------------------------------------")

        # _symbol_table = main_func.environment.symbol_table  # TODO delete me, debug only
        # _function_list = global_config.function_list  # TODO delete me, debug only
        # print("Resulting function list:")
        # print(function_list)
        # print("Resulting symbol table:")
        # symbol_table = global_config.generate_symbol_table(instruction_set, "Main")

        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")
        print("--------------------------------------INITIAL COMPILING FINISHED---------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")

        global_config.console_output += "\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "Initial compiling finished, exit code: 0\n"

        opt_list, opted_code = perform_optimization(final_generator.get_code().replace("+ -", "- "))

        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------OPTIMIZATION FINISHED---------------------------------------")
        print("                                           OPTIMIZATIONS MADE: " + str(len(opt_list)))
        print("-------------------------------------------------------------------------------------------------------")
        print("-------------------------------------------------------------------------------------------------------")

        global_config.console_output += "\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += "----------------------------------------------------------------------------\n"
        global_config.console_output += f"Optimization finished, {len(opt_list)} optimizations made\n"
        global_config.console_output += "Program finished, exit code: 0\n"

        path = 'C:\\Users\\Matus\\Documents\\USAC\\Compi2\\Proyecto2\\c-interp\\main-o.c'
        with io.open(path, 'w', encoding='utf8', newline='\n') as fout:
            fout.write(opted_code)

        return {
            "console_output": global_config.console_output,
            "lexic_errors": global_config.lexic_error_list,
            "syntactic_errors": global_config.syntactic_error_list,
            "semantic_errors": global_config.semantic_error_list,
            "symbol_table":
            global_config.tmp_symbol_table + global_config.generate_symbol_table(instruction_set, "Main"),
            "optimization": opt_list
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

    final_report_list = []

    opt_code = code
    func_names = re.findall(r'void fn_[^(]*(?=\(\))', opt_code)
    resulting_functions = []
    headers = re.search(r'([\s\S]*double t0[^;]*;)', code).group(1)
    for func in func_names:
        mm = f'(?<={func}\(\){{)([^}}]*)(?=}})'
        print(mm)
        func_code = re.search(mm, opt_code).group(0)

        blocks = [func_code]

        separators = [r'L[0-9]*:', r'goto L[0-9]*;', r'[a-zA-Z0-9_]*\(\);', 'return;']
        for reg_exp in separators:
            # Separate by labels
            sub_set = []
            for block in blocks:
                while True:
                    matched = re.search(reg_exp, block)
                    if matched is None:
                        sub_set.append(block)
                        break
                    _, match_j = matched.span()
                    sub_set.append(block[:match_j])
                    block = block[match_j:]
            blocks = sub_set

        optimized_blocks = []
        i = 0
        for block in blocks:
            print(f"opting block#{i}")
            i += 1

            partial = block
            while True:
                opt = Optimizer()
                partial = opt.optimize_local_rule_1(partial, code)
                partial = opt.optimize_local_rule_2(partial, code)
                # rule 2
                # rule 3
                # rule 4
                if len(opt.reports) == 0:
                    break
                final_report_list = final_report_list + opt.reports

            optimized_blocks.append(partial)

        the_code = "\n".join(optimized_blocks)
        the_f = f'{func}(){{\n{the_code}\n}}'
        resulting_functions.append(the_f)

    opt_opt_code = "\n".join(resulting_functions)
    gg = Generator(None)
    gg.add_main_enclosure()
    si_salio_este_semestre = f'{headers}\n{opt_opt_code}\n{gg.get_code()}'
    si_salio_este_semestre = re.sub('goto(L[0-9]+);', lambda m: f'goto {m.group(1)};', si_salio_este_semestre)

    return final_report_list, si_salio_este_semestre



if __name__ == '__main__':
    start()
    # start_opt()

    # x = 38
    # print(newtons_method_sqrt(x, x / 2))
