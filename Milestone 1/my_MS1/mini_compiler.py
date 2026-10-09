import sys
from antlr4 import *
from MiniLexer import MiniLexer
from MiniParser import MiniParser
from mini_ast_visitor import MiniToASTVisitor
from pretty_print_ast_visitor import PPASTVisitor
from semantics import StaticSemanticASTVisitor

def main(argv):
    # Check if --no-pp flag is passed
    show_pp = "--no-pp" not in argv
    
    # Filter out flags to get the source file path
    args = [arg for arg in argv[1:] if not arg.startswith("--")]
    if not args:
        print("Usage: python3 mini_compiler.py [--no-pp] <filename>")
        return

    input_stream = FileStream(args[0])  # create character stream from input file
    lexer = MiniLexer(input_stream)
    stream = CommonTokenStream(lexer)   
    parser = MiniParser(stream)
    program_ctx = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors.")
    else:
        print("Parse successful.")
        
        # Create AST
        mini_ast_visitor = MiniToASTVisitor()
        mini_ast = mini_ast_visitor.visitProgram(program_ctx)
        print("AST created:")

        # Pretty print AST (only if flag is not set)
        if show_pp:
            pp_visitor = PPASTVisitor()
            pp_str = mini_ast.accept(pp_visitor)
            print(pp_str)
        
        # Semantic Analysis
        semantic_visitor = StaticSemanticASTVisitor()
        num_errors = mini_ast.accept(semantic_visitor)
        print(num_errors)

if __name__ == '__main__':
    main(sys.argv)