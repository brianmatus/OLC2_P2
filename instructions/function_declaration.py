from typing import List, Union

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment, TransferType
from elements.id_tuple import IDTuple
from element_types.array_def_type import ArrayDefType

from errors.semantic_error import SemanticError
from global_config import log_semantic_error, log_syntactic_error, function_list
from generator import Generator


class FunctionDeclaration(Instruction):
    def __init__(self, function_id: str, params: List[IDTuple],
                 return_type:  ExpressionType, instructions: List[Instruction],
                 line: int, column: int):
        super().__init__(line, column)
        self.function_id: str = function_id
        self.params: List[IDTuple] = params

        self.return_type: ExpressionType = return_type
        self.return_content_type: ExpressionType = return_type
        self.return_capacity = None
        self.return_true_label = []
        self.return_false_label = []
        if isinstance(return_type, ArrayDefType):

            dims, t = global_config.array_type_to_dimension_dict_and_type(return_type)
            self.return_type = ExpressionType.ARRAY
            self.return_content_type = t
            self.return_capacity = dims

        self.instructions: List[Instruction] = instructions
        self.environment: Union[Environment, None] = None

        self.start_label = "func_declaration_start_label_not_set"

        if function_list.get(self.function_id) is not None:
            error_msg = f"La función {self.function_id} ya esta definida. " \
                        f"No esta permitido el sobrecargo de funciones."
            log_semantic_error(error_msg, self.line, self.column)
            raise SemanticError(error_msg, self.line, self.column)

        global_config.function_list[self.function_id] = self
        print(f'Function {self.function_id} saved to main environment')

        self.environment = Environment(global_config.main_environment)  # Just in case, this should happen in every call

        # Constructor wasn't working correctly, just in case
        self.environment.parent_environment = global_config.main_environment

        # FIXME does this work? idk, try it first before deleting
        # global_config.main_environment.size = self.environment.size

    def execute(self, env: Environment) -> ExecReturn:
        self.environment = Environment(env)

        for param in self.params:
            if param.expression_type == ExpressionType.ARRAY:

                self.environment.save_variable_array(variable_id=param.variable_id,
                                                     content_type=param.content_type,
                                                     dimensions=param.dimensions,
                                                     is_mutable=param.is_mutable,
                                                     is_init=True, line=self.line,
                                                     column=self.column)
                # No dimensions specified, need to set them in stack. This values are set by every func call
                if param.dimensions[1] is None:
                    for _ in param.dimensions.keys():
                        self.environment.size += 1

            # TODO check for vector
            # Any other normal expression:
            else:
                self.environment.save_variable(param.variable_id, param.expression_type, param.is_mutable,
                                               True, self.line, self.column)

        final_generator: Generator = Generator()
        final_generator.add_comment(f"<<<-------------------------------Function Declaration of {self.function_id}"
                                    f"------------------------------->>>")

        # dont_execute_me = final_generator.new_label()
        # final_generator.add_goto(dont_execute_me)

        self.start_label = final_generator.new_label()

        final_generator.add_label([self.start_label])

        return_position = final_generator.new_temp()
        final_generator.add_expression(return_position, "t1", "", "")

        # TODO update should be called from func call
        # final_generator.add_comment("-----Update P for a new environment-----")
        #
        # final_generator.add_expression("P", "P", env.size, "+")

        exit_label = final_generator.new_label()
        from elements.c_env import TransferInstruction
        self.environment.transfer_control = TransferInstruction(TransferType.RETURN, exit_label)

        self.environment.return_type = self.return_type
        final_generator.add_comment(f"-----{self.function_id} Instructions-----")
        for instruction in self.instructions:

            if isinstance(instruction, FunctionDeclaration):
                error_msg = f"}} faltante para función"
                log_syntactic_error(error_msg, self.line, self.column)
                raise SemanticError(error_msg, self.line, self.column)

            a = instruction.execute(self.environment)
            final_generator.combine_with(a.generator)

        final_generator.add_comment(f"-----End of {self.function_id} Instructions-----")
        # final_generator.add_comment(f"-----No return? set void-----")
        # already_returned = final_generator.new_label()
        # final_generator.add_if("t2", "1", "==", already_returned)
        # # final_generator.add_expression("t0", "-4242", "", "")
        # final_generator.add_label([already_returned])
        # final_generator.add_expression("t2", "0", "", "")

        final_generator.add_comment("Return label of func:")
        final_generator.add_label([exit_label])
        # final_generator.add_comment("-----Revert P back-----")
        # final_generator.add_expression("P", "P", env.size, "-")

        final_generator.add_comment("-----Where was i called from? return there-----")
        final_generator.add_comment("   -----return value will be set to t0 by return_inst-----")
        final_generator.add_comment(f"-----where to return will be set to t1-----")
        final_generator.add_comment(f"-----t1 is then catch by {return_position}-----")

        if self.function_id in global_config.function_call_list.keys():
            for i in range(len(global_config.function_call_list[self.function_id])):
                final_generator.add_if(return_position, str(i),
                                       "==", global_config.function_call_list[self.function_id][i])
        else:
            print(f"Function {self.function_id} was never called")
            final_generator.add_comment(f"Function {self.function_id} was never called")

        return ExecReturn(generator=final_generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)
