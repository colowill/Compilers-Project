import sys
from antlr4 import *
from Expr2Lexer import Expr2Lexer
from Expr2Parser import Expr2Parser

def main(argv):
	input_stream = FileStream(argv[1])
	lexer = Expr2Lexer(input_stream)
	stream = CommonTokenStream(lexer)
	parser = Expr2Parser(stream)
	tree = parser.start_()
	print(tree.children)

if __name__ == '__main__':
	main(sys.argv)
