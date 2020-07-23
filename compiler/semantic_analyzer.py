import sys
import os
from .grammar import ActionSymbol
from .symbol import SymbolTable
from enum import Enum, unique


class SemanticError():

    @unique
    class SemanticErrorType(Enum):
        SCOPING_ERROR = "Semantic Error! Illegal type of void for '{e._id}'"
        VOID_TYPE = "semantic error! Mismatch in numbers of arguments of '{e._id}'"
        PARAMETERS_NUMBER = "Semantic Error! No 'while' or 'switch' found for 'break'"
        BREAK = "Semantic Error! Type mismatch in operands, Got '{e._y}' instead of '{e._x}'"
        TYPE = "Semantic Error! Mismatch in type of argument {e._arg_num} for '{e._id}'. Expected '{e._x}' but got '{e._y}' instead'"
        PARAMETERS_TYPE = "Semantic Error! Mismatch in type of argument {e._arg_num} for '{e._id}'. Expected '{e._x}' but got '{e._y}' instead.'"

    def __init__(self, line, error_type, **kwargs):
        if not isinstance(error_type, SemanticError.SemanticErrorType):
            print('Invalid error type')
            sys.exit(1)
        self._line = line
        self._type = error_type
        self._id = kwargs.get('id', None)
        self._arg_num = kwargs.get('arg_num', None)
        self._x = kwargs.get('x', None)
        self._y = kwargs.get('y', None)

    def __repr__(self):
        error_text = self._type.value.format(e=self)
        return "#{line} : {error}".format(line=self._line, error=error_text)

    __str__ = __repr__
    """
      1. Scoping: all variables must be declared either globally or in the current scope, before they can be used in any expression. Besides, every function should be defined before it can be invoked. These are required in order to be able to implement a one pass compiler. If a variable or a function identifier with token ID lacks such a declaration or definition, respectively, the error should be reported by the message: #lineno: Semantic Error! 'ID' is not defined, where 'ID' is the undefined variable/function.
      2.  Void type: when defining a single variable or an array, the type cannot be void. In such a case, report the error by the error message:
      3. Actual and formal parameters number matching: when invoking a function, the number of arguments passed via invocation must match the number of parameters that has been given in the function definition. Otherwise, the error should be reported by the message:
      4. Break statement: if a 'break' statement is not within any while loops or switch statements, signal the error by the message:
      5. Type mismatch: in a numerical and/or comparison operation, the types of operands on both sides of the operation should match. Otherwise, the error should be reported by the message:
      6. Actual and formal parameter type matching: when invoking a function, the type of each argument passed via invocation must match the type of associated parameter in the function definition. Otherwise, the error should be reported by the message:
    """


class SemanticStack(object):
    def __init__(self):
        self.stack = []

    def __str__(self):
        return str(self.stack)

    __repr__ = __str__

    def __call__(self):
        return self.stack

    def top(self):
        return self.stack[-1]

    def from_top(self, index=0):
        return self.stack[-1-index]

    def pop(self, count=1):
        self.stack = self.stack[:len(
            self.stack)-count]

    def push(self, item):
        self.stack.append(item)

    def set_stack(self, items):
        self.stack = items

    def is_empty(self):
        return len(self.stack) == 0


class SemanticAnalyzer():

    _output_file = './output/output.txt'
    _errors_file = "./output/semantic_error.txt"

    def __init__(self, **kwargs):
        self._semantic_stack = SemanticStack()
        self._semantic_errors = []
        self._program_block = []
        self._line_count = 0
        self._symbol_table = SymbolTable()
        self.DEBUG = kwargs.get('DEBUG', False)
        self.OUTPUT = kwargs.get('OUTPUT', True)
        # Clear files
        if self.OUTPUT:
            try:
                os.mkdir('./output')
            except FileExistsError:
                pass
            with open(self._output_file, 'w') as output_file:
                output_file.write("")
            with open(self._errors_file, 'w') as errors_file:
                errors_file.write("")

    def _log(self, output):
        if self.DEBUG:
            print(output)

    def semantic_check(self, action_symbol):
        asd = SemanticError(
            0, SemanticError.SemanticErrorType.SCOPING_ERROR, id="test")
        self._write_semantic_error(asd)
        # Semantic analysis is performed in a manner very similar to one explained in Lecture 6 for intermediate code generation.
        # That is, the parser calls a function (let's call it 'semantic_check') in certain stages in the non-terminals subroutines.
        # Parser passes an appropriate action symbol as an argument to the semantic analyser (i.e., 'semantic_check' function).
        # Semantic analyser then executes the associated semantic routine, and the control returns to the parser.

        pass

    def code_gen(self, action_symbol, current_input):
        """
        1. (ADD, A1, A2, R) : The contents of A1 and A2 are added. The result will be saved in R.
        2. (MULT, A1, A2, R) : The contents of A1 and A2 are multiplied. The result will be saved in R.
        3. (SUB, A1, A2, R) : The content of A2 is subtracted from A1. The result will be saved in R.
        4. (EQ, A1, A2, R) : The contents of A1 and A2 are compared. If they are equal, '1' (i.e., as a true value) will be saved in R; otherwise, '0' (i.e., as a false value) will be saved in R.
        5. (LT, A1, A2, R) : If the content of A1 is less than the content of A2, '1' will be saved in R; otherwise, '0' will be saved in R.
        6. (ASSIGN, A, R, ) : The content of A is assigned to R.
        7. (JPF, A, L, ) : If content of A is 'false', the control will be transferred to L; otherwise, next three address code will be executed.
        8. (JP, L, , ) : The control is transferred to L.
        9. (PRINT, A, , ) : The content of A will be printed to the standard output.
        """
        routines = {
            ActionSymbol.ASSIGN: self._action_assign,
            ActionSymbol.ASSIGN_EMPTY: self._action_assign_empty,
            ActionSymbol.PROCESS_ID: self._action_process_id,
            ActionSymbol.PROCESS_NUM: self._action_process_num,
            ActionSymbol.LABEL: self._action_label,
            ActionSymbol.SAVE: self._action_save,
            ActionSymbol.WHILE: self._action_while,
            ActionSymbol.LESS_THAN: self._action_less_than,
            ActionSymbol.ADDITION: self._action_addition,
            ActionSymbol.MULTIPLY: self._action_multiply,
            ActionSymbol.EQUALS: self._action_equals,
            ActionSymbol.JPF_SAVE: self._action_jpf_save,
            ActionSymbol.JUMP: self._action_jump,
            ActionSymbol.CONDITIONAL_JUMP: self._action_conditional_jump,
            ActionSymbol.PRINT: self._output_routine,
            ActionSymbol.PROCESS_ARRAY: self._action_process_array
        }

        routine = routines.get(
            action_symbol, lambda x: 'Invalid action_symbol')
        self._log(self._semantic_stack)
        self._log("line count: {0}".format(self._line_count))
        output = routine(current_input)
        self._log(output)
        self._log(self._semantic_stack)
        self._log("line count: {0}".format(self._line_count))
        self._log(self._symbol_table)

    def _write_semantic_error(self, error):
        self._semantic_errors.append(error)
        if self.OUTPUT:
            try:
                with open(self._errors_file, 'a+') as semantic_errors_file:
                    semantic_errors_file.write(
                        "%s\n" % error)
            except IOError:
                print("Could not write semantic error")
                sys.exit(1)

    def _write_empty_semantic_error(self):
        if self.OUTPUT:
            try:
                with open(self._errors_file, 'w') as semantic_errors_file:
                    semantic_errors_file.write(
                        "The input program is semantically correct.")
            except IOError:
                print("Could not write empty semantic error")
                sys.exit(1)

    def _write_empty_output(self):
        if self.OUTPUT:
            try:
                with open(self._output_file, 'w') as output_file:
                    output_file.write(
                        "The output code has not been generated")
            except IOError:
                print("Could not write empty output file")
                sys.exit(1)

    def _order_program_block(self, elem):
        return int(elem.split('\t')[0])

    def _write_address_code(self, **kwargs):
        if len(self._semantic_errors) > 0:
            return self._write_empty_output()
        output_line = kwargs.get('line', self._line_count)
        arguments = dict(enumerate(kwargs['arguments']))
        output_string = "{0}\t({1}, {arg[0]}, {arg[1]}, {arg[2]})\n".format(
            output_line, kwargs.get('operation'), arg=[arguments.get(x, '') for x in range(3)])

        output_line_index = kwargs.get(
            'line') if 'line' in kwargs else output_line
        self._program_block.insert(output_line_index, output_string)
        self._program_block.sort(key=self._order_program_block)
        if kwargs.get('increment', True):
            self._increment_line_count()
        if self.OUTPUT:
            try:
                with open(self._output_file, 'w') as output_file:
                    output_file.writelines(self._program_block)
            except IOError:
                print("Could not write output file")
                sys.exit(1)

    def _increment_line_count(self, count=1):
        self._line_count += count

    def get_line_count(self):
        return self._line_count

    def get_semantic_stack(self):
        return self._semantic_stack()

    def set_semantic_stack(self, items):
        self._semantic_stack.set_stack(items)

    def _action_assign(self, current_input):
        self._write_address_code(operation=ActionSymbol.ASSIGN.value, arguments=[
                                 self._semantic_stack.top(), self._semantic_stack.from_top(1)])
        self._semantic_stack.pop(2)
        return 'PROCESSED ASSIGN ACTION'

    def _action_assign_empty(self, current_input):
        self._write_address_code(operation=ActionSymbol.ASSIGN.value, arguments=[
                                 '#0', self._semantic_stack.top()])
        self._semantic_stack.pop(1)
        return 'PROCESSED EMPTY ASSIGN ACTION: %s' % current_input

    def _action_process_id(self, current_input):
        address = self._symbol_table.find_address(current_input)
        self._semantic_stack.push(address)
        return 'PROCESSED ID ACTION'

    def _action_process_num(self, current_input):
        # address = self._symbol_table.lookup(current_input)
        self._semantic_stack.push('#%s' % current_input)
        return 'PROCESSED NUM ACTION'

    def _action_label(self, current_input):
        self._semantic_stack.push(self._line_count)
        return 'PROCESSED LABEL ACTION'

    def _action_save(self, current_input):
        self._semantic_stack.push(self._line_count)
        self._increment_line_count(1)
        return 'PROCESSED SAVE ACTION'

    def _action_while(self, current_input):
        self._write_address_code(line=self._semantic_stack.top(), increment=False, operation=ActionSymbol.CONDITIONAL_JUMP.value, arguments=[
                                 self._semantic_stack.from_top(1),  self.get_line_count()+1])
        self._write_address_code(operation=ActionSymbol.JUMP.value, arguments=[
                                 self._semantic_stack.from_top(2)])
        self._semantic_stack.pop(3)
        return 'PROCESSED WHILE ACTION'

    def _action_less_than(self, current_input):
        temp_address = self._symbol_table.get_temporary_address()
        self._write_address_code(operation=ActionSymbol.LESS_THAN.value, arguments=[
                                 self._semantic_stack.from_top(1), self._semantic_stack.top(), temp_address])
        self._semantic_stack.pop(2)
        self._semantic_stack.push(temp_address)
        return 'PROCESSED LESS THAN ACTION'

    def _action_equals(self, current_input):
        temp_address = self._symbol_table.get_temporary_address()
        self._write_address_code(operation=ActionSymbol.EQUALS.value, arguments=[
                                 self._semantic_stack.from_top(1), self._semantic_stack.top(), temp_address])
        self._semantic_stack.pop(2)
        self._semantic_stack.push(temp_address)
        return 'PROCESSED EQUALS ACTION'

    def _action_addition(self, current_input):
        temp_address = self._symbol_table.get_temporary_address()
        self._write_address_code(operation=ActionSymbol.ADDITION.value, arguments=[
                                 self._semantic_stack.top(), self._semantic_stack.from_top(1), temp_address])
        self._semantic_stack.pop(2)
        self._semantic_stack.push(temp_address)
        return 'PROCESSED ADDITION ACTION'

    def _action_multiply(self, current_input):
        temp_address = self._symbol_table.get_temporary_address()
        self._write_address_code(operation=ActionSymbol.MULTIPLY.value, arguments=[
                                 self._semantic_stack.top(), self._semantic_stack.from_top(1), temp_address])
        self._semantic_stack.pop(2)
        self._semantic_stack.push(temp_address)
        return 'PROCESSED MULTIPLY ACTION'

    def _action_jpf_save(self, current_input):
        self._write_address_code(increment=False, line=self._semantic_stack.top(), operation=ActionSymbol.CONDITIONAL_JUMP.value, arguments=[
                                 self._semantic_stack.from_top(1), self._line_count+1])
        self._semantic_stack.pop(2)
        self._semantic_stack.push(self._line_count)
        self._increment_line_count(1)
        return 'PROCESSED JPF_SAVE ACTION'

    def _action_jump(self, current_input):
        self._write_address_code(
            increment=False, line=self._semantic_stack.top(), operation=ActionSymbol.JUMP.value, arguments=[self._line_count])
        self._semantic_stack.pop(1)
        return 'PROCESSED JUMP ACTION'

    def _action_conditional_jump(self, current_input):
        self._write_address_code(increment=False, line=self._semantic_stack.top(), operation=ActionSymbol.CONDITIONAL_JUMP.value, arguments=[
                                 self._semantic_stack.from_top(1), self._line_count])
        self._semantic_stack.pop(2)
        return 'PROCESSED CONDITIONAL JUMP ACTION'

    def _output_routine(self, current_input):
        self._write_address_code(operation=ActionSymbol.PRINT.value, arguments=[
                                 self._semantic_stack.top()])
        self._semantic_stack.pop(1)
        return 'PROCESSED PRINT ACTION'

    def _action_process_array(self, current_input):
        pass
        # return 'PROCESSED PRINT ACTION'
