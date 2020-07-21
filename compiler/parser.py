import sys
import os
from anytree import Node, RenderTree
from token import TokenType
from grammar import GrammarString
class Parser():

    _parse_tree_file = './output/parse_tree.txt'
    _syntax_errors_file = "./output/syntax_errors.txt"

    def __init__(self, scanner):
        self._nodes = []
        self._stack = []
        self._syntax_errors = []
        self._parse_tree_root = None
        self._scanner = scanner
        # Clear files
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

    def __call__(self):
        current_token = self._scanner.get_next_token()
        self._push_stack((GrammarString.PROGRAM, None))

        while len(self._stack) > 0:
            (current_grammar_string, current_node) = self._peek_stack()
            current_input = current_token.get_lexeme()

            if current_grammar_string == GrammarString.EPSILON:
                self._pop_stack()
                self._add_parse_tree_node(current_grammar_string.value, current_node)
            # Match!
            elif isinstance(current_grammar_string, TokenType) or current_grammar_string == current_input and isinstance(current_grammar_string, str):
                self._pop_stack()
                self._add_parse_tree_node("(%s, %s)" % (
                    current_token.get_type().name, current_token.get_lexeme()), current_node)
                current_token = self._scanner.get_next_token()
            elif current_grammar_string in self.grammar:
                self._pop_stack()
                parse_action = self.grammar[current_grammar_string]
                if current_input in parse_action:
                    actions = parse_action[current_input]
                elif current_token.get_type() in parse_action:
                    actions = parse_action[current_token.get_type()]
                elif '' in parse_action:
                    actions = parse_action['']
                else:
                    self._write_syntax_error(current_token.get_row(), 'missing %s' % current_grammar_string.value)
                    continue
                  # Tree constructed in opposite order than stack
                new_node = self._add_parse_tree_node(
                    current_grammar_string.value, current_node)
                for action in actions[::-1]:
                    self._push_stack((action, new_node))
            else:
                print("PANIC!")
                error_message = ''
                if current_grammar_string != current_input:
                  error_message = 'missing %s' % current_grammar_string
                self._write_syntax_error(current_token.get_row(), error_message)
                break

        if current_token.get_type() == TokenType.END:
          self._add_parse_tree_node(TokenType.END.value, self._parse_tree_root)
        self._write_parse_tree()
        if len(self._syntax_errors) == 0:
            self._write_empty_syntax_error()
        return 0

    def _push_stack(self, item):
        self._stack.append(item)

    def _pop_stack(self):
        self._stack.pop()

    def _peek_stack(self):
        if len(self._stack) > 0:
            return self._stack[-1]
        return None

    def _add_parse_tree_node(self, node, parent):
        new_node = Node(node, parent)
        if self._parse_tree_root == None and parent == None:
            self._parse_tree_root = new_node
        self._nodes.append(new_node)
        return new_node

    def _write_syntax_error(self, row, error):
        self._syntax_errors.append((row, error))
        try:
            with open(self._syntax_errors_file, 'a+') as syntax_errors_file:
                syntax_errors_file.write(
                    "#%d : syntax error, %s \n" % (row, error))
        except IOError:
            print("Could not write syntax error for row %d" % row)
            sys.exit(1)

    def _write_empty_syntax_error(self):
        try:
            with open(self._syntax_errors_file, 'w') as syntax_errors_file:
                syntax_errors_file.write("There is no syntax error.")
        except IOError:
            print("Could not write empty syntax error")
            sys.exit(1)

    def get_syntax_errors(self):
        return self._syntax_errors

    def _write_parse_tree(self):
        try:
            with open(self._parse_tree_file, 'w') as parse_tree_file:
                for pre, _fill, node in RenderTree(self._parse_tree_root):
                    parse_tree_file.write("%s%s\n" % (pre, node.name))
        except IOError:
            print("Could not write parse tree")
            sys.exit(1)

    # For testing purposes
    def get_parse_tree(self):
        output = ""
        for pre, _fill, node in RenderTree(self._parse_tree_root):
            output += "%s%s\n" % (pre, node.name)
        return output

    grammar = {
        GrammarString.PROGRAM: {
            'void': [GrammarString.DECLARATION_LIST], 'int': [GrammarString.DECLARATION_LIST], '': [GrammarString.DECLARATION_LIST]
        },
        GrammarString.DECLARATION_LIST: {
            'void': [GrammarString.DECLARATION, GrammarString.DECLARATION_LIST], 'int': [GrammarString.DECLARATION, GrammarString.DECLARATION_LIST], '': [GrammarString.EPSILON]
        },
        GrammarString.DECLARATION: {
            'void': [GrammarString.DECLARATION_INITIAL, GrammarString.DECLARATION_PRIME], 'int': [GrammarString.DECLARATION_INITIAL, GrammarString.DECLARATION_PRIME]
        },
        GrammarString.DECLARATION_INITIAL: {
            'void': [GrammarString.TYPE_SPECIFIER, TokenType.ID], 'int': [GrammarString.TYPE_SPECIFIER, TokenType.ID]
        },
        GrammarString.DECLARATION_PRIME: {
            ';': [GrammarString.VAR_DECLARATION_PRIME], '[': [GrammarString.VAR_DECLARATION_PRIME], '(': [GrammarString.FUN_DECLARATION_PRIME]
        },
        GrammarString.VAR_DECLARATION_PRIME: {
            ';': [';'], '[': ['[', TokenType.NUM, ']', ';']
        },
        GrammarString.FUN_DECLARATION_PRIME: {
            '(': ['(', GrammarString.PARAMS,  ')', GrammarString.COMPOUND_STMT]
        },
        GrammarString.TYPE_SPECIFIER: {
            'void': [TokenType.KEYWORD], 'int': [TokenType.KEYWORD]
        },
        GrammarString.PARAMS: {
            'void': [TokenType.KEYWORD, GrammarString.PARAM_LIST_VOID_ABTAR], 'int': [TokenType.KEYWORD, TokenType.ID, GrammarString.PARAM_PRIME, GrammarString.PARAM_LIST]
        },
        GrammarString.PARAM_LIST_VOID_ABTAR: {
            TokenType.ID: [TokenType.ID, GrammarString.PARAM_PRIME, GrammarString.PARAM_LIST], '': [GrammarString.EPSILON]
        },
        GrammarString.PARAM_PRIME: {
          '[': ['[', ']'], '': [GrammarString.EPSILON]
        },
        GrammarString.PARAM_LIST: {
            ',': [',', GrammarString.PARAM, GrammarString.PARAM_LIST], '': [GrammarString.EPSILON]
        },
        GrammarString.COMPOUND_STMT: {
            '{': ['{', GrammarString.DECLARATION_LIST, GrammarString.STATEMENT_LIST, '}']
        },
        GrammarString.STATEMENT_LIST: {
            '{': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], 'break': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], ';': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST],
            'if': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], 'while': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], 'return': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST],
            'switch': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], TokenType.ID: [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], '+': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST],
            '-': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], '(': [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST], TokenType.NUM: [GrammarString.STATEMENT, GrammarString.STATEMENT_LIST],
            '': [GrammarString.EPSILON]
        },
        GrammarString.STATEMENT: {
            '{': [GrammarString.COMPOUND_STMT], 'break': [GrammarString.EXPRESSION_STMT], ';': [GrammarString.EXPRESSION_STMT],
            'if': [GrammarString.SELECTION_STMT], 'while': [GrammarString.ITERATION_STMT], 'return': [GrammarString.RETURN_STMT],
            'switch': [GrammarString.SWITCH_STMT], TokenType.ID: [GrammarString.EXPRESSION_STMT], '+': [GrammarString.EXPRESSION_STMT],
            '-': [GrammarString.EXPRESSION_STMT], '(': [GrammarString.EXPRESSION_STMT], TokenType.NUM: [GrammarString.EXPRESSION_STMT]
        },
        GrammarString.EXPRESSION_STMT: {
            'break': ['break', ';'], ';': [';'], TokenType.ID: [GrammarString.EXPRESSION, ';'],
            '+': [GrammarString.EXPRESSION, ';'], '-': [GrammarString.EXPRESSION, ';'], '(': [GrammarString.EXPRESSION, ';'],
            TokenType.NUM: [GrammarString.EXPRESSION, ';']
        },
        GrammarString.SELECTION_STMT: {
            'if': ['if', '(', GrammarString.EXPRESSION, ')', GrammarString.STATEMENT, 'else', GrammarString.STATEMENT]
        },
        GrammarString.ITERATION_STMT: {
            'while': ['while', '(', GrammarString.EXPRESSION, ')', GrammarString.STATEMENT]
        },
        GrammarString.RETURN_STMT: {
            'return': ['return', GrammarString.RETURN_STMT_PRIME]
        },
        GrammarString.RETURN_STMT_PRIME: {
            ';': [';'], TokenType.ID: [GrammarString.EXPRESSION, ';'], '+': [GrammarString.EXPRESSION, ';'], '-': [GrammarString.EXPRESSION, ';'], '(': [GrammarString.EXPRESSION, ';'], TokenType.NUM: [GrammarString.EXPRESSION, ';']
        },
        GrammarString.SWITCH_STMT: {
            'switch': ['switch', '(', GrammarString.EXPRESSION, ')', '{', GrammarString.CASE_STMTS, GrammarString.DEFAULT_STMT, '}']
        },
        GrammarString.CASE_STMTS: {
            'case': [GrammarString.CASE_STMT, GrammarString.CASE_STMTS], '': [GrammarString.EPSILON]
        },
        GrammarString.CASE_STMT: {
            'case': ['case', TokenType.NUM, ':', GrammarString.STATEMENT_LIST]
        },
        GrammarString.DEFAULT_STMT: {
            'default': ['default', ':', GrammarString.STATEMENT_LIST], '': [GrammarString.EPSILON]
        },
        GrammarString.EXPRESSION: {
            TokenType.ID: [TokenType.ID, GrammarString.B], '+': [GrammarString.SIMPLE_EXPRESSION_ZEGOND], '-': [GrammarString.SIMPLE_EXPRESSION_ZEGOND],
            '(': [TokenType.ID, GrammarString.B], TokenType.NUM: [GrammarString.SIMPLE_EXPRESSION_ZEGOND]
        },
        GrammarString.B: {
            '=': ['=', GrammarString.EXPRESSION], '[': ['[', GrammarString.EXPRESSION, ']', GrammarString.H], '(': [GrammarString.SIMPLE_EXPRESSION_PRIME], '*': [GrammarString.SIMPLE_EXPRESSION_PRIME], '+': [GrammarString.SIMPLE_EXPRESSION_PRIME], '-': [GrammarString.SIMPLE_EXPRESSION_PRIME], '<': [GrammarString.SIMPLE_EXPRESSION_PRIME], '==': [GrammarString.SIMPLE_EXPRESSION_PRIME], '': [GrammarString.SIMPLE_EXPRESSION_PRIME]
        },
        GrammarString.H: {
            '=': ['=', GrammarString.EXPRESSION], '*': [GrammarString.G, GrammarString.D, GrammarString.C], '+': [GrammarString.G, GrammarString.D, GrammarString.C], '-': [GrammarString.G, GrammarString.D, GrammarString.C], '<': [GrammarString.G, GrammarString.D, GrammarString.C], '==': [GrammarString.G, GrammarString.D, GrammarString.C], '': [GrammarString.G, GrammarString.D, GrammarString.C]
        },
        GrammarString.D: {
            '+': [GrammarString.ADDOP, GrammarString.TERM, GrammarString.D], '-': [GrammarString.ADDOP, GrammarString.TERM, GrammarString.D], '': [GrammarString.EPSILON]
        },
        GrammarString.SIMPLE_EXPRESSION_PRIME: {
            '(': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C], '*': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C], '+': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C], '-': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C], '<': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C], '==': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C], '': [GrammarString.ADDITIVE_EXPRESSION_PRIME, GrammarString.C]
        },
        GrammarString.SIMPLE_EXPRESSION_ZEGOND: {
            '+': [GrammarString.ADDITIVE_EXPRESSION_ZEGOND, GrammarString.C], '-': [GrammarString.ADDITIVE_EXPRESSION_ZEGOND, GrammarString.C], '(': [GrammarString.ADDITIVE_EXPRESSION_ZEGOND, GrammarString.C], TokenType.NUM: [GrammarString.ADDITIVE_EXPRESSION_ZEGOND, GrammarString.C]
        },
        GrammarString.C: {
            '<': [GrammarString.RELOP, GrammarString.ADDITIVE_EXPRESSION], '==': [GrammarString.RELOP, GrammarString.ADDITIVE_EXPRESSION], '': [GrammarString.EPSILON]
        },
        GrammarString.G: {
            '*': ['*', GrammarString.SIGNED_FACTOR, GrammarString.G], '': [GrammarString.EPSILON]
        },
        GrammarString.RELOP: {
            '<': ['<'], '==': ['==']
        },
        GrammarString.ADDITIVE_EXPRESSION: {
            '+': [GrammarString.TERM, GrammarString.D], '-': [GrammarString.TERM, GrammarString.D], '(': [GrammarString.TERM, GrammarString.D], TokenType.ID: [GrammarString.TERM, GrammarString.D], TokenType.NUM: [GrammarString.TERM, GrammarString.D]
        },
        GrammarString.ADDITIVE_EXPRESSION_PRIME: {
            '(': [GrammarString.TERM_PRIME, GrammarString.D], '*': [GrammarString.TERM_PRIME, GrammarString.D], '+': [GrammarString.TERM_PRIME, GrammarString.D], '-': [GrammarString.TERM_PRIME, GrammarString.D], '': [GrammarString.TERM_PRIME, GrammarString.D]
        },
        GrammarString.ADDITIVE_EXPRESSION_ZEGOND: {
            '+': [GrammarString.TERM_ZEGOND, GrammarString.D], '-': [GrammarString.TERM_ZEGOND, GrammarString.D], '(': [GrammarString.TERM_ZEGOND, GrammarString.D], TokenType.NUM: [GrammarString.TERM_ZEGOND, GrammarString.D]
        },
        GrammarString.ADDOP: {
            '+': ['+'], '-': ['-']
        },
        GrammarString.TERM: {
            '+': [GrammarString.SIGNED_FACTOR, GrammarString.G], '-': [GrammarString.SIGNED_FACTOR, GrammarString.G], '(': [GrammarString.SIGNED_FACTOR, GrammarString.G], TokenType.ID: [GrammarString.SIGNED_FACTOR, GrammarString.G], TokenType.NUM: [GrammarString.SIGNED_FACTOR, GrammarString.G]
        },
        GrammarString.TERM_PRIME: {
            '(': [GrammarString.SIGNED_FACTOR_PRIME, GrammarString.G], '*': [GrammarString.SIGNED_FACTOR_PRIME, GrammarString.G], '': [GrammarString.SIGNED_FACTOR_PRIME, GrammarString.G]
        },
        GrammarString.TERM_ZEGOND: {
            '+': [GrammarString.SIGNED_FACTOR_ZEGOND, GrammarString.G], '-': [GrammarString.SIGNED_FACTOR_ZEGOND, GrammarString.G], '(': [GrammarString.SIGNED_FACTOR_ZEGOND, GrammarString.G], TokenType.NUM: [GrammarString.SIGNED_FACTOR_ZEGOND, GrammarString.G]
        },
        GrammarString.SIGNED_FACTOR: {
            '+': ['+', GrammarString.FACTOR], '-': ['-', GrammarString.FACTOR], '(': [GrammarString.FACTOR], TokenType.ID: [GrammarString.FACTOR], TokenType.NUM: [GrammarString.FACTOR]
        },
        GrammarString.SIGNED_FACTOR_PRIME: {
            '(': [GrammarString.FACTOR_PRIME], '': [GrammarString.FACTOR_PRIME]
        },
        GrammarString.SIGNED_FACTOR_ZEGOND: {
            '+': ['+', GrammarString.FACTOR], '-': ['-', GrammarString.FACTOR], '(': [GrammarString.FACTOR_ZEGOND], TokenType.NUM: [GrammarString.FACTOR_ZEGOND]
        },
        GrammarString.FACTOR: {
            '(': ['(', GrammarString.EXPRESSION, ')'], TokenType.ID: [TokenType.ID, GrammarString.VAR_CALL_PRIME], TokenType.NUM: [TokenType.NUM]
        },
        GrammarString.FACTOR_PRIME: {
            '(': ['(', GrammarString.ARGS, ')'],  '': [GrammarString.EPSILON]
        },
        GrammarString.VAR_CALL_PRIME: {
            '(': ['(', GrammarString.ARGS, ')'], '[': [GrammarString.VAR_PRIME], '': [GrammarString.VAR_PRIME]
        },
        GrammarString.VAR_PRIME: {
            '[': ['[', GrammarString.EXPRESSION, ']'],  '': [GrammarString.EPSILON]
        },
        GrammarString.FACTOR_ZEGOND: {
            '(': ['(', GrammarString.EXPRESSION, ')'],  TokenType.NUM: [TokenType.NUM]
        },
        GrammarString.ARGS: {
            TokenType.ID: [GrammarString.ARG_LIST], '+': [GrammarString.ARG_LIST], '-': [GrammarString.ARG_LIST], '(': [GrammarString.ARG_LIST], TokenType.NUM: [GrammarString.ARG_LIST], '': [GrammarString.EPSILON]
        },
        GrammarString.ARG_LIST: {
            TokenType.ID: [GrammarString.EXPRESSION, GrammarString. ARG_LIST_PRIME], '+': [GrammarString.EXPRESSION, GrammarString. ARG_LIST_PRIME], '-': [GrammarString.EXPRESSION, GrammarString. ARG_LIST_PRIME], '(': [GrammarString.EXPRESSION, GrammarString. ARG_LIST_PRIME], TokenType.NUM: [GrammarString.EXPRESSION, GrammarString. ARG_LIST_PRIME]
        },
        GrammarString.ARG_LIST_PRIME: {
            ',': [], '': [GrammarString.EPSILON]
        },

    }
