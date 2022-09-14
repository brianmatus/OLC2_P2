import math
from typing import List, Union

import global_config
from errors.semantic_error import SemanticError
from element_types.func_call_arg import FuncCallArg
from abstract.expression import Expression
from elements.env import Environment
from elements.value_tuple import ValueTuple
from element_types.element_type import ElementType
from elements.symbol import Symbol
from elements.array_symbol import ArraySymbol
from elements.vector_symbol import VectorSymbol
from expressions.array_reference import ArrayReference
from expressions.variable_ref import VariableReference
from expressions.literal import Literal
from expressions.type_casting import TypeCasting
import copy

from element_types.logic_type import LogicType
from global_config import log_semantic_error


class ParameterFunctionCallE(Expression):

    def __init__(self, variable_id: Union[Expression, str], function_id: str, params: List[FuncCallArg], line: int, column: int):
        super().__init__(line, column)

        self.variable_id = variable_id
        self.function_id = function_id
        self.params = params


    def execute(self, environment: Environment) -> ValueTuple:

        # print("-------------------param func call-------------------")
        # print(self.variable_id)
        # print(self.function_id)
        # print(self.params)

        # print(self.variable_id)
        # print(type(self.variable_id))

        the_symbol = None

        if isinstance(self.variable_id, ArrayReference):

            # print("array reference!")
            result = self.variable_id.execute(environment)

            if isinstance(result.value, list):
                the_symbol = ArraySymbol(self.variable_id._id, result._type, self.variable_id.indexes, result.value,
                                         True, False)

            else:
                the_symbol = Symbol(self.variable_id._id, result._type, result.value, True, False)

        elif isinstance(self.variable_id, VariableReference):
            the_symbol = environment.recursive_get(self.variable_id._id)

        elif isinstance(self.variable_id, Literal):
            if self.function_id == "to_string":
                r = self.variable_id.execute(environment)
                return ValueTuple(str(r.value), ElementType.STRING_CLASS, False, None, None)

        elif isinstance(self.variable_id, TypeCasting):
            r = self.variable_id.execute(environment)
            the_symbol = Symbol("type_casting_forced_symbol", r._type, r.value, True, False)

        elif isinstance(self.variable_id, ParameterFunctionCallE):
            # FIXME check resulting function type
            if self.function_id == "to_string":
                r = self.variable_id.execute(environment)
                return ValueTuple(str(r.value), ElementType.STRING_CLASS, False, None, None)


        else:
            the_symbol = environment.recursive_get(self.variable_id)

        if the_symbol is None:
            error_msg = f"No existe una variable con el nombre {self.variable_id}"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if isinstance(the_symbol, Symbol):

            # Built in functions
            if self.function_id == "to_string":
                return self.native_to_string(the_symbol)

            if self.function_id == "abs":
                return self.native_abs(the_symbol)

            if self.function_id == "sqrt":
                return self.native_sqrt(the_symbol)

            if self.function_id == "clone":
                return self.native_clone(the_symbol)

        if isinstance(the_symbol, ArraySymbol):
            if self.function_id == "to_string":
                return self.native_to_string(the_symbol)

            if self.function_id == "len":
                return self.native_len(the_symbol)

            if self.function_id == "clone":
                return self.native_array_clone(the_symbol)

        if isinstance(the_symbol, VectorSymbol):

            match self.function_id:

                case "push":
                    return self.native_vec_push(the_symbol, environment)
                case "insert":
                    return self.native_vec_insert(the_symbol, environment)
                case "remove":
                    return self.native_vec_remove(the_symbol, environment)
                case "len":
                    return self.native_vec_len(the_symbol)
                case "capacity":
                    return self.native_vec_capacity(the_symbol)
                case "contains":
                    return self.native_vec_contains(the_symbol, environment)
                case _:
                    error_msg = f"No existe el método <{self.function_id}> en tipo Vec"
                    log_semantic_error(error_msg, self.line, self.column)
                    raise SemanticError(error_msg, self.line, self.column)


        # TODO Check if is struct
        # if if isinstance(the_symbol, struct_symbol):

        # TODO Check if present in struct
        print("missing stuff")
        error_msg = f"Acceso a parametro de variable invalido.."
        log_semantic_error(error_msg, self.line, self.column)
        raise SemanticError(error_msg, self.line, self.column)

    def native_to_string(self, the_symbol) -> ValueTuple:
        allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
                         ElementType.BOOL, ElementType.CHAR,
                         ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]
        if not the_symbol._type in allowed_types:
            error_msg = f".to_string() solo puede ser usado con i64, usize, f64, bool, char, String, &str."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(str(the_symbol.value), ElementType.STRING_CLASS, False)

    def native_abs(self, the_symbol) -> ValueTuple:
        allowed_types = [ElementType.INT, ElementType.FLOAT]
        if not the_symbol._type in allowed_types:
            error_msg = f".native_abs() solo puede ser usado con i64, f64."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(abs(the_symbol.value), the_symbol._type, False, None, None)

    def native_sqrt(self, the_symbol) -> ValueTuple:
        allowed_types = [ElementType.INT, ElementType.FLOAT]
        if not the_symbol._type in allowed_types:
            error_msg = f".native_sqrt() solo puede ser usado con i64, f64."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(math.sqrt(the_symbol.value), ElementType.FLOAT, False, None, None)

    def native_clone(self, the_symbol) -> ValueTuple:
        allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
                         ElementType.BOOL, ElementType.CHAR,
                         ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]
        if not the_symbol._type in allowed_types:
            error_msg = f".native_sqrt() solo puede ser usado i64, usize, f64, bool, char, String, &str."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(the_symbol.value, the_symbol._type, False, None, None)

    def native_array_clone(self, the_symbol) -> ValueTuple:
        allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
                         ElementType.BOOL, ElementType.CHAR,
                         ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS]
        if not the_symbol._type in allowed_types:
            error_msg = f".native_sqrt() solo puede ser usado i64, usize, f64, bool, char, String, &str."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(copy.deepcopy(the_symbol.value), the_symbol._type, False, None, None)

    def native_len(self, the_symbol) -> ValueTuple:
        allowed_types = [ElementType.INT, ElementType.USIZE, ElementType.FLOAT,
                         ElementType.BOOL, ElementType.CHAR,
                         ElementType.STRING_PRIMITIVE, ElementType.STRING_CLASS, ElementType.VECTOR]
        if not the_symbol._type in allowed_types:
            error_msg = f".len() solo puede ser usado con i64, usize, f64, bool, char, String, &str."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if isinstance(the_symbol, VectorSymbol):
            return ValueTuple(len(the_symbol.value), ElementType.INT, False, the_symbol.content_type,
                              the_symbol.capacity)

        return ValueTuple(len(the_symbol.value), ElementType.INT, False, None, None)

    def native_vec_push(self, the_symbol, environment) -> ValueTuple:

        if not the_symbol.is_mutable:
            error_msg = f"Vec <{the_symbol._id}> no es mutable y no puede ser modificado"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if len(self.params) != 1:
            error_msg = f"vec.push() solo toma un argumento de entrada. ({len(self.params)} fueron dados)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        element = self.params[0].expr.execute(environment)

        if not global_config.match_vector_deepness(the_symbol.deepness-1, element.value):
            error_msg = f"se ha ingresado una cantidad erronea de vectores anidados,"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        tmp = element
        while tmp._type == ElementType.VECTOR:
            tmp = tmp.value[0]

            if tmp._type == ElementType.ARRAY_EXPRESSION:
                error_msg = f"No pueden combinarse expressiones array con vectores. " \
                            f"No olvides vec! antes de [...]"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

        if the_symbol.content_type != tmp._type:
            error_msg = f".push() fue dado un tipo de dato invalido."
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if the_symbol.capacity[0] <= len(the_symbol.value):   # Minor capacity should not happen, just in case
            if the_symbol.capacity[0] == 0:
                the_symbol.capacity[0] = 1
            else:
                the_symbol.capacity[0] = the_symbol.capacity[0] * 2

        the_symbol.value.append(ValueTuple(element.value, element._type, element.is_mutable, the_symbol.content_type,
                                           the_symbol.capacity))
        return ValueTuple(None, ElementType.VOID, False, the_symbol.content_type, the_symbol.capacity)

    def native_vec_insert(self, the_symbol: VectorSymbol, environment) -> ValueTuple:
        if not the_symbol.is_mutable:
            error_msg = f"Vec <{the_symbol._id}> no es mutable y no puede ser modificado"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if len(self.params) != 2:
            error_msg = f"vec.insert() toma dos argumentos de entrada. ({len(self.params)} fueron dados)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        element = self.params[1].expr.execute(environment)

        if not global_config.match_vector_deepness(the_symbol.deepness - 1, element.value):
            error_msg = f"se ha ingresado una cantidad erronea de vectores anidados,"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        the_index: ValueTuple = self.params[0].expr.execute(environment)
        if the_index._type not in [ElementType.INT, ElementType.USIZE]:
            error_msg = f"El indice de inserción debe ser de tipo int/usize"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if the_index.value < 0:
            error_msg = f"El indice de inserción debe ser positivo"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if len(the_symbol.value) < the_index.value:
            error_msg = f"El indice de inserción esta fuera de el tamaño actual." \
                        f"({len(the_symbol.value)}, {the_index.value})"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        tmp = element
        while tmp._type == ElementType.VECTOR:
            tmp = tmp.value[0]

            if tmp._type == ElementType.ARRAY_EXPRESSION:
                error_msg = f"No pueden combinarse expressiones array con vectores. " \
                            f"No olvides vec! antes de [...]"
                global_config.log_semantic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

        if the_symbol.content_type != tmp._type:
            error_msg = f".insert() fue dado un tipo de dato invalido."
            global_config.log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if the_symbol.capacity[0] <= len(the_symbol.value):  # Minor capacity should not happen, just in case
            if the_symbol.capacity[0] == 0:
                the_symbol.capacity[0] = 1
            else:
                the_symbol.capacity[0] *= 2

        the_symbol.value.insert(the_index.value, ValueTuple(element.value, element._type, element.is_mutable,
                                                            the_symbol.content_type, the_symbol.capacity))
        return ValueTuple(None, ElementType.VOID, False, content_type=the_symbol.content_type,
                          capacity=the_symbol.capacity)

    def native_vec_remove(self, the_symbol: VectorSymbol, environment) -> ValueTuple:
        if not the_symbol.is_mutable:
            error_msg = f"Vec <{the_symbol._id}> no es mutable y no puede ser modificado"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if len(self.params) != 1:
            error_msg = f"vec.remove() solo toma un argumento de entrada. ({len(self.params)} fueron dados)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        the_index: ValueTuple = self.params[0].expr.execute(environment)
        if the_index._type not in [ElementType.INT, ElementType.USIZE]:
            error_msg = f"El indice de inserción debe ser de tipo int/usize"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if the_index.value < 0:
            error_msg = f"El indice de inserción debe ser positivo"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if len(the_symbol.value) <= the_index.value:
            error_msg = f"El indice de inserción esta fuera de el tamaño actual {len(the_symbol.value)}"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        r = the_symbol.value.pop(the_index.value)

        if the_symbol.deepness != 1:
            return ValueTuple(r, ElementType.VECTOR, the_symbol.is_mutable, the_symbol.content_type,
                              the_symbol.capacity)

        return ValueTuple(r.value, r._type, the_symbol.is_mutable, the_symbol.content_type, the_symbol.capacity)
        # return ValueTuple(r, the_symbol.content_type, False, None, None)

    def native_vec_len(self, the_symbol: VectorSymbol) -> ValueTuple:

        if len(self.params) != 0:
            error_msg = f"vec.len() no toma ningún argumento de entrada. ({len(self.params)} fueron dados)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(len(the_symbol.value), ElementType.INT, False, content_type=the_symbol.content_type,
                          capacity=the_symbol.capacity)

    def native_vec_capacity(self, the_symbol: VectorSymbol) -> ValueTuple:

        if len(self.params) != 0:
            error_msg = f"vec.capacity() no toma ningún argumento de entrada. ({len(self.params)} fueron dados)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        return ValueTuple(the_symbol.capacity[0], ElementType.INT, False, the_symbol.content_type, the_symbol.capacity)

    def native_vec_contains(self, the_symbol: VectorSymbol, environment) -> ValueTuple:

        if not self.params[0].as_reference:
            error_msg = f"El valor a buscar debe ser pasado por referencia ->" \
                        f"{self.params[0].expr.execute(environment).value}"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)


        if the_symbol.deepness != 1:
            error_msg = f"vec.contains() solo funciona para vectores de 1 dimension (o solo eso implemente yo xD)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        if len(self.params) != 1:
            error_msg = f"vec.contains() solo toma un argumento de entrada. ({len(self.params)} fueron dados)"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        the_element: ValueTuple = self.params[0].expr.execute(environment)

        if the_element._type != the_symbol.content_type:
            error_msg = f"El tipo de elemento de búsqueda debe ser igual al contenido en el vector"
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        m = global_config.value_tuple_array_to_array(the_symbol.value)
        r = the_element.value in m

        return ValueTuple(r, ElementType.BOOL, the_symbol.is_mutable, None, None)
        # return ValueTuple(r, the_symbol.content_type, False, None, None)









