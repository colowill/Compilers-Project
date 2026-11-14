import os
import sys
import argparse
from antlr4 import *
from ir_visitor import IRVisitor
from MiniLexer import MiniLexer
from MiniParser import MiniParser
from mini_ast_visitor import MiniToASTVisitor
from pretty_print_ast_visitor import PPASTVisitor
from rv32_transformer import RV32Transformer
from semantics import StaticSemanticASTVisitor
 
def main(argv):
    arg_parser = argparse.ArgumentParser(description="Mini compiler")
    arg_parser.add_argument("file", help="the .mini file to compile")
    arg_parser.add_argument("-p", action="store_true", help="pretty-print the AST")
    arg_parser.add_argument("-s", action="store_true", help="print the symbol tables")
    arg_parser.add_argument("-I", action="store_true", help="print intermediate representation")
    args = arg_parser.parse_args(argv[1:])

    input_stream = FileStream(args.file)
    lexer = MiniLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = MiniParser(stream)
    program_ctx = parser.program()

    num_errors = 0

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors.")
    else:
        print("Parse successful.")

        mini_ast_visitor = MiniToASTVisitor()
        mini_ast = mini_ast_visitor.visitProgram(program_ctx)
        print("AST created:")

        if args.p:
            pp_visitor = PPASTVisitor()
            print(mini_ast.accept(pp_visitor))

        semantic_visitor = StaticSemanticASTVisitor()
        num_errors = mini_ast.accept(semantic_visitor)

        if args.s:
            scopes = [semantic_visitor.symbols.scope[0]] + semantic_visitor.symbols.history
            for scope in scopes:
                print(scope["scope"], scope["symbols"])

        if num_errors == 0:
            ir_visitor = IRVisitor()
            ir_body = mini_ast.accept(ir_visitor)

            if args.I:
                print(ir_body)

            rv32_body = RV32Transformer(ir_body).run()

            with open(os.path.splitext(args.file)[0] + ".s", "w") as pen:
                pen.write(rv32_body)
            sys.exit(0)

    print(f"ERRORS FOUND {num_errors}")

if __name__ == '__main__':
    main(sys.argv)