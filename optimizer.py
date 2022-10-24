import re

from typing import List

class OptimizationReport:
    def __init__(self, reason: str, before: str, after: str):
        self.reason = reason
        self.before = before
        self.after = after



class Optimizer:
    def __init__(self):
        self.reports: List[str] = []

    def optimize_local_rule_1(self, code: str, original_total_code) -> str:

        instructions = code.replace("\r", "").replace(" ", "").strip().split("\n")
        # instructions = code.replace("\r", "").strip().split("\n")
        instructions = [x for x in instructions if x]
        change_made = True
        while change_made is True:
            change_made = False

            # Reverse lookup tends to remove more common expression
            for i in range(len(instructions)-1, 0, -1):
            # for i in range(len(instructions)):
                inst = instructions[i]

                # Should not be searched nor optimized
                label = re.search(r'L[0-9]*:', inst)
                if label is not None:
                    continue

                # Should not be searched but it SHOULD be optimized (in inner loop)
                goto = re.search(r'goto', inst)
                if goto is not None:
                    continue

                # STACK assignments are not optimized (yet??)
                stack = re.search(r'STACK', inst)
                if stack is not None:
                    continue
                    # TODO implement
                    # s_i, _ = stack.span()
                    # if s_i == 0:
                    #     continue

                # HEAP assignments are not optimized (yet??)
                heap = re.search(r'HEAP', inst)
                if heap is not None:
                    continue
                    # TODO implement
                    # s_i, _ = stack.span()
                    # if s_i == 0:
                    #     continue

                return_i = re.search(r'return', inst)
                if return_i is not None:
                    continue

                print_i = re.search(r'print', inst)
                if print_i is not None:
                    continue

                fn_call = re.search(r'[a-zA-Z0-9_]*\(\);', inst)
                if fn_call is not None:
                    continue

                xx = re.search('([a-zA-Z0-9_]*)=([^;]*);', inst)
                if xx is None:
                    pass
                the_tmp, the_expr = xx.groups()
                # tmp_was_reassigned = False

                if the_expr == "H":
                    continue

                for j in range(i+1, len(instructions)):
                    cpr_inst = instructions[j]

                    # Should not be optimized
                    if re.search(r'if\(', inst) is not None:
                        continue

                    # Should not be searched nor optimized
                    label = re.search(r'L[0-9]*:', cpr_inst)
                    if label is not None:
                        continue

                    # Should not be searched but it SHOULD be optimized (in inner loop)
                    goto = re.search(r'goto', cpr_inst)
                    if goto is not None:
                        continue

                    return_i = re.search(r'return', inst)
                    if return_i is not None:
                        continue

                    rr = re.search('(([a-zA-Z0-9_]*)=([^;]*);)', cpr_inst)
                    if rr is None:
                        continue
                    cpr_the_tmp, cpr_the_expr = rr.group(2), rr.group(3)

                    # If tmp was reassigned, same expression is no longer valid
                    if the_tmp == cpr_the_tmp:
                        # tmp_was_reassigned = True
                        break

                    if cpr_the_expr == the_expr:
                        new_inst = f'{cpr_the_tmp}={the_tmp};'
                        instructions[j] = new_inst
                        self.reports.append(f"Local<->Regla 1: Sub-expresiones comunes<->{rr.group(1)}<->{new_inst}")
                        change_made = True

        return "\n".join(instructions)


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