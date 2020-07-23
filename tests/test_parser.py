from unittest import main, TestCase, skip
from unittest.mock import patch, mock_open
from context import Parser, Scanner, SymbolTable

class TestParser(TestCase):

    valid_input = (
        b"void main(void){\n"
        b"int a;\n"
        b"int b;\n"
        b"a = b + - 1;\n"
        b"}\n"
    )

    def tearDown(self):
      SymbolTable().clear()

    @patch('compiler.semantic_analyzer.SemanticAnalyzer.code_gen')
    def test_parse_tree(self, mocked_analyzer):
      self.maxDiff = None
      scanner = Scanner(self.valid_input, OUTPUT=False)
      parser = Parser(scanner, OUTPUT=False)
      parse_tree = parser.get_parse_tree()
      self.assertEqual(parse_tree, expected_parse_tree)

    @skip("TODO")
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_write_parse_tree(self, mocked_function):
      pass

    @skip("TODO")
    @patch("compiler.semantic_analyzer.SemanticAnalyzer.code_gen")
    def test_action_symbols(self, mocked_function):
      pass

    @skip("TODO")
    @patch("compiler.semantic_analyzer.SemanticAnalyzer.semantic_check")
    def test_analysis(self, mocked_function):
      pass

    # def test_syntax_errors(self):
    #     scanner = Scanner(self.valid_input)
    #     parser = Parser(scanner)
    #     syntax_errors = parser.get_syntax_errors()
    #     self.assertEqual(syntax_errors, [])

if __name__ == "__main__":
    unittest.main()

expected_parse_tree = """Program
├── DeclarationList
│   ├── Declaration
│   │   ├── DeclarationInitial
│   │   │   ├── TypeSpecifier
│   │   │   │   └── (KEYWORD, void)
│   │   │   └── (ID, main)
│   │   └── DeclarationPrime
│   │       └── FunDeclarationPrime
│   │           ├── (SYMBOL, ()
│   │           ├── Params
│   │           │   ├── (KEYWORD, void)
│   │           │   └── ParamListVoidAbtar
│   │           │       └── epsilon
│   │           ├── (SYMBOL, ))
│   │           └── CompoundStmt
│   │               ├── (SYMBOL, {)
│   │               ├── DeclarationList
│   │               │   ├── Declaration
│   │               │   │   ├── DeclarationInitial
│   │               │   │   │   ├── TypeSpecifier
│   │               │   │   │   │   └── (KEYWORD, int)
│   │               │   │   │   └── (ID, a)
│   │               │   │   └── DeclarationPrime
│   │               │   │       └── VarDeclarationPrime
│   │               │   │           └── (SYMBOL, ;)
│   │               │   └── DeclarationList
│   │               │       ├── Declaration
│   │               │       │   ├── DeclarationInitial
│   │               │       │   │   ├── TypeSpecifier
│   │               │       │   │   │   └── (KEYWORD, int)
│   │               │       │   │   └── (ID, b)
│   │               │       │   └── DeclarationPrime
│   │               │       │       └── VarDeclarationPrime
│   │               │       │           └── (SYMBOL, ;)
│   │               │       └── DeclarationList
│   │               │           └── epsilon
│   │               ├── StatementList
│   │               │   ├── Statement
│   │               │   │   └── ExpressionStmt
│   │               │   │       ├── Expression
│   │               │   │       │   ├── (ID, a)
│   │               │   │       │   └── B
│   │               │   │       │       ├── (SYMBOL, =)
│   │               │   │       │       └── Expression
│   │               │   │       │           ├── (ID, b)
│   │               │   │       │           └── B
│   │               │   │       │               └── SimpleExpressionPrime
│   │               │   │       │                   ├── AdditiveExpressionPrime
│   │               │   │       │                   │   ├── TermPrime
│   │               │   │       │                   │   │   ├── SignedFactorPrime
│   │               │   │       │                   │   │   │   └── FactorPrime
│   │               │   │       │                   │   │   │       └── epsilon
│   │               │   │       │                   │   │   └── G
│   │               │   │       │                   │   │       └── epsilon
│   │               │   │       │                   │   └── D
│   │               │   │       │                   │       ├── Addop
│   │               │   │       │                   │       │   └── (SYMBOL, +)
│   │               │   │       │                   │       ├── Term
│   │               │   │       │                   │       │   ├── SignedFactor
│   │               │   │       │                   │       │   │   ├── (SYMBOL, -)
│   │               │   │       │                   │       │   │   └── Factor
│   │               │   │       │                   │       │   │       └── (NUM, 1)
│   │               │   │       │                   │       │   └── G
│   │               │   │       │                   │       │       └── epsilon
│   │               │   │       │                   │       └── D
│   │               │   │       │                   │           └── epsilon
│   │               │   │       │                   └── C
│   │               │   │       │                       └── epsilon
│   │               │   │       └── (SYMBOL, ;)
│   │               │   └── StatementList
│   │               │       └── epsilon
│   │               └── (SYMBOL, })
│   └── DeclarationList
│       └── epsilon
└── $
"""
