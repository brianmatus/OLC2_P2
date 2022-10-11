from enum import Enum

ExpressionType = Enum('ExpressionType',
                      ' '.join([
                          # 'VOID',  # necessary? idk
                          'INT',
                          'USIZE',
                          'FLOAT',
                          'BOOL',
                          'CHAR',
                          'VOID',
                          'STRING_PRIMITIVE',  # literal
                          'STRING_CLASS',  # class (using .to_owned() or .to_string()
                          'ARRAY',  # only used internally
                          'VECTOR',
                          'NON_SET_TYPE'
                      ]))
