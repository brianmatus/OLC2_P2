from enum import Enum

LogicType = Enum('LogicType',
                 ' '.join([
                     "OPE_EQUAL",
                     "OPE_NEQUAL",
                     "OPE_LESS",
                     "OPE_LESS_EQUAL",
                     "OPE_MORE",
                     "OPE_MORE_EQUAL",

                     "LOGIC_OR",
                     "LOGIC_AND",
                     "LOGIC_NOT",
                     # "LOGIC_TERNARY",
                 ]))
