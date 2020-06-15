import sys
import scanner

def main(path):
    try:
        with open(path, 'rb') as content_file:
            content = content_file.read()
    except IOError:
        print("Error: File not found.")
        return 1

    _scanner = scanner.Scanner(content)
    output = _scanner()
    while output:
      output = _scanner()
    return 0


if __name__ == '__main__':
    # TODO: Read input file from arguments
    status = main('../input.txt')
    sys.exit(status)
