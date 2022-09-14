from typing import List, Union

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.element_type import ElementType
from elements.env import Environment
from abstract.expression import Expression
from expressions.literal import Literal
from elements.value_tuple import ValueTuple

from global_config import log_semantic_error
from errors.semantic_error import SemanticError


class ForInRanged:
    def __init__(self, a: Expression, b: Expression):
        self.a: Expression = a
        self.b: Expression = b


class ForInI(Instruction):
    def __init__(self, looper: str, range_expr: Union[Expression, ForInRanged], instructions: List[Instruction],
                 line: int, column: int):
        super().__init__(line, column)
        self.looper: str = looper
        self.instructions: List[Instruction] = instructions
        self.range_expr: Union[Expression, ForInRanged] = range_expr
        self.environment = Environment(None)  # default, for compiler to recognize it
        self.intermediate_env = Environment(None)

    def execute(self, env: Environment) -> ExecReturn:

        # print("executing for in")

        env.remove_child(self.intermediate_env)
        self.intermediate_env = Environment(env)
        env.children_environment.append(self.environment)

        elements = None
        the_type = None

        # Check range (before looper to determine type

        if isinstance(self.range_expr, ForInRanged):
            a = self.range_expr.a.execute(env)
            b = self.range_expr.b.execute(env)

            if a._type not in [ElementType.INT, ElementType.USIZE] \
                    or b._type not in [ElementType.INT, ElementType.USIZE]:
                error_msg = f"Un rango definido por a..b debe de ser tipo int o usize"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            if a.value > b.value:
                error_msg = f"Rango invalido. El numero de la izquierda no puede ser mayor al de la derecha"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            elements = [Literal(v, ElementType.INT, self.line, self.column) for v in range(a.value, b.value)]
            the_type = ElementType.INT

        # TODO check if its vector
        # elif vector:

        else:
            r = self.range_expr.execute(env)

            if not isinstance(r.value, list):
                error_msg = f"Una expression para for-in debe ser array o vector"
                log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            elements = r.value

            tmp = r
            while (tmp._type == ElementType.ARRAY_EXPRESSION):
                tmp = tmp.value[0]

            the_type = tmp._type

        pass
        #TODO mark error  if either elements or the_type is None?? idk

        # print(elements)
        # print(the_type)

        element: ValueTuple
        for element in elements:

            self.intermediate_env.remove_child(self.environment)
            self.environment = Environment(self.intermediate_env)
            self.intermediate_env.children_environment.append(self.environment)

            if isinstance(element.value, list):
                # print("needs declarement as array")

                self.environment.save_variable_array(self.looper, the_type,
                                                     global_config.extract_dimensions_to_dict(element.value),
                                                     element.value, False, True, self.line, self.column)
            # elif instance vector
            # elif instance struct
            else:
                # print("needs normal symbol")
                self.environment.save_variable(self.looper, the_type, element.value, False, True, True,
                                               self.line, self.column)

            needs_break = False
            instruction: Instruction
            for instruction in self.instructions:

                result = instruction.execute(self.environment)
                if result.propagate_method_return:
                    return result

                if result.propagate_break:
                    needs_break = True
                    break

                if result.propagate_continue:
                    break

            else:
                # Continue if the inner loop wasn't broken.
                continue
            # Inner loop was broken, break the outer.
            if needs_break:
                break
            # continue

        return ExecReturn(ElementType.BOOL, False, False, False, False)
