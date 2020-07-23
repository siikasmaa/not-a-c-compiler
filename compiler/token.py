import sys
from enum import Enum, unique

OPERATORS = [
    ";",
    ":",
    ",",
    "[",
    "]",
    "(",
    ")",
    "{",
    "}",
    "+",
    "-",
    "*",
    "=",
    "<",
    "=="
]

RESERVED_KEYWORDS = [
    "if",
    "else",
    "void",
    "int",
    "while",
    "break",
    "continue",
    "switch",
    "default",
    "case",
    "return",
    "output"
]


@unique
class TokenType(Enum):
    KEYWORD = 'KEYWORD'
    EOF = "$"
    ID = 'ID'
    NUM = 'NUM'
    SYMBOL = 'SYMBOL'


class Token(object):

    def __init__(self, row, column, token_type, lexeme):
        if not isinstance(token_type, TokenType):
            print('Invalid token')
            sys.exit(1)
        self._row = row
        self._column = column
        self._type = token_type
        self._lexeme = lexeme

    def __str__(self):
        return "%s :%d:%d" % (self._lexeme, self._row, self._column)

    def __repr__(self):
        return self.__str__()

    def get_column(self):
        return self._column

    def set_column(self, column):
        self._column = column
        return self

    def get_row(self):
        return self._row

    def set_row(self, row):
        self._row = row
        return self

    def get_type(self):
        return self._type

    def set_type(self, token_type):
        self._type = token_type
        return self

    def get_lexeme(self):
        return self._lexeme

    def set_lexeme(self, lexeme):
        self._lexeme = lexeme
        return self
