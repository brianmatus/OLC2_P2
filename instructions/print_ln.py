from typing import List


from errors.semantic_error import SemanticError
import global_config
from abstract.instruction import Instruction
from returns.ast_return import ASTReturn
from returns.exec_return import ExecReturn
from element_types.element_type import ElementType
from elements.env import Environment
from abstract.expression import Expression
from expressions.literal import Literal
from elements.value_tuple import ValueTuple


class PrintLN(Instruction):

    def __init__(self, expr_list, has_ln: bool, line: int, column: int):
        super().__init__(line, column)
        self.expr_list: List[Expression] = expr_list
        self.has_ln: bool = has_ln

    def execute(self, env: Environment) -> ExecReturn:

        if self.expr_list[0]._type is not ElementType.STRING_PRIMITIVE:
            print("println formatter is not string_primitive")
            error_msg = f'El primer argumento de println debería ser un string primitivo'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        _str: Literal = self.expr_list[0]

        needed = _str.value.count("{}") + _str.value.count("{:?}")

        if needed != len(self.expr_list[1:]):
            error_msg = f'La cantidad de elementos de formato y argumentos obtenidos no es la misma'
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        the_str: str = _str.value

        # r = the_str.find("\\n")
        # the_str.replace("\\n", "\n")

        for arg in self.expr_list[1:]:
            # print("titan")
            # print(arg)
            the_arg = arg.execute(env)

            # print(the_arg)

            i1 = the_str.find("{}")  # -1
            i2 = the_str.find("{:?}")  # 4
            next_is_simple = ((i1 < i2) or (i2 == -1)) and (i1 != -1)
            # print(next_is_simple)

            # Arrays
            if isinstance(the_arg.value, list):

                # print("change for array")
                if next_is_simple:
                    error_msg = f'{{}} fue dado para una variable que es array/vector'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                if the_arg._type == ElementType.VECTOR:
                    the_str = the_str.replace("{:?}", str(global_config.value_tuple_vector_to_array(the_arg.value)), 1)
                    continue

                the_str = the_str.replace("{:?}", str(global_config.value_tuple_array_to_array(the_arg.value)), 1)
                continue

            allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
                             ElementType.BOOL, ElementType.CHAR,
                             ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]

            if the_arg._type not in allowed_types:
                error_msg = f'El tipo {the_arg._type.name} debe ser casteado para usar en print.'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            if not next_is_simple:
                error_msg = f'{{:?}} fue dado para una variable que no es array'
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            the_str = the_str.replace("{}", str(the_arg.value), 1)
            continue

        global_config.console_output += the_str

        if self.has_ln:
            global_config.console_output += "\n"

        return ExecReturn(ElementType.BOOL, True, False, False, False)

    def ast(self) -> ASTReturn:
        pass
