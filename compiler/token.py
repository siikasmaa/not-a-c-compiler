from enum import Enum, unique

@unique
class TokenType(Enum):
    ADDITION = "+"
    ASSIGN = "="
    BREAK = "break"
    CASE = "case"
    COLON = ":"
    COMMA = ","
    CONTINUE = "continue"
    DEFAULT = "default"
    KEYWORD = 'KEYWORD'
    ELSE = "else"
    EQUAL = "=="
    ID = 'ID'
    IF = "if"
    INT = "int"
    LEFT_CURLY_BRACKET = "{"
    LEFT_PARENTHESIS = "("
    LEFT_SQUARE_BRACKET = "["
    LESS_THAN = "<"
    LINE_COMMENT = "//"
    MULTILINE_COMMENT_END = "*/"
    MULTILINE_COMMENT_START = "/*"
    MULTIPLICATION = "*"
    NUM = 'NUM'
    SYMBOL = 'SYMBOL'
    RETURN = "return"
    RIGHT_CURLY_BRACKET = "}"
    RIGHT_PARENTHESIS = ")"
    RIGHT_SQUARE_BRACKET = "]"
    SEMICOLON = ";"
    STRING = "string"
    SUBTRACTION = "-"
    SWITCH = "switch"
    VOID = "void"
    WHILE = "while"

class Token():

    def __init__(self, row, column, token_type, lexeme):
        if not isinstance(token_type, TokenType):
            # TODO: Should error
            pass
        self._row = row
        self._column = column
        self._type = token_type
        self._lexeme = lexeme

    def get_column(self):
        return self._column

    def set_column(self, column):
        self._column = column

    def get_row(self):
        return self._row

    def set_row(self, row):
        self._row = row

    def get_type(self):
        return self._type.name

    def set_type(self, token_type):
        self._type = token_type

    def get_lexeme(self):
        return self._lexeme

    def set_lexeme(self, lexeme):
        self._lexeme = lexeme
