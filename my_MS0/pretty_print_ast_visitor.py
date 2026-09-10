from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast

class PPASTVisitor(mini_ast.ASTVisitor):
    """Print the AST using indentation to show its structure."""

    def visit_program(self, program: program_ast.Program, indent=0):
        """To help you get started, this is my implementation of the visit_program() function.
        You don't have to use this code or even pretty print using indentation. 
        You could do something entirely different and prettier! 
        You could build a graphviz graph which would be beautiful!"""
        program_str = "Type (Struct) Declarations:\n"
        for tdecls in program.types:
            program_str += self.visit_type_declaration(tdecls, indent+1)
        program_str += "Declarations:\n"
        for decls in program.declarations:
            program_str += self.visit_declaration(decls, indent+1)
        program_str += "\nFunctions:\n"
        for funcs in program.functions:
            program_str += self.visit_function(funcs, indent+1)
        return program_str

    def visit_declaration(self, declaration: program_ast.Declaration, indent):
        
        indent_str = "\t"*indent
        type_str = declaration.type.accept(self)
        name_str = declaration.name.accept(self)
        result = f"{indent_str}Declaration: {type_str} {name_str}\n"
        return result

    def visit_type_declaration(self, type_declaration: program_ast.TypeDeclaration, indent):
        return "foo"

    def visit_function(self, function: program_ast.Function, indent):
        return "foo"
   
    def visit_type(self, type_: type_ast.Type):
        pass

    def visit_int_type(self, int_type: type_ast.IntType):
        return "int"

    def visit_bool_type(self, bool_type: type_ast.BoolType):
        return "bool"

    def visit_struct_type(self, struct_type: type_ast.StructType):
        return struct_type.name.accept(self)
    
    def visit_return_type_real(self, return_type_real: type_ast.ReturnTypeReal):
        pass
    
    def visit_return_type_void(self, return_type_void) -> mini_ast.Any:
        pass

    #def visit_statement(self, statement: statement_ast.Statement):
    #    pass
        
    def visit_assignment_statement(self, assignment_statement: statement_ast.AssignmentStatement):
        pass

    def visit_conditional_statement(self, conditional_statement: statement_ast.ConditionalStatement):
        pass

    def visit_block_statement(self, block_statement: statement_ast.BlockStatement):
        pass

    def visit_while_statement(self, while_statement: statement_ast.WhileStatement):
        pass

    def visit_delete_statement(self, delete_statement: statement_ast.DeleteStatement):
        pass

    def visit_invocation_statement(self, invocation_statement: statement_ast.InvocationStatement):
        pass

    def visit_println_statement(self, println_statement: statement_ast.PrintLnStatement):
        pass

    def visit_print_statement(self, print_statement: statement_ast.PrintStatement):
        pass

    def visit_return_empty_statement(self, return_empty_statement: statement_ast.ReturnEmptyStatement):
        pass

    def visit_return_statement(self, return_statement: statement_ast.ReturnStatement):
        pass

    #def visit_expression(self, expression: expression_ast.Expression):
    #    pass

    def visit_dot_expression(self, dot_expression: expression_ast.DotExpression):
        pass

    def visit_false_expression(self, false_expression: expression_ast.FalseExpression):
        pass

    def visit_true_expression(self, true_expression: expression_ast.TrueExpression):
        pass

    def visit_identifier_expression(self, identifier_expression: expression_ast.IdentifierExpression):
        return identifier_expression.id

    def visit_new_expression(self, new_expression: expression_ast.NewExpression):
        pass

    def visit_null_expression(self, null_expression: expression_ast.NullExpression):
        pass

    def visit_read_expression(self, read_expression: expression_ast.ReadExpression):
        pass

    def visit_integer_expression(self, integer_expression: expression_ast.IntegerExpression):
        pass

    def visit_invocation_expression(self, invocation_expression: expression_ast.InvocationExpression):
        pass

    def visit_unary_expression(self, unary_expression: expression_ast.UnaryExpression):
        pass

    def visit_binary_expression(self, binary_expression: expression_ast.BinaryExpression):
        pass

    #def visit_lvalue(self, lvalue: lvalue_ast.LValue):
    #    pass
        
    def visit_lvalue_dot(self, lvalue_dot: lvalue_ast.LValueDot):
        pass

    def visit_lvalue_id(self, lvalue_id: lvalue_ast.LValueID):
        pass