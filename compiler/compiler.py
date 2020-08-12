import sys
import scanner
import parser
import symbol


def main(path):
    try:
        with open(path, 'rb') as content_file:
            content = content_file.read()
    except IOError:
        print("Error: File not found.")
        return 1
    _scanner = scanner.Scanner(content)
    _parser = parser.Parser(_scanner)
    print(_symbol_table)
    return 0


if __name__ == '__main__':
    # TODO: Read input file from arguments
    status = main('./input.txt')
    sys.exit(status)
