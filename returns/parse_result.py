from typing import List
from errors.lexic_error import LexicError
from errors.semantic_error import SemanticError
from errors.syntactic_error import SyntacticError


class ParseResult:

    def __init__(self, lexic_error_list: List[LexicError], syntactic_error_list: List[SyntacticError],
                 semantic_error_list: List[SemanticError], symbol_table: List[List[str]],
                 console_output: str, ast_tree: str):

        self.lexic_error_list = lexic_error_list
        self.semantic_error_list = semantic_error_list
        self.syntactic_error_list = syntactic_error_list
        self.symbol_table = symbol_table
        self.console_output = console_output
        self.ast_tree = ast_tree

