import sys
import os


class SemanticError():
    """
      1. Scoping: all variables must be declared either globally or in the current scope, before they can be used in any expression. Besides, every function should be defined before it can be invoked. These are required in order to be able to implement a one pass compiler. If a variable or a function identifier with token ID lacks such a declaration or definition, respectively, the error should be reported by the message: #lineno: Semantic Error! 'ID' is not defined, where 'ID' is the undefined variable/function.
      2.  Void type: when defining a single variable or an array, the type cannot be void. In such a case, report the error by the error message: #lineno: Semantic Error! Illegal type of void for 'ID', where ID is the variable or array with the illegal type.
      3. Actual and formal parameters number matching: when invoking a function, the number of arguments passed via invocation must match the number of parameters that has been given in the function definition. Otherwise, the error should be reported by the message: #lineno: semantic error! Mismatch in numbers of arguments of 'ID', where 'ID' is the function that has been invoked illegally.
      4. Break statement: if a 'break' statement is not within any while loops or switch statements, signal the error by the message: #lineno: Semantic Error! No 'while' or 'switch' found for 'break'.
      5. Type mismatch: in a numerical and/or comparison operation, the types of operands on both sides of the operation should match. Otherwise, the error should be reported by the message: #lineno: Semantic Error! Type mismatch in operands, Got 'Y' instead of 'X', where 'Y' is the mismatched type and 'X' is the expected type.
      6. Actual and formal parameter type matching: when invoking a function, the type of each argument passed via invocation must match the type of associated parameter in the function definition. Otherwise, the error should be reported by the message: #lineno: Semantic Error! Mismatch in type of argument N for 'ID'. Expected 'X' but got 'Y' instead', where 'N' is the number of the argument with the illegal type, 'ID' is the function's name, 'X' is the expected type, and 'Y' is the illegal type.
    """


class SemanticAnalyzer():

    _output_file = './output/output.txt'
    _errors_file = "./output/semantic_error.txt"

    def __init__(self, scanner):
        self._semantic_stack = []
        self._semantic_errors = []
        # Clear files
        try:
            os.mkdir('./output')
        except FileExistsError:
            pass
        with open(self._output_file, 'w') as output_file:
            output_file.write("")
        with open(self._errors_file, 'w') as errors_file:
            errors_file.write("")

    def semantic_check(self):
        # Semantic analysis is performed in a manner very similar to one explained in Lecture 6 for intermediate code generation.
        #  That is, the parser calls a function (let's call it 'semantic_check') in certain stages in the non-terminals subroutines.
        #  Parser passes an appropriate action symbol as an argument to the semantic analyser (i.e., 'semantic_check' function).
        # Semantic analyser then executes the associated semantic routine, and the control returns to the parser.
        pass

    def code_gen(self):
        # executes the appropriate semantic routine associated with the received action symbol (based on the technique introduced in Lecture 6).
        # Generated three-address codes are saved in an output text file called 'output.txt'.
        # Parser calls a function called 'code_gen' and sends an action symbol as an argument to 'code_gen' at appropriate times during parsing.
        # The code generator is called by the parser to perform a code generation task, which can be modifying the semantic stack and/or generating a number of three address codes.

        # Note that every three address code is preceded by a line number starting from zero.
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
        pass

    def _write_semantic_errors_file(self):
        # Should ouput "The input program is semantically correct" if no errors
        pass
