from typing import Tuple
class Generator:

    def __init__(self) -> None:
        # self.generator = None
        self.tmp: int = 0
        self.label: int = 0
        self.code: list = []
        self.tempList: list = []

    def get_used_temps(self) -> str:
        return ",".join(self.tempList)

    def get_code(self) -> str:
        return "\n".join(self.code)

    def get_final_code(self) -> str:

        self.add_main_enclosure()
        self.add_headers_on_top()
        self.add_tmps_on_top()
        return "\n".join(self.code)

    # tmp
    def new_temp(self) -> str:
        tmp = "t" + str(self.tmp)
        self.tmp = self.tmp + 1

        self.tempList.append(tmp)
        return tmp

    # Label
    def new_label(self) -> str:
        tmp = self.label
        self.label = self.label + 1
        return "L" + str(tmp)

##############################################################

    def add_main_enclosure(self):
        if len(self.tempList) > 0:
            self.code = f"void main(){{\n" \
                        f"{self.code}\n" \
                        f"return 0;\n" \
                        f"}}"

    # should be called after add_main_enclosure
    def add_tmps_on_top(self):
        if len(self.tempList) > 0:
            self.code = f"double {self.get_used_temps()};\n\n" \
                        f"{self.code}\n"

    # should be called after add_tmps_on_top
    def add_headers_on_top(self):
        self.code = f'#include <stdio.h>\n' \
                    f'#include <math.h>\n' \
                    f'double HEAP[1000];\n' \
                    f'double STACK[78000];\n' \
                    f'double P;\n' \
                    f'double H;\n\n' \
                    f'{self.code}'

    # foo()
    def add_call_func(self, name: str):
        self.code.append(name + "();")

    # label
    def add_label(self, label: str):
        self.code.append(label + ":")

    # var = val
    def add_expression(self, target: str, left: str, right: str, operator: str):
        self.code.append(target + " = " + left + " " + operator + " " + right + ";")

    # if
    def add_if(self, left: str, right: str, operator: str, label: str):
        self.code.append("if(" + left + " " + operator + " " + right + ") goto " + label + ";")

    # goto
    def add_goto(self, label: str):
        self.code.append("goto " + label + ";")

    # printf(...)
    def add_printf(self, typePrint: str, value: str):
        self.code.append("printf(\"%" + typePrint + "\"," + value + ");")

    # prints newline
    def add_newline(self):
        self.code.append('printf(\"%c\",10);')

    # H = H + 1
    def add_next_heap(self):
        self.code.append("H = H + 1;")

    # P = P + i
    def add_next_stack(self, index: str):
        self.code.append("P = P + " + index + ";")

    # P = P - i
    def add_back_stack(self, index: str):
        self.code.append("P = P - " + index + ";")

    # heap[i]
    def add_get_heap(self, target: str, index: str):
        self.code.append(target + " = HEAP[(int)" + index + " ];")

    # heap[i] = val
    def add_set_heap(self, index: str, value: str):
        self.code.append("HEAP[(int)" + index + "] = " + value + ";")

    # stack[i]
    def add_get_stack(self, target: str, index: str):
        self.code.append(target + " = STACK[(int)" + index + "];")

    # heap[i] = val
    def add_set_stack(self, index: str, value: str):
        self.code.append("STACK[(int)" + index + "] = " + value + ";")
