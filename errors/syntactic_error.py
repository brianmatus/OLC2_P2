class SyntacticError(Exception):

    def __init__(self, reason: str, line: int, column: int):
        self.reason = reason
        self.row = line
        self.column = column

    def __str__(self):
        return f"{self.reason}<->{self.row}<->{self.column}"

    def __repr__(self):
        return f"{self.reason}<->{self.row}<->{self.column}"