import re

from typing import List

class OptimizationReport:
    def __init__(self, reason: str, before: str, after: str):
        self.reason = reason
        self.before = before
        self.after = after



class Optimizer:
    def __init__(self):
        self.reports: List[str] = ["a<->b<->c"]

    def optimize_local_rule_1(self, code: str):

        instructions = code.replace("\r", "").strip().split("\n")




        pass


    def optimize_local_always_true_always_false_ifs(self, code: str) -> str:
        # TODO NOT IMPLEMENTED YET
        before_start_i = 0
        before_end_i = len(code)
        after_start_i = 0
        after_end_i = len(code)

        r = re.search(r'if \(([0-9]*) (>=|>|<=|<|==|!=) ([0-9]*) \) goto ([a-zA-Z0-9]*);', code)
        a, operation, b, label = r.groups()
        always_true = False
        always_false = False
        match operation:
            case '>':
                if float(a) > float(b):
                    always_true = True
                always_false = True
            case '>=':
                if float(a) >= float(b):
                    always_true = True
                always_false = True
            case '<':
                if float(a) < float(b):
                    always_true = True
                always_false = True
            case '<=':
                if float(a) <= float(b):
                    always_true = True
                always_false = True
            case '==':
                if float(a) == float(b):
                    always_true = True
                always_false = True
            case '!=':
                if float(a) != float(b):
                    always_true = True
                always_false = True

        start, finish = r.span()
        if always_true:
            # make direct jump
            # code after this is inaccesible, remove
            code_before = code[:start]
            code_after = code[finish:]

        if always_false:
            # remove jump
            pass
        return code