# Generated from Expr2.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .Expr2Parser import Expr2Parser
else:
    from Expr2Parser import Expr2Parser

# This class defines a complete listener for a parse tree produced by Expr2Parser.
class Expr2Listener(ParseTreeListener):

    # Enter a parse tree produced by Expr2Parser#start_.
    def enterStart_(self, ctx:Expr2Parser.Start_Context):
        pass

    # Exit a parse tree produced by Expr2Parser#start_.
    def exitStart_(self, ctx:Expr2Parser.Start_Context):
        pass


    # Enter a parse tree produced by Expr2Parser#expr.
    def enterExpr(self, ctx:Expr2Parser.ExprContext):
        pass

    # Exit a parse tree produced by Expr2Parser#expr.
    def exitExpr(self, ctx:Expr2Parser.ExprContext):
        pass


    # Enter a parse tree produced by Expr2Parser#atom.
    def enterAtom(self, ctx:Expr2Parser.AtomContext):
        pass

    # Exit a parse tree produced by Expr2Parser#atom.
    def exitAtom(self, ctx:Expr2Parser.AtomContext):
        pass



del Expr2Parser