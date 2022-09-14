from enum import Enum

ArithmeticType = Enum('ArithmeticType',
                   ' '.join([
                       "SUM",
                       "SUB",
                       "MULT",
                       "DIV",
                       "POW_INT",
                       "POW_FLOAT",
                       "MOD",
                       "NEG"
                   ]))
