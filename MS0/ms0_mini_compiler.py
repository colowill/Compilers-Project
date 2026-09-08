import sys
from antlr4 import *
from MiniLexer import MiniLexer
from MiniParser import MiniParser
from mini_ast_visitor import MiniToASTVisitor

def main(argv):
    input_stream = FileStream(argv[1])  # create a stream of characters from the input file (e.g., test.mini)
    lexer = MiniLexer(input_stream)     # create a lexer for the input stream
    stream = CommonTokenStream(lexer)   
    parser = MiniParser(stream)         # create a parser for the stream of tokens
    program_ctx = parser.program()      # recursively parse, starting with the top-level 'program' construct of Mini.g4

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors.")
    else:
        print("Parse successful.")
        """Create AST."""
        mini_ast_visitor = MiniToASTVisitor()
        mini_ast = mini_ast_visitor.visitProgram(program_ctx)
        print("AST created.")
        print(mini_ast)

        """Pretty print AST.
        Milestone 0: Implement this visitor"""
        #pp_visitor = PPASTVisitor()
        #pp_str = mini_ast.accept(pp_visitor)
        #print(pp_str)


if __name__ == '__main__':
    main(sys.argv)


