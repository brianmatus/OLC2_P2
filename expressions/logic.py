import errors.semantic_error
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from generator import Generator

from element_types.logic_type import LogicType
import global_config


class Logic(Expression):

    def __init__(self, left: Expression, right: Expression, logic_type: LogicType, line: int, column: int):
        super().__init__(line, column)
        self.left: Expression = left
        self.right: Expression = right
        self.logic_type = logic_type
        self.expression_type = ExpressionType.BOOL

    def execute(self, environment: Environment) -> ValueTuple:

        left = self.left.execute(environment)
        right = self.right.execute(environment)

        # print("----------------------------------------")
        # print("Logical")
        # print(left)
        # print(right)

        a = left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT
        a2 = left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.USIZE
        a3 = left.expression_type in [ExpressionType.INT, ExpressionType.USIZE] and \
            right.expression_type in [ExpressionType.INT, ExpressionType.USIZE]
        b = left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT
        c = left.expression_type == ExpressionType.STRING_PRIMITIVE \
            and right.expression_type == ExpressionType.STRING_PRIMITIVE

        c2 = left.expression_type == ExpressionType.STRING_CLASS \
            and right.expression_type == ExpressionType.STRING_CLASS
        d = left.expression_type == ExpressionType.BOOL and right.expression_type == ExpressionType.BOOL
        e = self.logic_type == LogicType.LOGIC_OR or self.logic_type == LogicType.LOGIC_AND \
            or self.logic_type == LogicType.LOGIC_NOT

        # Check int-float-string for relational, and only bool for logical
        if not (a or a2 or a3 or b or c or c2 or (d and e)):
            error_msg = f"Operación relacional invalida " \
                        f"({left.expression_type.name} -> {right.expression_type.name})." \
                        f"Las operaciones relacionales deben ser realizadas entre valores del mismo tipo entre solo " \
                        f"int,float o string. Las operaciones lógicas solo pueden ser de tipo bool"

            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

        match self.logic_type:
            case LogicType.OPE_MORE:
                generator = left.generator.combine_with(right.generator)
                true_label = generator.new_label()
                false_label = generator.new_label()

                if left.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    logical_str_compare(generator, true_label, false_label, left.value, right.value, ">")
                    return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                      [true_label], [false_label])

                generator.add_if(left.value, right.value, ">", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_LESS:
                generator = left.generator.combine_with(right.generator)
                true_label = generator.new_label()
                false_label = generator.new_label()

                if left.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    logical_str_compare(generator, true_label, false_label, left.value, right.value, "<")
                    return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                      [true_label], [false_label])

                generator.add_if(left.value, right.value, "<", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_MORE_EQUAL:
                generator = left.generator.combine_with(right.generator)
                true_label = generator.new_label()
                false_label = generator.new_label()

                if left.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    logical_str_compare(generator, true_label, false_label, left.value, right.value, ">=")
                    return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                      [true_label], [false_label])

                generator.add_if(left.value, right.value, ">=", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_LESS_EQUAL:
                generator = left.generator.combine_with(right.generator)
                true_label = generator.new_label()
                false_label = generator.new_label()

                if left.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    logical_str_compare(generator, true_label, false_label, left.value, right.value, "<=")
                    return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                      [true_label], [false_label])

                generator.add_if(left.value, right.value, "<=", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_EQUAL:
                generator = left.generator.combine_with(right.generator)
                true_label = generator.new_label()
                false_label = generator.new_label()

                if left.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    logical_str_compare(generator, true_label, false_label, left.value, right.value, "==")
                    return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                      [true_label], [false_label])

                generator.add_if(left.value, right.value, "==", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_NEQUAL:
                generator = left.generator.combine_with(right.generator)
                true_label = generator.new_label()
                false_label = generator.new_label()

                if left.expression_type in [ExpressionType.STRING_PRIMITIVE, ExpressionType.STRING_CLASS]:
                    logical_str_compare(generator, true_label, false_label, left.value, right.value, "!=")
                    return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                      [true_label], [false_label])

                generator.add_if(left.value, right.value, "!=", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            ###########################################################
            case LogicType.LOGIC_OR:
                generator = left.generator
                generator.add_label(left.false_label)
                generator.combine_with(right.generator)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  left.true_label + right.true_label, right.false_label)

            case LogicType.LOGIC_AND:
                generator = left.generator
                generator.add_label(left.true_label)
                generator.combine_with(right.generator)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  right.true_label, left.false_label + right.false_label)

            case LogicType.LOGIC_NOT:
                return ValueTuple(None, ExpressionType.BOOL, False, left.generator, ExpressionType.BOOL, None, False,
                                  left.false_label, left.true_label)
            case _:
                print("ERROR??? Unknown logic type?")

        print("POTENTIAL ERROR? UNEXPECTED Logic Execution")
        return ValueTuple(999999999999, ExpressionType.INT, is_mutable=False, content_type=None, capacity=None,
                          generator=None, is_tmp=True, true_label=["logic_error_f"], false_label=["logic_error_t"])


def logical_str_compare(generator: Generator, true_label: str, false_label: str, ptr1: str, ptr2: str, operation: str):
    generator.add_comment(f'Comparison of ptr::{ptr1} {operation} ptr::{ptr2}')
    t_ptr1 = generator.new_temp()
    t_value1 = generator.new_temp()
    t_ptr2 = generator.new_temp()
    t_value2 = generator.new_temp()

    l_loop = generator.new_label()
    l_2_greater = generator.new_label()
    l_not_eos_1 = generator.new_label()
    l_still_looping = generator.new_label()
    l_notequal = generator.new_label()
    l_1greater = generator.new_label()
    l_2greater = generator.new_label()

    generator.add_expression(t_ptr1, ptr1, "", "")
    generator.add_expression(t_ptr2, ptr2, "", "")

    generator.add_label([l_loop])
    generator.add_get_heap(t_value1, t_ptr1)
    generator.add_get_heap(t_value2, t_ptr2)

    generator.add_if(t_value1, "-1", "!=", l_not_eos_1)
    generator.add_if(t_value2, "-1", "!=", l_2greater)

    if operation in [">=", "<=", "=="]:
        generator.add_goto(true_label)
    else:
        generator.add_goto(false_label)

    generator.add_label([l_2_greater])
    if operation in ["<=", "<"]:
        generator.add_goto(true_label)
    else:
        generator.add_goto(false_label)

    generator.add_label([l_not_eos_1])
    generator.add_if(t_value2, "-1", "!=", l_still_looping)

    if operation in [">=", ">"]:
        generator.add_goto(true_label)
    else:
        generator.add_goto(false_label)

    generator.add_label([l_still_looping])
    generator.add_if(t_value1, t_value2, "!=", l_notequal)

    generator.add_expression(t_ptr1, t_ptr1, "1", "+")
    generator.add_expression(t_ptr2, t_ptr2, "1", "+")
    generator.add_goto(l_loop)

    generator.add_label([l_notequal])
    generator.add_if(t_value1, t_value2, ">", l_1greater)
    generator.add_goto(l_2greater)

    generator.add_label([l_1greater])
    if operation in [">=", ">"]:
        generator.add_goto(true_label)
    else:
        generator.add_goto(false_label)

    generator.add_label([l_2greater])
    if operation in ["<=", "<"]:
        generator.add_goto(true_label)
    else:
        generator.add_goto(false_label)

    generator.add_comment(f'End of Comparison')
