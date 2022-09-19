import global_config
from typing import List

debug_prints = True

class Generator:

    def __init__(self) -> None:
        # self.generator = None
        self.code: list = []
        self.tempList: list = []

    def get_used_temps(self) -> str:
        return ",".join([f"t{i}" for i in range(global_config.tmp_i)])

    def get_code(self) -> str:
        return "\n".join(self.code)

    def set_as_final_code(self) -> str:
        self.add_main_enclosure()
        self.add_tmps_on_top()
        self.add_headers_on_top()
        return "\n".join(self.code)

    def combine_with(self, gen):  # gen: Generator
        self.code = self.code + gen.code

    # tmp
    def new_temp(self) -> str:
        tmp = "t" + str(global_config.tmp_i)
        global_config.tmp_i += 1

        self.tempList.append(global_config.tmp_i)
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
                         f"P = 10;\n"
                         f"H = 15;\n"
                         f"{self.get_code()}\n"
                         f'printf("Final H:%f\\n", H);\n'
                         f'printf("Final P:%f\\n", P);\n'
                         f'printf("STACK:\\n[\\n");\n'
                         f'int i;\n'
                         
                         
                         f'for(i = 0; i < sizeof(STACK) / sizeof(double); i++){{\n'
                         f'printf("%i : %.2f\\n", i, STACK[i]);\n'
                         f'}}\n'
                         f'printf("]\\n");\n'
                         f'printf("HEAP:\\n[\\n");\n'
                         f'for(i = 0; i < sizeof(HEAP) / sizeof(double); i++){{\n'
                         f'printf("%i : %.2f\\n", i, HEAP[i]);\n'
                         f'}}\n'
                         f'printf("]\\n");\n'
                         
                         
                         
                         f"return 0;\n"
                         f"}}\n"]
            return

        self.code = [f"int main(){{\n"
                     f"{self.get_code()}\n"
                     f"return 0;\n"
                     f"}}"]

    # should be called after add_main_enclosure
    def add_tmps_on_top(self):
        if global_config.tmp_i > 0:
            self.code = [f"double {self.get_used_temps()};\n\n",
                         f"{self.get_code()}\n"]

    # should be called after add_tmps_on_top
    def add_headers_on_top(self):
        self.code = [f'#include <stdio.h>\n'
                     f'#include <math.h>\n'
                     f'double HEAP[40];\n'
                     f'double STACK[20];\n'
                     f'double P;\n'
                     f'double H;\n\n'
                     f'{self.get_code()}']

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
            self.code.append(f"{lbl}:")

    # var = val
    def add_expression(self, target: str, left: str, right: str, operator: str):
        self.code.append(f'{target} = {left} {operator} {right};')

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
        for char in msg:
            self.code.append(f"printf(\"%c\",{str(ord(char))});")

    # prints newline
    def add_newline(self):
        self.code.append('printf(\"%c\",10);')

    # H = H + 1
    def add_next_heap(self):
        self.code.append("H = H + 1;")

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

    def add_error_return(self, return_code: str):
        self.code.append(f"return {return_code};")

    def add_comment(self, msg):
        self.code.append(f"//{msg}")
