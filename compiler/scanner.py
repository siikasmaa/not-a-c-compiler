import sys
import os
from enum import Enum
from .token import Token, TokenType, OPERATORS, RESERVED_KEYWORDS
from .symbol import Symbol, SymbolTable


class LexicalError(Enum):
    INVALID_INPUT = 'Invalid input'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched */'
    INVALID_NUMBER = 'Invalid number'


class Scanner():

    def __init__(self, content, **kwargs):
        self._current_char_index = 0
        self._current_row = 1
        self._current_column = 0
        self._current_token_column = 0
        self._input = content
        self._tokens = []
        self._symbol_table = SymbolTable()
        self.OUTPUT = kwargs.get('OUTPUT', True)
        # Clear files
        if self.OUTPUT:
            try:
                os.mkdir('./output')
            except FileExistsError:
                pass
            with open(self._tokens_file, 'w') as tokens_file:
                tokens_file.write("")
            with open(self._lexical_errors_file, 'w') as lexical_errors_file:
                lexical_errors_file.write("")

    def __call__(self):
        return self.get_next_token()

    _lexical_errors_file = "./output/lexical_errors.txt"
    _tokens_file = './output/tokens.txt'

    def get_next_token(self):
        current_char = self._get_next_char()
        next_token = None

        if self._is_symbol(current_char):
            # Symbol has to come before is_letter!
            next_token = self._create_symbol_token(current_char)
        elif self._is_letter(current_char):
            next_token = self._create_id_or_keyword_token(current_char)
        elif self._is_digit(current_char):
            next_token = self._create_num_token(current_char)

        if next_token:
            return next_token

        if self._is_end_of_content():
            return self._create_eof_token()
        self.create_lexical_error(current_char)
        return self.get_next_token()

    def create_lexical_error(self, character):
        if chr(character) == '*' and chr(self._peek_next_char()) == '/':
            self._write_lexical_error(
                self._current_row, '*/', LexicalError.UNMATCHED_COMMENT)
            # Consume the following character '/'
            self._read_next_char()
            return
        invalid_input = ""
        current_char = character
        while True:
            next_char = self._peek_next_char()
            invalid_input += chr(current_char)
            if self._is_symbol(next_char) or self._is_letter(next_char) or self._is_digit(next_char) or chr(next_char) == '/' or self._is_whitespace(next_char) or self._is_end_of_content():
                break
            current_char = self._read_next_char()
        self._write_lexical_error(
            self._current_row, invalid_input, LexicalError.INVALID_INPUT)

    def _write_lexical_error(self, row, input, error):
        if self.OUTPUT:
            try:
                with open(self._lexical_errors_file, 'a+') as lexical_errors_file:
                    lexical_errors_file.write(
                        "%d. (%s, %s) \n" % (row, input, error))
            except IOError:
                print("Could not write lexical error for row %d" % row)
                sys.exit(1)

    def skip_comment(self):
        # Consume the first /
        current_char = self._read_next_char()
        next_peek = self._peek_next_char()
        if chr(current_char) == '/':
            while True:
                if self._is_end_of_line(current_char) or self._is_end_of_content():
                    self._next_row()
                    break
                current_char = self._read_next_char()
        else:
            # For nested multiline comments
            multiline_count = 0
            while True:
                if self._is_multiline_comment(current_char, self._peek_next_char()):
                    multiline_count += 1
                    # Consume '/'
                    self._read_next_char()
                elif chr(current_char) == '*' and chr(next_peek) == '/':
                    # Consume '*'
                    self._read_next_char()
                    if multiline_count == 0:
                        break
                    else:
                        multiline_count -= 1
                elif self._is_end_of_content():
                    self._write_lexical_error(
                        self._current_row-multiline_count, '/*', LexicalError.UNCLOSED_COMMENT)
                    break
                elif self._is_end_of_line(current_char):
                    continue
                next_peek = self._peek_next_char()
                current_char = self._read_next_char()

    def _get_next_char(self):
        self._current_token_column = self._current_column
        next_char = self._peek_next_char()
        current_char = self._read_next_char()

        if self._is_end_of_content():
            return current_char
        elif self._skip_whitespace_eol(current_char):
            return self._get_next_char()
        elif self._is_comment(current_char, next_char):
            self.skip_comment()
            return self._get_next_char()
        elif self._is_end_of_line(current_char):
            self._next_row()
            return self._get_next_char()

        return current_char

    def _skip_whitespace_eol(self, current_char):
        if self._is_end_of_line(current_char):
            self._next_row()
            return True
        return self._is_whitespace(current_char)

    def _is_end_of_content(self):
        return self._current_char_index + 1 >= len(self._input)

    def _is_symbol(self, character):
        if chr(character) == '=' and chr(self._peek_next_char()) == '=':
            return True
        return chr(character) in OPERATORS

    def _is_digit(self, character):
        return chr(character).isdigit()

    def _is_letter(self, character):
        return chr(character).isalpha()

    def _is_comment(self, character, next_character):
        return self._is_multiline_comment(character, next_character) or (chr(character) == '/' and chr(next_character) == '/')

    def _is_multiline_comment(self, character, next_character):
        return chr(character) == '/' and chr(next_character) == '*'

    def _is_whitespace(self, character):
        return chr(character).isspace()

    def _is_end_of_line(self, character):
        return character == 10

    def _is_end_of_keyword_or_identifier(self, character):
        return self._is_whitespace(character) or self._is_end_of_line(character) or self._is_end_of_content() or self._is_symbol(character)

    def _read_next_char(self):
        if not self._is_end_of_content():
            current_char = self._input[self._current_char_index]
            self._current_char_index += 1
            self._current_column += 1

            return current_char
        return 0

    def _get_current_char(self):
        if not self._is_end_of_content():
            current_char = self._input[self._current_char_index]
            return current_char
        return 0

    def _peek_next_char(self):
        if not self._is_end_of_content():
            return self._input[self._current_char_index + 1]
        return 0

    def create_token(self, token_type, lexeme):
        token = Token(self._current_row,
                      self._current_token_column, token_type, lexeme)
        self._tokens.append((token.get_type().name, lexeme))
        if token_type == TokenType.ID:
            self._symbol_table.insert(Symbol(lexeme))
        return token

    def _create_symbol_token(self, character):
        if chr(self._get_current_char()) == '=':
            # Consume the following character '='
            self._read_next_char()
            return self.create_token(TokenType.SYMBOL, '==')
        return self.create_token(TokenType.SYMBOL, chr(character))

    def _create_num_token(self, character):
        lexeme = chr(character)
        current_char = character
        while self._is_digit(self._get_current_char()):
            current_char = self._read_next_char()
            lexeme += chr(current_char)
        if self._is_letter(self._get_current_char()):
            current_char = self._read_next_char()
            lexeme += chr(current_char)
            self._write_lexical_error(
                self._current_row, lexeme, LexicalError.INVALID_NUMBER)
            return  # Raise error and create separate error handler?
        return self.create_token(TokenType.NUM, lexeme)

    def _create_eof_token(self):
        return self.create_token(TokenType.EOF, '$')

    def _create_id_or_keyword_token(self, character):
        lexeme = ""
        current_char = character
        while True:
            lexeme += chr(current_char)
            next_char = self._get_current_char()
            if lexeme in RESERVED_KEYWORDS:
                return self.create_token(TokenType.KEYWORD, lexeme)
            if not self._is_digit(next_char) and not self._is_letter(next_char):
                if not self._is_end_of_keyword_or_identifier(next_char):
                    lexeme += chr(next_char)
                    self._write_lexical_error(
                        self._current_row, lexeme, LexicalError.INVALID_INPUT)
                    self._read_next_char()
                    return
                break
            current_char = self._read_next_char()
        return self.create_token(TokenType.ID, lexeme)

    def _write_tokens_file(self):
        output = ""
        for token_type, token_string in self._tokens:
            output += " (%s, %s)" % (token_type, token_string)
        self._tokens.clear()

        if output != "":
            try:
                with open(self._tokens_file, 'a+') as tokens_file:
                    tokens_file.write("%d. %s \n" %
                                      (self._current_row, output))
            except IOError:
                print("Could not write tokens for row %d" % self._current_row)
                sys.exit(1)

    def _next_row(self):
        self._write_tokens_file()
        self._current_row += 1
        self._current_column = 0
