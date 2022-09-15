import errors.semantic_error
from abstract.expression import Expression
from elements.c_env import Environment
from elements.value_tuple import ValueTuple
from element_types.c_expression_type import ExpressionType
from returns.ast_return import ASTReturn
from element_types.arithmetic_type import ArithmeticType
import math

import global_config


class Arithmetic(Expression):

    def __init__(self, left: Expression, right: Expression, _type: ArithmeticType, line: int, column: int):
        super().__init__(line, column)
        self.left = left
        self.right = right
        self._type = _type
        self.content_type = None

    def __str__(self):
        return f'Arithmetic({self.left}, {self._type.name}, {self.right}'

    def execute(self, environment: Environment) -> ValueTuple:

        error_msj: str = ""
        left: ValueTuple = self.left.execute(environment)
        right: ValueTuple = self.right.execute(environment)

        self.content_type = left.content_type

        match self._type:

            case ArithmeticType.POW_INT:

                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    return ValueTuple(value=math.pow(left.value, right.value), expression_type=ExpressionType.INT, is_mutable=False,
                                      content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica POW {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.POW_FLOAT:

                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=math.pow(left.value, right.value), expression_type=ExpressionType.FLOAT,
                                      is_mutable=False, content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica POWF {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.SUM:

                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    return ValueTuple(value=left.value + right.value, expression_type=ExpressionType.INT, is_mutable=False,
                                      content_type=None, capacity=None)

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        # if left.value + right.value < 0:
                        #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                        #     global_config.log_semantic_error(error_msg, self.line, self.column)
                        #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                        return ValueTuple(value=left.value + right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        # if left.value + right.value < 0:
                        #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                        #     global_config.log_semantic_error(error_msg, self.line, self.column)
                        #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                        return ValueTuple(value=left.value + right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=left.value + right.value, expression_type=ExpressionType.FLOAT, is_mutable=False,
                                      content_type=None, capacity=None)

                # &str + String
                if left.expression_type == ExpressionType.STRING_PRIMITIVE and right.expression_type == ExpressionType.STRING_CLASS:
                    return ValueTuple(value=left.value + right.value, expression_type=ExpressionType.STRING_CLASS, is_mutable=False,
                                      content_type=None, capacity=None)

                # String + &str
                if left.expression_type == ExpressionType.STRING_CLASS and right.expression_type == ExpressionType.STRING_PRIMITIVE:
                    return ValueTuple(value=left.value + right.value, expression_type=ExpressionType.STRING_CLASS, is_mutable=False,
                                      content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica SUMA {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.SUB:
                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    return ValueTuple(value=left.value - right.value, expression_type=ExpressionType.INT, is_mutable=False,
                                      content_type=None, capacity=None)
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=left.value - right.value, expression_type=ExpressionType.FLOAT, is_mutable=False,
                                      content_type=None, capacity=None)

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        # TODO Should usize be measured for undersize?
                        # if left.value - right.value < 0:
                        #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos." \
                        #                 f"({left.value - right.value})"
                        #     global_config.log_semantic_error(error_msg, self.line, self.column)
                        #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                        return ValueTuple(value=left.value - right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        # if left.value - right.value < 0:
                        #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                        #     global_config.log_semantic_error(error_msg, self.line, self.column)
                        #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                        return ValueTuple(value=left.value - right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica RESTA {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.MULT:
                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    return ValueTuple(value=left.value * right.value, expression_type=ExpressionType.INT, is_mutable=False,
                                      content_type=None, capacity=None)
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=left.value * right.value, expression_type=ExpressionType.FLOAT, is_mutable=False,
                                      content_type=None, capacity=None)

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        # if left.value * right.value < 0:
                        #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                        #     global_config.log_semantic_error(error_msg, self.line, self.column)
                        #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                        return ValueTuple(value=left.value * right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        # if left.value + right.value < 0:
                        #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                        #     global_config.log_semantic_error(error_msg, self.line, self.column)
                        #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                        return ValueTuple(value=left.value * right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica MULTIPLICACION {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.DIV:


                if right.value == 0:
                    error_msg = f"Operacion Aritmetica DIV no puede ser divisor 0."
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    return ValueTuple(value=left.value / right.value, expression_type=ExpressionType.FLOAT, is_mutable=False,
                                      content_type=None, capacity=None)
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=left.value / right.value, expression_type=ExpressionType.FLOAT, is_mutable=False,
                                      content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica DIVISION {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.MOD:
                # INT
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.INT:
                    return ValueTuple(value=left.value % right.value, expression_type=ExpressionType.INT, is_mutable=False,
                                      content_type=None, capacity=None)
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT and right.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=left.value % right.value, expression_type=ExpressionType.FLOAT, is_mutable=False,
                                      content_type=None, capacity=None)

                # USIZE INT(literals)
                if left.expression_type == ExpressionType.USIZE and right.expression_type == ExpressionType.INT:
                    if global_config.is_arithmetic_pure_literals(self.right):
                        return ValueTuple(value=left.value % right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                # INT(literals) USIZE
                if left.expression_type == ExpressionType.INT and right.expression_type == ExpressionType.USIZE:
                    if global_config.is_arithmetic_pure_literals(self.left):
                        return ValueTuple(value=left.value % right.value, expression_type=ExpressionType.USIZE, is_mutable=False,
                                          content_type=None, capacity=None)

                error_msg = f"Operacion Aritmetica MODULAR {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case ArithmeticType.NEG:

                # INT
                if left.expression_type == ExpressionType.INT:
                    return ValueTuple(value=0-left.value, expression_type=ExpressionType.INT, is_mutable=False, content_type=None,
                                      capacity=None)
                # FLOAT
                if left.expression_type == ExpressionType.FLOAT:
                    return ValueTuple(value=0-left.value, expression_type=ExpressionType.FLOAT, is_mutable=False, content_type=None,
                                      capacity=None)

                error_msg = f"Operacion Aritmetica MODULAR {left.expression_type.name} <-> {right.expression_type.name} es invalida."
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)

            case _:
                print("ERROR??? Unknown arithmetic type?")

    def ast(self) -> ASTReturn:

        if self._type == ArithmeticType.NEG:
            return self.singular_operation_ast()
        return self.two_operation_ast()

    def singular_operation_ast(self) -> ASTReturn:
        father_index: int = global_config.get_unique_number()
        left_ast = self.left.ast()
        result = f'{father_index}[label="ARITHMETIC {self._type.name}"]\n' \
                 f'{left_ast.value}\n' \
                 f'{father_index} -> {left_ast.head_ref}\n'
        return ASTReturn(result, father_index)

    def two_operation_ast(self) -> ASTReturn:
        father_index: int = global_config.get_unique_number()
        left_ast = self.left.ast()
        right_ast = self.right.ast()
        result = f'{father_index}[label="ARITHMETIC {self._type.name}"]\n' \
                 f'{left_ast.value}\n' \
                 f'{father_index} -> {left_ast.head_ref}\n' \
                 f'{right_ast.value}\n' \
                 f'{father_index} -> {right_ast.head_ref}\n'
        return ASTReturn(result, father_index)
