import errors.semantic_error
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType

from element_types.logic_type import LogicType
import global_config


class TypeCasting(Expression):

    def __init__(self, cast_to: ExpressionType, expr: Expression, line: int, column: int):
        super().__init__(line, column)
        self.cast_to: ExpressionType = cast_to
        self.expr: Expression = expr

    def execute(self, environment: Environment) -> ValueTuple:
        res = self.expr.execute(environment)

        # Same Types
        if res.expression_type == self.cast_to:
            return res

        ##################################################
        # INT TO USIZE
        if res.expression_type == ExpressionType.INT and self.cast_to == ExpressionType.USIZE:
            res.expression_type = ExpressionType.USIZE
            return res

        # USIZE TO INT
        if res.expression_type == ExpressionType.USIZE and self.cast_to == ExpressionType.INT:
            res.expression_type = ExpressionType.INT
            return res

        # INT TO FLOAT
        if res.expression_type == ExpressionType.INT and self.cast_to == ExpressionType.FLOAT:
            res.expression_type = ExpressionType.FLOAT
            return res
        # FLOAT TO INT
        if res.expression_type == ExpressionType.FLOAT and self.cast_to == ExpressionType.INT:
            t = res.generator.new_temp()
            res.generator.add_casting(target=t, to_be_casted=res.value, cast_to="int")
            return ValueTuple(value=t, expression_type=ExpressionType.INT, is_mutable=False, generator=res.generator,
                              content_type=ExpressionType.INT, capacity=None, is_tmp=True,
                              true_label=res.true_label, false_label=res.false_label)

        # INT TO BOOL, INVALID, use != 0
        # BOOL TO INT
        if res.expression_type == ExpressionType.BOOL and self.cast_to == ExpressionType.INT:
            t = res.generator.new_temp()
            res.generator.add_label(res.true_label)
            res.generator.add_expression(t, "1", "", "")
            res.generator.add_label(res.false_label)
            res.generator.add_expression(t, "0", "", "")
            return ValueTuple(value=t, expression_type=ExpressionType.INT, is_mutable=False, generator=res.generator,
                              content_type=ExpressionType.INT, capacity=None, is_tmp=True,
                              true_label=res.true_label, false_label=res.false_label)

        # INT TO CHAR
        if res.expression_type == ExpressionType.INT and self.cast_to == ExpressionType.CHAR:
            res.expression_type = ExpressionType.CHAR
            return res
        # CHAR TO INT
        if res.expression_type == ExpressionType.CHAR and self.cast_to == ExpressionType.INT:
            res.expression_type = ExpressionType.INT
            return res

        # INT TO STRING INVALID, should be done with .to_string()
        # STRING TO INT  INVALID, always invalid? idk

        ##################################################
        # USIZE TO FLOAT
        if res.expression_type == ExpressionType.USIZE and self.cast_to == ExpressionType.FLOAT:
            res.expression_type = ExpressionType.FLOAT
            return res
        # FLOAT TO USIZE INVALID, cast to i64 before

        # USIZE TO BOOL INVALID, use != 0
        # BOOL TO USIZE
        if res.expression_type == ExpressionType.BOOL and self.cast_to == ExpressionType.USIZE:
            t = res.generator.new_temp()
            res.generator.add_label(res.true_label)
            res.generator.add_expression(t, "1", "", "")
            res.generator.add_label(res.false_label)
            res.generator.add_expression(t, "0", "", "")
            return ValueTuple(value=t, expression_type=ExpressionType.USIZE, is_mutable=False, generator=res.generator,
                              content_type=ExpressionType.USIZE, capacity=None, is_tmp=True,
                              true_label=res.true_label, false_label=res.false_label)

        # USIZE TO CHAR INVALID
        # CHAR TO USIZE
        if res.expression_type == ExpressionType.CHAR and self.cast_to == ExpressionType.USIZE:
            res.expression_type = ExpressionType.USIZE
            return res

        ##################################################

        # FLOAT TO BOOL INVALID, use != 0
        # BOOL TO FLOAT INVALID, cast to i64 before

        # FLOAT TO CHAR INVALID
        # CHAR TO FLOAT INVALID, cast to i64 before

        ##################################################

        # BOOL TO CHAR INVALID
        # CHAR TO BOOL INVALID




