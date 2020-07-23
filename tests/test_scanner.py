from unittest import main, TestCase, skip
from unittest.mock import patch, mock_open
from context import Scanner, TokenType, SymbolTable

class TestScanner(TestCase):

    valid_input = (
        b"int a = 0;\n"
        b"a = 2 + 2;\n"
        b"//b = a < cde;\n"
        b"if a == 0;\n"
    )

    invalid_input = (
            b"if (b /* comment2 */ == 3d) {\n"
            b"a = 3;\n"
            b"cd!e = 7;\n"
            b"}\n"
            b"else */\n"
        )

    def tearDown(self):
      SymbolTable().clear()

    def test_token_type(self):
        scanner = Scanner(self.valid_input, OUTPUT=False)

        expected_tokens = [
            TokenType.KEYWORD, TokenType.ID, TokenType.SYMBOL, TokenType.NUM, TokenType.SYMBOL,
            TokenType.ID, TokenType.SYMBOL, TokenType.NUM, TokenType.SYMBOL, TokenType.NUM, TokenType.SYMBOL,
            TokenType.KEYWORD, TokenType.ID, TokenType.SYMBOL, TokenType.NUM, TokenType.SYMBOL
        ]

        for expected_token in expected_tokens:
            current_token = scanner()
            self.assertEqual(current_token.get_type(), expected_token)

        # Check last token
        current_token = scanner()
        self.assertEqual(current_token.get_type(), TokenType.EOF)

    def test_token_lexeme(self):
        scanner = Scanner(self.valid_input, OUTPUT=False)

        expected_lexemes = [
            'int', 'a', '=', '0', ';',
            'a', '=', '2', '+', '2', ';',
            'if', 'a', '==', '0', ';'
        ]

        for expected_lexeme in expected_lexemes:
            current_token = scanner()
            self.assertEqual(current_token.get_lexeme(), expected_lexeme)

    def test_token_row(self):
        scanner = Scanner(self.valid_input, OUTPUT=False)

        expected_rows = [
            1, 1, 1, 1, 1,
            2, 2, 2, 2, 2, 2,
            4, 4, 4, 4, 4
        ]

        for expected_row in expected_rows:
            current_token = scanner()
            self.assertEqual(current_token.get_row(), expected_row)

    def test_token_column(self):
        scanner = Scanner(self.valid_input, OUTPUT=False)

        expected_columns = [
            0, 4, 6, 8, 9,
            0, 2, 4, 6, 8, 9,
            0, 3, 5, 8, 9
        ]

        for expected_column in expected_columns:
            current_token = scanner()
            self.assertEqual(current_token.get_column(), expected_column)

    def test_invalid_input_types(self):
        scanner = Scanner(self.invalid_input, OUTPUT=False)

        expected_tokens = [
            TokenType.KEYWORD, TokenType.SYMBOL, TokenType.ID, TokenType.SYMBOL, TokenType.SYMBOL, TokenType.SYMBOL,
            TokenType.ID, TokenType.SYMBOL, TokenType.NUM, TokenType.SYMBOL,
            TokenType.ID, TokenType.SYMBOL, TokenType.NUM, TokenType.SYMBOL,
            TokenType.SYMBOL,
            TokenType.KEYWORD
        ]

        for expected_token in expected_tokens:
            current_token = scanner()
            self.assertEqual(current_token.get_type(), expected_token)

    def test_invalid_input_lexeme(self):
        scanner = Scanner(self.invalid_input, OUTPUT=False)

        expected_lexemes = [
            'if', '(', 'b', '==', ')', '{',
            'a', '=', '3', ';',
            'e', '=', '7', ';',
            '}',
            'else'
        ]

        for expected_lexeme in expected_lexemes:
            current_token = scanner()
            self.assertEqual(current_token.get_lexeme(), expected_lexeme)

    @skip("TODO")
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_write_lexical_error(self, mocked_function):
      pass

    @skip("TODO")
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_write_tokens_file(self, mocked_function):
      pass

if __name__ == "__main__":
    unittest.main()
