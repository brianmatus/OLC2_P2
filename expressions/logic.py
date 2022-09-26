import errors.semantic_error
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from returns.ast_return import ASTReturn
from generator import Generator

from element_types.logic_type import LogicType
import global_config


class Logic(Expression):

    # TODO add correct code for string comparison. Leaving as it is will only compare first char

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
        a3 = left.expression_type in [ExpressionType.INT, ExpressionType.USIZE] and right.expression_type in [ExpressionType.INT, ExpressionType.USIZE]
        b = left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT
        c = left.expression_type == ExpressionType.STRING_PRIMITIVE and right.expression_type == ExpressionType.STRING_PRIMITIVE
        d = left.expression_type == ExpressionType.BOOL and right.expression_type == ExpressionType.BOOL
        e = self.logic_type == LogicType.LOGIC_OR or self.logic_type == LogicType.LOGIC_AND or self.logic_type == LogicType.LOGIC_NOT

        # Check int-float-string for relational, and only bool for logical
        if not (a or a2 or a3 or b or c or (d and e)):
            error_msg = f"Operación relacional invalida " \
                        f"({left.expression_type.name} -> {right.expression_type.name})." \
                        f"Las operaciones relacionales deben ser realizadas entre valores del mismo tipo entre solo " \
                        f"int,float o string. Las operaciones lógicas solo pueden ser de tipo bool"

            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

        match self.logic_type:
            case LogicType.OPE_MORE:

                generator = Generator()
                generator.code = left.generator.code + right.generator.code
                true_label = generator.new_label()
                false_label = generator.new_label()
                generator.add_if(left.value, right.value, ">", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_LESS:

                generator = Generator()
                generator.code = left.generator.code + right.generator.code
                true_label = generator.new_label()
                false_label = generator.new_label()
                generator.add_if(left.value, right.value, "<", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_MORE_EQUAL:
                generator = Generator()
                generator.code = left.generator.code + right.generator.code
                true_label = generator.new_label()
                false_label = generator.new_label()
                generator.add_if(left.value, right.value, ">=", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_LESS_EQUAL:

                generator = Generator()
                generator.code = left.generator.code + right.generator.code
                true_label = generator.new_label()
                false_label = generator.new_label()
                generator.add_if(left.value, right.value, "<=", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_EQUAL:
                generator = Generator()
                generator.code = left.generator.code + right.generator.code
                true_label = generator.new_label()
                false_label = generator.new_label()
                generator.add_if(left.value, right.value, "==", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])

            case LogicType.OPE_NEQUAL:
                generator = Generator()
                generator.code = left.generator.code + right.generator.code
                true_label = generator.new_label()
                false_label = generator.new_label()
                generator.add_if(left.value, right.value, ">", true_label)
                generator.add_goto(false_label)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  [true_label], [false_label])


            ###########################################################
            case LogicType.LOGIC_OR:
                generator = Generator()
                generator.code = left.generator.code
                generator.add_label(left.false_label)
                generator.combine_with(right.generator)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  left.true_label + right.true_label, right.false_label)

            case LogicType.LOGIC_AND:
                generator = Generator()
                generator.code = left.generator.code
                generator.add_label(left.true_label)
                generator.combine_with(right.generator)
                return ValueTuple(None, ExpressionType.BOOL, False, generator, ExpressionType.BOOL, None, False,
                                  right.true_label, left.false_label + right.false_label)

            case LogicType.LOGIC_NOT:
                # left.generator.add_goto(left.false_label[0])  #FIXME idk?
                return ValueTuple(None, ExpressionType.BOOL, False, left.generator, ExpressionType.BOOL, None, False,
                                  left.false_label, left.true_label)
            case _:
                print("ERROR??? Unknown logic type?")

        print("POTENTIAL ERROR? UNEXPECTED Logic Execution")
        return ValueTuple(999999999999, ExpressionType.INT, is_mutable=False, content_type=None, capacity=None
                          ,generator=None, is_tmp=True)
