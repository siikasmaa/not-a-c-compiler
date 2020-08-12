import sys
import os
from anytree import Node, RenderTree
from .token import TokenType
from .grammar import GrammarString, ActionSymbol
from .semantic_analyzer import SemanticAnalyzer
from .symbol import SymbolTable


class Parser():

    _parse_tree_file = './output/parse_tree.txt'
    _syntax_errors_file = "./output/syntax_errors.txt"

    def __init__(self, lexer, **kwargs):
        self._nodes = []
        self._syntax_errors = []
        self._parse_tree_root = None
        self._current_node = None
        self._lookahead_token = None
        self._lexer = lexer
        self._symbol_table = SymbolTable()
        self.DEBUG = kwargs.get('DEBUG', False)
        self._analyzer = SemanticAnalyzer(DEBUG=self.DEBUG)
        self.OUTPUT = kwargs.get('OUTPUT', True)

        self._lookahead_token = self._lexer.get_next_token()
        # Clear files
        if self.OUTPUT:
            try:
                os.mkdir('./output')
            except FileExistsError:
                pass
            with open(self._parse_tree_file, 'w') as _parse_tree_file:
                _parse_tree_file.write("")
            with open(self._syntax_errors_file, 'w') as syntax_errors_file:
                syntax_errors_file.write("")

        # start parsing!
        self.__call__()

    def __repr__(self):
        return self.get_parse_tree()

    def _log(self, *args):
        if self.DEBUG:
            print(args)

    def __call__(self):
        while self._lookahead_token.get_type() != TokenType.EOF:
            self.program()

        if self._lookahead_token.get_type() == TokenType.EOF:
            self._add_parse_tree_node(
                TokenType.EOF.value, self._parse_tree_root)
        self._write_parse_tree()
        if len(self._syntax_errors) == 0:
            self._write_empty_syntax_error()
        return 0

    def _add_parse_tree_node(self, node, parent):
        value = node.value if isinstance(node, GrammarString) else node
        new_node = Node(value, parent)
        if self._parse_tree_root == None and parent == None:
            self._parse_tree_root = new_node
        self._nodes.append(new_node)
        return new_node

    def _write_syntax_error(self, row, error):
        self._syntax_errors.append((row, error))
        if self.OUTPUT:
            try:
                with open(self._syntax_errors_file, 'a+') as syntax_errors_file:
                    syntax_errors_file.write(
                        "#%d : syntax error, %s \n" % (row, error))
            except IOError:
                print("Could not write syntax error for row %d" % row)
                sys.exit(1)

    def _write_empty_syntax_error(self):
        if self.OUTPUT:
            try:
                with open(self._syntax_errors_file, 'w') as syntax_errors_file:
                    syntax_errors_file.write("There is no syntax error.")
            except IOError:
                print("Could not write empty syntax error")
                sys.exit(1)

    def _write_parse_tree(self):
        if self.OUTPUT:
            try:
                with open(self._parse_tree_file, 'w') as parse_tree_file:
                    for pre, _fill, node in RenderTree(self._parse_tree_root):
                        parse_tree_file.write("%s%s\n" % (pre, node.name))
            except IOError:
                print("Could not write parse tree")
                sys.exit(1)

    # For testing purposes
    def get_syntax_errors(self):
        return self._syntax_errors

    # For testing purposes
    def get_parse_tree(self):
        output = ""
        for pre, _fill, node in RenderTree(self._parse_tree_root):
            output += "%s%s\n" % (pre, node.name)
        return output

    def match(self, expected_token, parent_node):
        if isinstance(expected_token, TokenType) and self._lookahead_token.get_type() == expected_token or isinstance(expected_token, str) and self._lookahead_token.get_lexeme() == expected_token:
            self._add_parse_tree_node("(%s, %s)" % (
                self._lookahead_token.get_type().name, self._lookahead_token.get_lexeme()), parent_node)
            self._lookahead_token = self._lexer.get_next_token()
        else:
            raise Exception('Invalid syntax')

    # Grammar procedures
    # N+1 procedures, N: amount of non-terminal symbols

    def program(self):
        node = self._add_parse_tree_node(GrammarString.PROGRAM, None)
        if self._lookahead_token.get_lexeme() in ('void', 'int', '$'):
            self.declaration_list(node)
        else:
            raise Exception('Invalid syntax')

    def declaration_list(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.DECLARATION_LIST, parent_node)
        if self._lookahead_token.get_lexeme() in ('void', 'int'):
            self.declaration(new_node)
            self.declaration_list(new_node)
        elif self._lookahead_token.get_lexeme() in ('$', '{', 'break', ';', 'if', 'while', 'return', 'switch', '+', '-', '(', '}') or self._lookahead_token.get_type() in (TokenType.ID, TokenType.NUM):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def declaration(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.DECLARATION, parent_node)
        if self._lookahead_token.get_lexeme() in ('void', 'int'):
            self.declaration_initial(new_node)
            self.declaration_prime(new_node)

    def declaration_initial(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.DECLARATION_INITIAL, parent_node)
        if self._lookahead_token.get_lexeme() in ('void'):
            self.type_specifier(new_node)
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_ID, self._lookahead_token.get_lexeme())
            self.match(TokenType.ID, new_node)
            self._analyzer.code_gen(
                ActionSymbol.ASSIGN_EMPTY, self._lookahead_token.get_lexeme())
        elif self._lookahead_token.get_lexeme() in ('int'):
            self.type_specifier(new_node)
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_ID, self._lookahead_token.get_lexeme())
            self.match(TokenType.ID, new_node)

    def declaration_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.DECLARATION_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('('):
            self.fun_declaration_prime(new_node)
        elif self._lookahead_token.get_lexeme() in (';', '['):
            self.var_declaration_prime(new_node)

    def var_declaration_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.VAR_DECLARATION_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in (';'):
            self._analyzer.code_gen(
                ActionSymbol.ASSIGN_EMPTY, self._lookahead_token.get_lexeme())
            self.match(';', new_node)
        elif self._lookahead_token.get_lexeme() in ('['):
            self.match('[', new_node)
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_ARRAY, self._lookahead_token.get_lexeme())
            self.match(TokenType.NUM, new_node)
            self.match(']', new_node)
            self.match(';', new_node)

    def fun_declaration_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.FUN_DECLARATION_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('('):
            self.match('(', new_node)
            self.params(new_node)
            self.match(')', new_node)
            self.compound_stmt(new_node)

    def type_specifier(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.TYPE_SPECIFIER, parent_node)
        if self._lookahead_token.get_lexeme() in ('void', 'int'):
            self.match(TokenType.KEYWORD, new_node)

    def params(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.PARAMS, parent_node)
        if self._lookahead_token.get_lexeme() in ('int'):
            self.match(TokenType.KEYWORD, new_node)
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_ID, self._lookahead_token.get_lexeme())
            self.match(TokenType.ID, new_node)
            self.param_prime(new_node)
            self.param_list(new_node)
        elif self._lookahead_token.get_lexeme() in ('void'):
            self.match(TokenType.KEYWORD, new_node)
            self.param_list_void_abtar(new_node)

    def param_list_void_abtar(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.PARAM_LIST_VOID_ABTAR, parent_node)
        if self._lookahead_token.get_type() in (TokenType.ID, TokenType.ID):
            self.match(TokenType.ID, new_node)
            self.param_prime(new_node)
            self.param_list(new_node)
        elif self._lookahead_token.get_lexeme() in (')'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def param_list(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.PARAM_LIST, parent_node)
        if self._lookahead_token.get_lexeme() in (','):
            self.match(',', new_node)
            self.param(new_node)
            self.param_list(new_node)
        elif self._lookahead_token.get_lexeme() in (')'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def param(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.PARAM, parent_node)
        if self._lookahead_token.get_lexeme() in ('int', 'void'):
            self.declaration_initial(new_node)
            self.param_prime(new_node)

    def param_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.PARAM_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('['):
            self.match('[', new_node)
            self.match(']', new_node)
        elif self._lookahead_token.get_lexeme() in (',', ')'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def compound_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.COMPOUND_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('{'):
            self.match('{', new_node)
            self.declaration_list(new_node)
            self.statement_list(new_node)
            self.match('}', new_node)

    def statement_list(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.STATEMENT_LIST, parent_node)
        if self._lookahead_token.get_lexeme() in ('{', 'break', ';', 'if', 'while', 'return', 'switch', '+', '-', '(', 'output') or self._lookahead_token.get_type() in (TokenType.NUM, TokenType.ID):
            self.statement(new_node)
            self.statement_list(new_node)
        elif self._lookahead_token.get_lexeme() in ('}', 'case', 'default'):
            #  Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def statement(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.STATEMENT, parent_node)
        if self._lookahead_token.get_lexeme() in ('break', ';', '+', '-', '(') or self._lookahead_token.get_type() in (TokenType.NUM, TokenType.ID):
            self.expression_stmt(new_node)
        elif self._lookahead_token.get_lexeme() in ('{'):
            self.compound_stmt(new_node)
        elif self._lookahead_token.get_lexeme() in ('if'):
            self.selection_stmt(new_node)
        elif self._lookahead_token.get_lexeme() in ('while'):
            self.iteration_stmt(new_node)
        elif self._lookahead_token.get_lexeme() in ('return'):
            self.return_stmt(new_node)
        elif self._lookahead_token.get_lexeme() in ('switch'):
            self.switch_stmt(new_node)
        elif self._lookahead_token.get_lexeme() in ('output'):
            self.match('output', new_node)
            self.match('(', new_node)
            self.expression(new_node)
            self.match(')', new_node)
            self._analyzer.code_gen(
                ActionSymbol.PRINT, self._lookahead_token.get_lexeme())
            self.match(';', new_node)

    def expression_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.EXPRESSION_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() in (TokenType.NUM, TokenType.ID):
            self.expression(new_node)
            self._analyzer.code_gen(
                ActionSymbol.ASSIGN, self._lookahead_token.get_lexeme())
            self.match(';', new_node)
        elif self._lookahead_token.get_lexeme() in ('break'):
            self.match('break', new_node)
            self.match(';', new_node)
        elif self._lookahead_token.get_lexeme() in (';'):
            self.match(';', new_node)

    def selection_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SELECTION_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('if'):
            self.match('if', new_node)
            self.match('(', new_node)
            self.expression(new_node)
            self.match(')', new_node)
            self._analyzer.code_gen(
                ActionSymbol.SAVE, self._lookahead_token.get_lexeme())
            self.statement(new_node)
            self.match('else', new_node)
            self._analyzer.code_gen(
                ActionSymbol.JPF_SAVE, self._lookahead_token.get_lexeme())
            self.statement(new_node)
            self._analyzer.code_gen(
                ActionSymbol.JUMP, self._lookahead_token.get_lexeme())

    def iteration_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.ITERATION_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('while'):
            self.match('while', new_node)
            self._analyzer.code_gen(
                ActionSymbol.LABEL, self._lookahead_token.get_lexeme())
            self.match('(', new_node)
            self.expression(new_node)
            self.match(')', new_node)
            self._analyzer.code_gen(
                ActionSymbol.SAVE, self._lookahead_token.get_lexeme())
            self.statement(new_node)
            self._analyzer.code_gen(
                ActionSymbol.WHILE, self._lookahead_token.get_lexeme())

    def return_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.RETURN_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('return'):
            self.match('return', new_node)
            self.return_stmt_prime(new_node)

    def return_stmt_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.RETURN_STMT_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in (';'):
            self.match(';', new_node)
        elif self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() in (TokenType.NUM, TokenType.ID):
            self.expression(new_node)
            self.match(';', new_node)

    def switch_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SWITCH_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('switch'):
            self.match('switch', new_node)
            self.match('(', new_node)
            self.expression(new_node)
            self.match(')', new_node)
            self.match('{', new_node)
            self.case_stmts(new_node)
            self.default_stmt(new_node)
            self.match('}', new_node)

    def case_stmts(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.CASE_STMTS, parent_node)
        if self._lookahead_token.get_lexeme() in ('case'):
            self.case_stmt(new_node)
            self.case_stmts(new_node)
        elif self._lookahead_token.get_lexeme() in ('default', '}'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def case_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.CASE_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('case'):
            self.match('case', new_node)
            self.match(TokenType.NUM, new_node)
            self.match(':', new_node)
            self.statement_list(new_node)

    def default_stmt(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.DEFAULT_STMT, parent_node)
        if self._lookahead_token.get_lexeme() in ('default'):
            self.match('default', new_node)
            self.match(':', new_node)
            self.statement_list(new_node)
        elif self._lookahead_token.get_lexeme() in ('}'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def expression(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.EXPRESSION, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() == TokenType.NUM:
            self.simple_expression_zegond(new_node)
        elif self._lookahead_token.get_type() == TokenType.ID:
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_ID, self._lookahead_token.get_lexeme())
            self.match(TokenType.ID, new_node)
            self.b(new_node)

    def b(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.B, parent_node)
        if self._lookahead_token.get_lexeme() in ('='):
            self.match('=', new_node)
            self.expression(new_node)
        elif self._lookahead_token.get_lexeme() in ('['):
            self.match('[', new_node)
            self.expression(new_node)
            self.match(']', new_node)
            self.h(new_node)
        elif self._lookahead_token.get_lexeme() in ('(', '*', '+', '-', '<', '==', ';', ')', ']', ','):
            self.simple_expression_prime(new_node)

    def h(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.H, parent_node)
        if self._lookahead_token.get_lexeme() in ('='):
            self.match('=', new_node)
            self.expression(new_node)
        elif self._lookahead_token.get_lexeme() in ('*', '+', '-', '<', '==', ';', ')', ']', ','):
            self.g(new_node)
            self.d(new_node)
            self.c(new_node)

    def simple_expression_zegond(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SIMPLE_EXPRESSION_ZEGOND, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() == TokenType.NUM:
            self.additive_expression_zegond(new_node)
            self.c(new_node)

    def simple_expression_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SIMPLE_EXPRESSION_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('(', '*', '+', '-', '<', '==', ';', ')', ']', ','):
            self.additive_expression_prime(new_node)
            self.c(new_node)

    def c(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.C, parent_node)
        if self._lookahead_token.get_lexeme() in ('<'):
            self.relop(new_node)
            self.additive_expression(new_node)
            self._analyzer.code_gen(
                ActionSymbol.LESS_THAN, self._lookahead_token.get_lexeme())
        elif self._lookahead_token.get_lexeme() in ('=='):
            self.relop(new_node)
            self.additive_expression(new_node)
            self._analyzer.code_gen(
                ActionSymbol.EQUALS, self._lookahead_token.get_lexeme())
        elif self._lookahead_token.get_lexeme() in (';', ')', ']', ','):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def relop(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.RELOP, parent_node)
        if self._lookahead_token.get_lexeme() in ('<'):
            self.match('<', new_node)
        elif self._lookahead_token.get_lexeme() in ('=='):
            self.match('==', new_node)

    def additive_expression(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.ADDITIVE_EXPRESSION, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() in (TokenType.ID, TokenType.NUM):
            self.term(new_node)
            self.d(new_node)

    def additive_expression_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.ADDITIVE_EXPRESSION_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('(', '*', '+', '-', '==', ';', ')', ']', ','):
            self.term_prime(new_node)
            self.d(new_node)

    def additive_expression_zegond(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.ADDITIVE_EXPRESSION_ZEGOND, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() == TokenType.NUM:
            self.term_zegond(new_node)
            self.d(new_node)

    def d(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.D, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-'):
            self.addop(new_node)
            self.term(new_node)
            self._analyzer.code_gen(
                ActionSymbol.ADDITION, self._lookahead_token.get_lexeme())
            self.d(new_node)
        elif self._lookahead_token.get_lexeme() in ('<', '==', ';', ')', ']', ','):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def addop(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.ADDOP, parent_node)
        if self._lookahead_token.get_lexeme() in ('+'):
            self.match('+', new_node)
        elif self._lookahead_token.get_lexeme() in ('-'):
            self.match('-', new_node)

    def term(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.TERM, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() in (TokenType.ID, TokenType.NUM):
            self.signed_factor(new_node)
            self.g(new_node)

    def term_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.TERM_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('(', '*', '+', '-', '<', '==', ';', ')', ']', ','):
            self.signed_factor_prime(new_node)
            self.g(new_node)

    def term_zegond(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.TERM_ZEGOND, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() == TokenType.NUM:
            self.signed_factor_zegond(new_node)
            self.g(new_node)

    def g(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.G, parent_node)
        if self._lookahead_token.get_lexeme() in ('*'):
            self.match('*', new_node)
            self.signed_factor(new_node)
            self._analyzer.code_gen(
                ActionSymbol.MULTIPLY, self._lookahead_token.get_lexeme())
            self.g(new_node)
        elif self._lookahead_token.get_lexeme() in ('+', '-', '<', '==', ';', ')', ']', ','):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def signed_factor(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SIGNED_FACTOR, parent_node)
        if self._lookahead_token.get_lexeme() in ('+'):
            self.match('+', new_node)
            self.factor(new_node)
        elif self._lookahead_token.get_lexeme() in ('-'):
            self.match('-', new_node)
            self.factor(new_node)
        elif self._lookahead_token.get_lexeme() in ('(') or self._lookahead_token.get_type() in (TokenType.ID, TokenType.NUM):
            self.factor(new_node)

    def signed_factor_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SIGNED_FACTOR_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('(', '*', '+', '-', '<', '==', ';', ')', ']', ','):
            self.factor_prime(new_node)

    def signed_factor_zegond(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.SIGNED_FACTOR_ZEGOND, parent_node)
        if self._lookahead_token.get_lexeme() in ('+'):
            self.match('+', new_node)
            self.factor(new_node)
        elif self._lookahead_token.get_lexeme() in ('-'):
            self.match('-', new_node)
            self.factor(new_node)
        elif self._lookahead_token.get_lexeme() in ('(') or self._lookahead_token.get_type() == TokenType.NUM:
            self.factor_zegond(new_node)

    def factor(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.FACTOR, parent_node)
        if self._lookahead_token.get_lexeme() in ('('):
            self.match('(', new_node)
            self.expression(new_node)
            self.match(')', new_node)
        elif self._lookahead_token.get_type() == TokenType.ID:
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_ID, self._lookahead_token.get_lexeme())
            self.match(TokenType.ID, new_node)
            self.var_call_prime(new_node)
        elif self._lookahead_token.get_type() == TokenType.NUM:
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_NUM, self._lookahead_token.get_lexeme())
            self.match(TokenType.NUM, new_node)

    def var_call_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.VAR_CALL_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('('):
            self.match('(', new_node)
            self.args(new_node)
            self.match(')', new_node)
        elif self._lookahead_token.get_lexeme() in ('[', '*', '+', '-', ';', ')', '<', '==', ']', ','):
            self.var_prime(new_node)

    def var_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.VAR_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('['):
            self.match('[', new_node)
            self.expression(new_node)
            self.match(']', new_node)
        elif self._lookahead_token.get_lexeme() in ('*', '+', '-', ';', ')', '<', '==', ']', ','):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def factor_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.FACTOR_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in ('('):
            self.match('(', new_node)
            self.args(new_node)
            self.match(')', new_node)
        elif self._lookahead_token.get_lexeme() in ('*', '+', '-', '<', '==', ';', ')', ']', ','):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def factor_zegond(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.FACTOR_ZEGOND, parent_node)
        if self._lookahead_token.get_lexeme() in ('('):
            self.match('(', new_node)
            self.expression(new_node)
            self.match(')', new_node)
        elif self._lookahead_token.get_type() == TokenType.NUM:
            self._analyzer.code_gen(
                ActionSymbol.PROCESS_NUM, self._lookahead_token.get_lexeme())
            self.match(TokenType.NUM, new_node)

    def args(self, parent_node):
        new_node = self._add_parse_tree_node(GrammarString.ARGS, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() in (TokenType.ID, TokenType.NUM):
            self.arg_list(new_node)
        elif self._lookahead_token.get_lexeme() in (')'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)

    def arg_list(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.ARG_LIST, parent_node)
        if self._lookahead_token.get_lexeme() in ('+', '-', '(') or self._lookahead_token.get_type() in (TokenType.ID, TokenType.NUM):
            self.expression(new_node)
            self.arg_list_prime(new_node)

    def arg_list_prime(self, parent_node):
        new_node = self._add_parse_tree_node(
            GrammarString.ARG_LIST_PRIME, parent_node)
        if self._lookahead_token.get_lexeme() in (','):
            self.match(',', new_node)
            self.expression(new_node)
            self.arg_list_prime(new_node)
        elif self._lookahead_token.get_lexeme() in (')'):
            # Do nothing
            self._add_parse_tree_node(
            GrammarString.EPSILON, new_node)
