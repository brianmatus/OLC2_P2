from errors.semantic_error import SemanticError
import global_config
from abstract.instruction import Instruction
from returns.ast_return import ASTReturn
from returns.exec_return import ExecReturn
from element_types.element_type import ElementType
from elements.env import Environment
from abstract.expression import Expression
from elements.value_tuple import ValueTuple


class Declaration(Instruction):

    def __init__(self, _id: str, _type: ElementType, expression: Expression, is_mutable: bool, line: int, column: int):
        super().__init__(line, column)
        self._id = _id
        self._type: ElementType = _type
        self.expression: Expression = expression
        self.is_mutable = is_mutable

        # if self._type is None:
        #     print(f'Instance of declaration with id:{self._id} type:inferred')
        # else:
        #     print(f'Instance of declaration with id:{self._id} type:{self._type.name}')

    def execute(self, env: Environment) -> ExecReturn:
        # Declaration without assignment, using default values  (not possible? idk
        # if self.expression is None:
        #     match self._type:
        #         case ElementType.INT:
        #             env.save_variable(self._id, self._type, 0, self.line, self.column, False)
        #         case ElementType.FLOAT:
        #             env.save_variable(self._id, self._type, float(0.0), self.line, self.column, False)
        #         case ElementType.BOOL:
        #             env.save_variable(self._id, self._type, False, self.line, self.column, False)

        # Using not_init instead
        if self.expression is None:
            env.save_variable(self._id, self._type, None,
                              is_mutable=self.is_mutable, is_init=False, is_array=False,
                              line=self.line, column=self.column)

            return ExecReturn(ElementType.BOOL, True, False, False, False)

        expr: ValueTuple = self.expression.execute(env)
        # print(expr)

        # We have an impostor?
        if isinstance(expr.value, list):

            if expr._type == ElementType.ARRAY_EXPRESSION:

                # This should be and inferred array, so no normal declaration
                dimensions = global_config.extract_dimensions_to_dict(expr.value)
                tmp = expr
                while (tmp._type == ElementType.ARRAY_EXPRESSION):
                    tmp = tmp.value[0]
                the_type = tmp._type
                env.save_variable_array(self._id, the_type, dimensions, expr.value, False, True, self.line, self.column)
                return ExecReturn(ElementType.BOOL, True, False, False, False)

            if expr._type == ElementType.VECTOR:

                if len(expr.value) == 0:
                    error_msg = f"No se puede inferir el tipo de un vector vacio, debe especificar un tipo."
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                tmp = expr
                while (tmp._type == ElementType.VECTOR):
                    tmp = tmp.value[0]

                    if tmp._type == ElementType.ARRAY_EXPRESSION:
                        error_msg = f"No pueden combinarse expressiones array con vectores. " \
                                    f"No olvides vec! antes de [...]"
                        global_config.log_semantic_error(error_msg, self.line, self.column)
                        raise SemanticError(error_msg, self.line, self.column)



                deepness = global_config.get_vector_deepness(expr.value)

                match_deepness = global_config.match_vector_deepness(deepness, expr.value)
                if not match_deepness:
                    error_msg = f'La definición del vector no concuerda con la expresión dada (dimensiones)'
                    global_config.log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)

                from expressions.parameter_function_call import ParameterFunctionCallE
                from expressions.array_reference import ArrayReference

                if isinstance(self.expression, ParameterFunctionCallE):
                    env.save_variable_vector(self._id, ElementType.VECTOR, tmp._type, deepness, expr.value,
                                             self.is_mutable,
                                             len(expr.value), self.line, self.column)
                    return ExecReturn(ElementType.BOOL, True, False, False, False)

                if isinstance(self.expression, ArrayReference):
                    env.save_variable_vector(self._id, ElementType.VECTOR, tmp._type, deepness, expr.value,
                                             self.is_mutable,
                                             [len(expr.value)], self.line, self.column)
                    return ExecReturn(ElementType.BOOL, True, False, False, False)


                env.save_variable_vector(self._id, ElementType.VECTOR, tmp._type, deepness, expr.value, self.is_mutable,
                                         [self.expression.capacity.execute(env)], self.line, self.column)

                # FIXME This is "more correct"???
                # env.save_variable_vector(self._id, ElementType.VECTOR, tmp._type, deepness, expr.value, self.is_mutable,
                #                          self.expression.capacity, self.line, self.column)

                return ExecReturn(ElementType.BOOL, True, False, False, False)

            error_msg = f"UKNOWN TYPE: Expresion con valor tipo lista no reconocido (not array/vector)"
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)


        # Infer if not explicitly specified
        if self._type is None:
            self._type = expr._type

        # Check same type

        if expr._type == self._type:

            env.save_variable(self._id, self._type, expr.value,
                              is_mutable=self.is_mutable, is_init=True, is_array=False,
                              line=self.line, column=self.column)

            return ExecReturn(ElementType.BOOL, True, False, False, False)

        # Exceptions of same type:

        # char var_type with str expr_type
        if self._type == ElementType.CHAR and expr._type == ElementType.STRING_PRIMITIVE:
            env.save_variable(self._id, self._type, expr.value,
                              is_mutable=self.is_mutable, is_init=True, is_array=False,
                              line=self.line, column=self.column)

            return ExecReturn(ElementType.BOOL, True, False, False, False)


        # usize var_type with int expr_type


        if self._type == ElementType.USIZE and expr._type == ElementType.INT:

            if global_config.is_arithmetic_pure_literals(self.expression):
                # if expr.value < 0:
                #     error_msg = f"USIZE UNDERFLOW: Valores usize deben ser positivos."
                #     global_config.log_semantic_error(error_msg, self.line, self.column)
                #     raise errors.semantic_error.SemanticError(error_msg, self.line, self.column)
                env.save_variable(self._id, self._type, expr.value,
                                  is_mutable=self.is_mutable, is_init=True, is_array=False,
                                  line=self.line, column=self.column)

                return ExecReturn(ElementType.BOOL, True, False, False, False)





        # Error:
        error_msg = f'Asignacion de tipo {expr._type.name} a variable <{self._id}> de tipo {self._type.name}'
        global_config.log_semantic_error(error_msg, self.line, self.column)
        raise SemanticError(error_msg, self.line, self.column)

    def ast(self) -> ASTReturn:
        father_ref = global_config.get_unique_number()
        id_ref = global_config.get_unique_number()
        the_type: str
        if self._type is None:
            the_type = "Inferred"
        else:
            the_type = self._type.name

        result: str = f'{father_ref}[label="DECLARATION\\n{the_type}"]\n' \
                      f'{id_ref}[label={self._id}]\n' \
                      f'{father_ref} -> {id_ref}\n'

        if self.expression is None:
            return ASTReturn(result, father_ref)

        expr_ast = self.expression.ast()
        result += f'{expr_ast.value}\n' \
                  f'{father_ref} -> {expr_ast.head_ref}\n'
        return ASTReturn(result, father_ref)
