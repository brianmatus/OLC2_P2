import errors.semantic_error
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from returns.ast_return import ASTReturn

from element_types.logic_type import LogicType
import global_config


class Logic(Expression):

    # Should implement ternary???

    def __init__(self, left: Expression, right: Expression, _type: LogicType, line: int, column: int):
        super().__init__(line, column)
        self.left: Expression = left
        self.right: Expression = right
        self._type = _type

    def execute(self, environment: Environment) -> ValueTuple:
        error_msg = ""



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
        e = self._type == LogicType.LOGIC_OR or self._type == LogicType.LOGIC_AND or self._type == LogicType.LOGIC_NOT

        #Check int-float-string for relational, and only bool for logical
        if not (a or a2 or a3 or b or c or (d and e)):
            error_msg = f"Operación relacional invalida ({left.expression_type.name} -> {right.expression_type.name})." \
                        f"Las operaciones relacionales deben ser realizadas entre valores del mismo tipo entre solo " \
                        f"int,float o string. Las operaciones lógicas solo pueden ser de tipo bool"

            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

        match self._type:
            case LogicType.OPE_MORE:

                if left.value > right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            case LogicType.OPE_LESS:

                if left.value < right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            case LogicType.OPE_MORE_EQUAL:

                if left.value >= right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            case LogicType.OPE_LESS_EQUAL:

                if left.value <= right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            case LogicType.OPE_EQUAL:
                if left.value == right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            case LogicType.OPE_NEQUAL:
                if left.value != right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            case LogicType.OPE_NEQUAL:
                if left.value != right.value:
                    return ValueTuple(True, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
                else:
                    return ValueTuple(False, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)

            ###########################################################
            case LogicType.LOGIC_OR:
                return ValueTuple(left.value or right.value, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
            case LogicType.LOGIC_AND:
                return ValueTuple(left.value and right.value, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
            case LogicType.LOGIC_NOT:
                return ValueTuple(not left.value, ExpressionType.BOOL, is_mutable=False, content_type=None, capacity=None)
            case _:
                print("ERROR??? Unknown logic type?")

        print("POTENTIAL ERROR? UNEXPECTED Logic Execution")
        return ValueTuple(999999999999, ExpressionType.INT, is_mutable=False, content_type=None, capacity=None)

    def ast(self) -> ASTReturn:
        if self._type == LogicType.LOGIC_NOT:
            return self.singular_operation_ast()
        # Here should go ternary check if implemented
        return self.two_operation_ast()

    def singular_operation_ast(self) -> ASTReturn:
        father_index = global_config.get_unique_number()
        left_ast = self.left.ast()
        result = f'{father_index}[label="LOGIC {self._type.name}"]\n' \
                 f'{left_ast.value}\n' \
                 f'{father_index} ->{left_ast.head_ref}\n'
        return ASTReturn(value=result, head_ref=father_index)

    def two_operation_ast(self) -> ASTReturn:
        father_index = global_config.get_unique_number()
        left_ast = self.left.ast()
        right_ast = self.right.ast()
        result = f'{father_index}[label="LOGIC {self._type.name}"]\n' \
                 f'{left_ast.value}\n' \
                 f'{father_index} ->{left_ast.head_ref}\n' \
                 f'{right_ast.value}\n' \
                 f'{father_index} ->{right_ast.head_ref}\n'
        return ASTReturn(value=result, head_ref=father_index)

