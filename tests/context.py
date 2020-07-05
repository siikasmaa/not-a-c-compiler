
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from compiler.scanner import Scanner
from compiler.token import Token, TokenType
from compiler.parser import Parser

