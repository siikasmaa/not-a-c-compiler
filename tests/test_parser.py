import unittest
from context import Parser, Scanner


class TestParser(unittest.TestCase):

    valid_input = (
        b"void main(void){\n"
        b"int a;\n"
        b"int b;\n"
        b"a = b + - 1;\n"
        b"}\n"
    )

    def test_parse_tree(self):
      self.maxDiff = None
      scanner = Scanner(self.valid_input)
      parser = Parser(scanner)
      parse_tree = parser.get_parse_tree()
      self.assertEqual(parse_tree, expected_parse_tree)

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
