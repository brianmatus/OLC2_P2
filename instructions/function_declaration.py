from typing import List, Union

import global_config
from returns.exec_return import ExecReturn
from abstract.instruction import Instruction
from element_types.c_expression_type import ExpressionType
from elements.c_env import Environment, TransferType
from elements.id_tuple import IDTuple

from errors.semantic_error import SemanticError
from global_config import log_semantic_error, function_list
from generator import Generator


class FunctionDeclaration(Instruction):
    def __init__(self, function_id: str, params: List[IDTuple],
                 return_type:  ExpressionType, instructions: List[Instruction],
                 line: int, column: int):
        super().__init__(line, column)
        self.function_id: str = function_id
        self.params: List[IDTuple] = params
        self.return_type: ExpressionType = return_type
        self.instructions: List[Instruction] = instructions
        self.environment: Union[Environment, None] = None

        self.start_label = "func_declr_start_label_not_set"

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

    def execute(self, env: Environment) -> ExecReturn:
        self.environment = Environment(env)
        self.environment.size = len(self.params)  # This will be set by func_call, space is just allocated

        final_generator: Generator = Generator()
        final_generator.add_comment(f"<<<-------------------------------Function Declaration of {self.function_id}"
                                    f"------------------------------->>>")

        # dont_execute_me = final_generator.new_label()
        # final_generator.add_goto(dont_execute_me)

        self.start_label = final_generator.new_label()

        final_generator.add_label([self.start_label])

        final_generator.add_comment("-----Update P for a new environment-----")

        final_generator.add_expression("P", "P", env.size, "+")

        exit_label = final_generator.new_label()
        self.environment.queue_transfer(TransferType.RETURN, exit_label)
        final_generator.add_comment(f"-----{self.function_id} Instructions-----")
        for instruction in self.instructions:
            a = instruction.execute(self.environment)
            final_generator.combine_with(a.generator)

        final_generator.add_comment(f"-----End of {self.function_id} Instructions-----")
        final_generator.add_comment(f"-----No return? set void-----")
        already_returned = final_generator.new_label()
        final_generator.add_if("t2", "1", "==", already_returned)
        # final_generator.add_expression("t0", "-4242", "", "")
        final_generator.add_label([already_returned])
        final_generator.add_expression("t2", "0", "", "")

        final_generator.add_label([exit_label])
        final_generator.add_comment("-----Revert P back-----")
        final_generator.add_expression("P", "P", env.size, "-")

        final_generator.add_comment("-----Where was i called from? return there-----")
        final_generator.add_comment("   -----return value will be set to t0 by return_inst-----")
        final_generator.add_comment("-----where to return will be set to t1 by func_call_inst-----")

        if self.function_id in global_config.function_call_list.keys():
            for i in range(len(global_config.function_call_list[self.function_id])):
                final_generator.add_if("t1", str(i), "==", global_config.function_call_list[self.function_id][i])
        else:
            print(f"Function {self.function_id} was never called")
            final_generator.add_comment(f"Function {self.function_id} was never called")

        return ExecReturn(generator=final_generator,
                          propagate_method_return=False, propagate_continue=False, propagate_break=False)
