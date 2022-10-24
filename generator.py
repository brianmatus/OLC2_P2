import global_config
from typing import List

debug_prints = False
add_comments = True
HEAP_SIZE = 2500
HEAP_COUNTER = 0
STACK_SIZE = 100
STACK_COUNTER = 0


class Generator:

    def __init__(self, env) -> None:
        # self.generator = None
        self.code: list = []
        self.tempList: list = []
        self.env = env

    def get_used_temps(self) -> str:
        return ",".join([f"t{i}" for i in range(global_config.tmp_i)])

    def get_code(self) -> str:
        return "\n".join(self.code)

    def set_as_final_code(self) -> str:
        self.add_main_enclosure()
        self.code = global_config.function_3ac_code + self.code
        self.add_tmps_on_top()
        self.add_headers_on_top()

        return "\n".join(self.code)

    def combine_with(self, gen):  # gen: Generator
        self.code = self.code + gen.code[:]  # slice is ok? idk
        self.tempList = self.tempList + gen.tempList[:]
        return self

    # tmp
    def new_temp(self, persist=False) -> str:
        tmp = "t" + str(global_config.tmp_i)
        self.tempList.append(global_config.tmp_i)
        global_config.tmp_i += 1
        if persist:
            self.env.add_tmp_to_function(tmp)
        return tmp

    # Label
    def new_label(self) -> str:
        tmp = global_config.label_i
        global_config.label_i = global_config.label_i + 1
        return "L" + str(tmp)

    ##############################################################

    def add_main_enclosure(self):

        if debug_prints:
            self.code = [f"int main(){{\n"
                         f"P = 0;\n"
                         f"H = 0;\n"
                         f"int heap_iter;\n"
                         f"for(heap_iter = 0; heap_iter < sizeof(HEAP) / sizeof(double); heap_iter++) {{\n"
                         f"HEAP[heap_iter] = -42;\n"
                         f"}}\n"
                         f"for(heap_iter = 0; heap_iter < sizeof(STACK) / sizeof(double); heap_iter++) {{\n"
                         f"STACK[heap_iter] = -42;\n"
                         f"}}\n"
                         f"{self.get_code()}\n"
                         # f"//--------------------------DEBUG INFO-----------------\n"
                         # f'printf("Final H:%f\\n", H);\n'
                         # f'printf("Final P:%f\\n", P);\n'
                         # f'printf("STACK:\\n[\\n");\n'
                         # f'int i;\n'
                         # 
                         # 
                         # f'for(i = 0; i < sizeof(STACK) / sizeof(double); i++){{\n'
                         # f'printf("%i : %.2f\\n", i, STACK[i]);\n'
                         # f'}}\n'
                         # f'printf("]\\n");\n'
                         # f'printf("HEAP:\\n[\\n");\n'
                         # f'for(i = 0; i < sizeof(HEAP) / sizeof(double); i++){{\n'
                         # f'printf("%i : %.2f\\n", i, HEAP[i]);\n'
                         # f'}}\n'
                         # f'printf("]\\n");\n'
                         
                         f"return 0;\n"
                         f"}}\n"]
            return

        self.code = [f"int main(){{\n"
                     f"{self.get_code()}\n"
                     # f"//----------------------------CODE END------------------\n"
                     f"fn_main();\n"
                     f"return 0;\n"
                     f"}}"]

    # should be called after add_main_enclosure
    def add_tmps_on_top(self):
        if global_config.tmp_i > 0:
            self.code = [f"double {self.get_used_temps()};\n\n",
                         f"{self.get_code()}\n"]

        # self.code = [f"double t0,t1,t2;\n\n{self.get_code()}\n"]

    # should be called after add_tmps_on_top
    def add_headers_on_top(self):
        a = self.code[::]
        self.code = [f'#include <stdio.h>\n'
                     f'#include <math.h>\n'
                     f'double HEAP[{HEAP_SIZE}];\n'
                     f'double STACK[{STACK_SIZE}];\n'
                     f'double P;\n'
                     f'double H;\n\n']

        # for func in global_config.function_list.keys():
        #     self.code.append(f"void fn_{func}();")

        self.code += a

    ##############################################################

    # foo()
    def add_call_func(self, name: str):
        self.code.append(f'{name}();')
        self.code.append(name + "();")

    # label
    def add_label(self, label: List[str]):
        if len(label) == 0:
            return
        for lbl in label:
            if lbl == "":
                print("WARNING: LBL IS EMPTY")

            self.code.append(f"{lbl}:")

    # var = val
    def add_expression(self, target: str, left: str, right: str, operator: str):
        self.code.append(f'{target} = {left} {operator} {right};')

    def add_casting(self, target: str, to_be_casted: str, cast_to: str):
        self.code.append(f'{target} = ({cast_to}) {to_be_casted};')

    # if
    def add_if(self, left: str, right: str, operator: str, label: str):
        self.code.append(f"if ({left} {operator} {right} ) goto {label};")

    # goto
    def add_goto(self, label: str):
        self.code.append(f"goto {label};")

    # printf(...)
    def add_printf(self, type_print: str, value: str):
        self.code.append(f"printf(\"%{type_print}\",{value});")

    def add_print_message(self, msg: str):
        escaped = msg.translate(str.maketrans({"\n": r"\\n",
                                                    }))
        # self.code.append(f"// Printing:{escaped}")
        for char in msg:
            self.code.append(f"printf(\"%c\",{str(ord(char))});")

    # prints newline
    def add_newline(self):
        self.code.append('printf(\"%c\",10);')

    # H = H + 1
    def add_next_heap(self):
        global HEAP_COUNTER

        if HEAP_COUNTER >= HEAP_SIZE:
            error_msg = f'GENERATOR::HEAP OVERFLOW'
            global_config.log_semantic_error(error_msg, -42, -42)
            from errors.semantic_error import SemanticError
            raise SemanticError(error_msg, -42, -42)

        self.code.append("H = H + 1;")
        HEAP_COUNTER += 1

    # P = P + i
    def add_next_stack(self, index: str):
        self.code.append(f"P = P + {index};")

    # P = P - i
    def add_back_stack(self, index: str):
        self.code.append(f"P = P - {index};")

    # heap[i]
    def add_get_heap(self, target: str, index: str):
        self.code.append(f"{target} = HEAP[(int){index}];")

    # heap[i] = val
    def add_set_heap(self, index: str, value: str):
        self.code.append(f'HEAP[(int){index}] = {value};')

    # stack[i]
    def add_get_stack(self, target: str, index: str):
        self.code.append(f'{target} = STACK[(int){index}];')

    # heap[i] = val
    def add_set_stack(self, index: str, value: str):
        self.code.append(f'STACK[(int){index}] = {value};')

    # 1: Division by 0
    # 2: Index out of bounds
    # ?? idk i forgot
    def add_error_return(self, return_code: str):
        # self.code.append(f"return {return_code};")
        if return_code != "":
            self.code.append(f"t1={return_code};")
        self.code.append(f"return;")

    def add_comment(self, msg):
        if add_comments:
            pass
            # self.code.append(f"//{msg}")

    def add_set_as_function(self, name):
        a = self.code[::]
        self.code = []
        self.code.append(f"void fn_{name} (){{")

        # tmp_str = ""
        # for tmp in self.tempList:
        #     tmp_str += f",t{tmp}"
        # self.code.append(f"double {tmp_str[1:]};")
        self.code += a
        self.code.append("H=H; // exit label can't be empty lmao")
        self.code.append("}")

    def add_func_call(self, func_id):
        self.code.append(f"fn_{func_id}();")
