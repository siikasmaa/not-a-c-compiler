from unittest import main, TestCase, skip
from unittest.mock import patch, mock_open
from context import Parser, Scanner, SymbolTable, SemanticAnalyzer, ActionSymbol


class TestSemanticAnalyzer(TestCase):

    valid_input = (
        b"/*==== Sample T1 ====*/\n"
        b"void main(void){\n"
        b"int a;\n"
        b"int b;\n"
        b"a = 10;\n"
        b"b = 0;\n"
        b"while (b < a){\n"
        b"b = b + 1;\n"
        b"if (b == 2){\n"
        b"output(a);\n"
        b"}\n"
        b"else{\n"
        b"if (6 < b){\n"
        b"break;\n"
        b"}\n"
        b"else {\n"
        b"output(b);\n"
        b"}\n"
        b"}\n"
        b"}\n"
        b"}\n"
    )

    expected_output = (
        "0	(ASSIGN, #0, 500, )\n"
        "1	(ASSIGN, #0, 504, )\n"
        "2	(ASSIGN, #0, 508, )\n"
        "3	(ASSIGN, #10, 504, )\n"
        "4	(ASSIGN, #0, 508, )\n"
        "5	(LT, 508, 504, 1000)\n"
        "6	(JPF, 1000, 18, )\n"
        "7	(ADD, #1, 508, 1004)\n"
        "8	(ASSIGN, 1004, 508, )\n"
        "9	(EQ, 508, #2, 1008)\n"
        "10	(JPF, 1008, 13, )\n"
        "11	(PRINT, 504, , )\n"
        "12	(JP, 17, , )\n"
        "13	(LT, #6, 508, 1012)\n"
        "14	(JPF, 1012, 16, )\n"
        "15	(JP, 17, , )\n"
        "16	(PRINT, 508, , )\n"
        "17	(JP, 5, , )\n"
    )

    valid_input_2 = (
        b"void main(void){\n"
        b"int arr[10];\n"
        b"int a;\n"
        b"int b;\n"
        b"a = 10 * 2 + 3 * (1 < 0);\n"
        b"b = 4 + 3;\n"
        b"output(a);\n"
        b"output(b);\n"
        b"}\n"
    )

    expected_output_2 = (
        "0	(ASSIGN, #0, 500, )\n"
        "1	(ASSIGN, #0, 508, )\n"
        "2	(ASSIGN, #0, 512, )\n"
        "3	(MULT, #2, #10, 1000)\n"
        "4	(LT, #1, #0, 1004)\n"
        "5	(MULT, 1004, #3, 1008)\n"
        "6	(ADD, 1008, 1000, 1012)\n"
        "7	(ASSIGN, 1012, 508, )\n"
        "8	(ADD, #3, #4, 1016)\n"
        "9	(ASSIGN, 1016, 512, )\n"
        "10	(PRINT, 508, , )\n"
        "11	(PRINT, 512, , )\n"
    )

    valid_input_3 = (
        b"void main(void){\n"
        b"int arr[10];\n"
        b"int var1;\n"
        b"int var2;\n"
        b"var1 = 1;\n"
        b"arr[0] = var1 = var2 = 5;\n"
        b"output(var1);\n"
        b"output(arr[0]);\n"
        b"arr[var1 = var2] = var2 = 7;\n"
        b"output(var1);\n"
        b"output(var2);\n"
        b"output(arr[5]);\n"
        b"}\n"
    )

    # TODO: CONTAINS ERROR AFTER LINE 3
    expected_output_3 = (
        "0	(ASSIGN, #0, 500, )\n"
        "1	(ASSIGN, #0, 508, )\n"
        "2	(ASSIGN, #0, 512, )\n"
        "3	(ASSIGN, #1, 508, )\n"
        "4	(ASSIGN, #5, 512, )\n"
        "5	(PRINT, 508, , )\n"
        "6	(PRINT, #0, , )\n"
        "7	(ASSIGN, #7, 512, )\n"
        "8	(PRINT, 508, , )\n"
        "9	(PRINT, 512, , )\n"
        "10	(PRINT, #5, , )\n"
    )

    def tearDown(self):
        SymbolTable().clear()

    def test_code_generation(self):
        self.maxDiff = None
        scanner = Scanner(self.valid_input)
        Parser(scanner, DEBUG=False, OUTPUT=False)
        with open('output/output.txt', 'r') as output_file:
            output = output_file.read()
        self.assertEqual(output, self.expected_output)

    def test_code_generation_2(self):
        self.maxDiff = None
        scanner = Scanner(self.valid_input_2)
        Parser(scanner, DEBUG=False, OUTPUT=False)
        with open('output/output.txt', 'r') as output_file:
            output = output_file.read()
        self.assertEqual(output, self.expected_output_2)

    def test_code_generation_3(self):
        self.maxDiff = None
        scanner = Scanner(self.valid_input_3)
        Parser(scanner, DEBUG=False, OUTPUT=False)
        with open('output/output.txt', 'r') as output_file:
            output = output_file.read()
        self.assertEqual(output, self.expected_output_3)

    @skip("TODO")
    def test_semantic(self):
        pass

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._action_assign')
    def test_code_gen(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.code_gen(ActionSymbol.ASSIGN, 'test')
        mocked_function.assert_called_with('test')

    def test_get_line_count(self):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._line_count = 101
        self.assertEqual(analyzer.get_line_count(), 101)
        analyzer._increment_line_count()
        self.assertEqual(analyzer.get_line_count(), 102)
        analyzer._increment_line_count(5)
        self.assertEqual(analyzer.get_line_count(), 107)

    def test_semantic_stack(self):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2', 'item3'])
        analyzer._semantic_stack.pop()
        self.assertEqual(analyzer.get_semantic_stack(), ['item1', 'item2'])
        analyzer._semantic_stack.pop(2)
        self.assertEqual(analyzer.get_semantic_stack(), [])

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_write_address_code(self, mocked_function):
        analyzer = SemanticAnalyzer()
        analyzer._line_count = 101
        analyzer._write_address_code(
            increment=False, line=110, operation='op', arguments=['item1'])
        self.assertEqual(analyzer.get_line_count(), 101)
        mocked_function.assert_called_with('./output/output.txt', 'w')
        mocked_function.return_value.__enter__().writelines.assert_called_with([
            '110\t(op, item1, , )\n'])
        analyzer._write_address_code(operation='test', arguments=[
                                     'item1', 'item2', 'item3'])
        self.assertEqual(analyzer.get_line_count(), 102)
        mocked_function.return_value.__enter__().writelines.assert_called_with(
            ['101\t(test, item1, item2, item3)\n', '110\t(op, item1, , )\n'])

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_assign(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_assign('test')
        mocked_function.assert_called_with(
            arguments=['item2', 'item1'], operation='ASSIGN')
        self.assertTrue(analyzer._semantic_stack.is_empty())

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_assign_empty(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1'])
        analyzer._action_assign_empty('test')
        mocked_function.assert_called_with(
            arguments=['#0', 'item1'], operation='ASSIGN')
        self.assertTrue(analyzer._semantic_stack.is_empty())

    @patch('compiler.symbol.SymbolTable.find_address', return_value=7)
    def test_action_process_id(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._action_process_id('test')
        self.assertEqual(analyzer.get_semantic_stack(), [7])

    def test_action_process_num(self):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._action_process_num(10)
        self.assertEqual(analyzer.get_semantic_stack(), ['#10'])

    def test_action_label(self):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._line_count = 100
        analyzer._action_label('while')
        self.assertEqual(analyzer.get_semantic_stack(), [100])
        self.assertEqual(analyzer.get_line_count(), 100)

    def test_action_save(self):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._line_count = 100
        analyzer._action_save('while')
        self.assertEqual(analyzer.get_semantic_stack(), [100])
        self.assertEqual(analyzer.get_line_count(), 101)

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_while(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._line_count = 2
        analyzer.set_semantic_stack(['item1', 'item2', 'item3'])
        analyzer._action_while('while')
        mocked_function.assert_any_call(
            arguments=['item2', 3], operation='JPF', increment=False, line='item3')
        mocked_function.assert_any_call(arguments=['item1'], operation='JP')
        self.assertEqual(mocked_function.call_count, 2)
        self.assertTrue(analyzer._semantic_stack.is_empty())

    @patch('compiler.symbol.SymbolTable.get_temporary_address', return_value=201)
    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_less_than(self, mock_address_code, mock_address):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_less_than('<')
        mock_address_code.assert_called_with(
            arguments=['item1', 'item2', 201], operation='LT')
        self.assertEqual(analyzer.get_semantic_stack(), [201])

    @patch('compiler.symbol.SymbolTable.get_temporary_address', return_value=201)
    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_equals(self, mock_address_code, mock_address):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_equals('<')
        mock_address_code.assert_called_with(
            arguments=['item1', 'item2', 201], operation='EQ')
        self.assertEqual(analyzer.get_semantic_stack(), [201])

    @patch('compiler.symbol.SymbolTable.get_temporary_address', return_value=201)
    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_addition(self, mock_address_code, mock_address):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_addition('+')
        mock_address_code.assert_called_with(
            arguments=['item2', 'item1', 201], operation='ADD')
        self.assertEqual(analyzer.get_semantic_stack(), [201])

    @patch('compiler.symbol.SymbolTable.get_temporary_address', return_value=201)
    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_multiply(self, mock_address_code, mock_address):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_multiply('+')
        mock_address_code.assert_called_with(
            arguments=['item2', 'item1', 201], operation='MULT')
        self.assertEqual(analyzer.get_semantic_stack(), [201])

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_jpf_save(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._line_count = 2
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_jpf_save('test')
        mocked_function.assert_called_with(
            arguments=['item1', 3], operation='JPF', increment=False, line='item2')
        self.assertEqual(analyzer.get_semantic_stack(), [2])
        self.assertEqual(analyzer._line_count, 3)

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_jump(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer._line_count = 2
        analyzer.set_semantic_stack(['item1'])
        analyzer._action_jump('test')
        mocked_function.assert_called_with(
            arguments=[2], increment=False, line='item1', operation='JP')
        self.assertTrue(analyzer._semantic_stack.is_empty())

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_action_conditional_jump(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1', 'item2'])
        analyzer._action_conditional_jump('test')
        mocked_function.assert_called_with(
            arguments=['item1', 0], increment=False, line='item2', operation='JPF')
        self.assertTrue(analyzer._semantic_stack.is_empty())

    @patch('compiler.semantic_analyzer.SemanticAnalyzer._write_address_code')
    def test_output_routine(self, mocked_function):
        analyzer = SemanticAnalyzer(OUTPUT=False)
        analyzer.set_semantic_stack(['item1'])
        analyzer._output_routine('test')
        mocked_function.assert_called_with(
            arguments=['item1'], operation='PRINT')
        self.assertTrue(analyzer._semantic_stack.is_empty())


if __name__ == "__main__":
    unittest.main()
