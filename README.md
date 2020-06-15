# C- compiler with Python

## Compiler Specification

- Compiler includes four main modules for lexical analysis, syntax analysis, semantic analysis and intermediate code generation
- Compiler is __one-pass__; the input program is read only once and the four main parts of the compiler work in a pipeline fashion.
- The input to the compiler (through a file called _input.txt_) is a text file including a C-minus program, which has to be translated.

## C-minus

C-minus, a simplified version of the C programming language. In this project, we implement a one-pass compiler for a slightly modified version of C-minus.

## Part 1

In this part of the project, you implement a scanner to recognize the tokens of input C-minus programs.

