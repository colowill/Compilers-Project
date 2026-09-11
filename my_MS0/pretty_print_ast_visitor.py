from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast

class PPASTVisitor(mini_ast.ASTVisitor):
    """Print the AST using indentation to show its structure."""

    def visit_program(self, program: program_ast.Program, indent=0):
        """To help you get started, this is my implementation of the visit_program() function.
        You don't have to use this code or even pretty print using indentation. 
        You could do something entirely different and prettier! 
        You could build a graphviz graph which would be beautiful!"""
        indent += 1
        indent_base = "\t"*indent
        program_str = "Program\n"
        program_str += f"{indent_base}Types\n"
        for tdecls in program.types:
            program_str += self.visit_type_declaration(tdecls, indent+1)
        program_str += f"{indent_base}Declarations\n"
        for decls in program.declarations:
            program_str += self.visit_declaration(decls, indent+1)
        program_str += f"\n{indent_base}Functions\n"
        for funcs in program.functions:
            program_str += self.visit_function(funcs, indent+1)
        return program_str

    def visit_declaration(self, declaration: program_ast.Declaration, indent):
        indent_0 = "\t"*indent
        type_str = declaration.type.accept(self)
        name_str = declaration.name.accept(self)
        result = f"{indent_0}Declaration: {type_str} {name_str}\n"
        return result

    def visit_type_declaration(self, type_declaration: program_ast.TypeDeclaration, indent):
        indent_0 = "\t"*(indent)
        indent_1 = "\t"*(indent+1)
        type_dec_name_str = type_declaration.name.accept(self)
        
        result = f"{indent_0}TypeDeclaration: {type_dec_name_str}\n"
        result += f"{indent_1}Fields\n"
        
        for field in type_declaration.fields:
            result += self.visit_declaration(field, indent+2)
        return result

    def visit_function(self, function: program_ast.Function, indent):
        indent_0 = "\t"*indent
        indent_1 = "\t"*(indent+1)
        indent_2 = "\t"*(indent+2)
        function_name = function.name.accept(self)
        function_return_type = function.ret_type.accept(self)
        result = f"{indent_0}Function: {function_name}\n"
        
        result += f"{indent_1}Parameters:\n"
        if not function.params:
            result += f"{indent_2}(none)\n"
        else:
            for params in function.params:
                result += self.visit_declaration(params, indent+2)
                
        result += f"{indent_1}Return Type: {function_return_type}\n"
        result += f"{indent_1}Body\n"
        # search through statement types to determine which one it is
        for statement in function.body:
            
                                
        return result
   
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

    def visit_statement(self, statement: statement_ast.Statement, indent):
        if isinstance(statement, statement_ast.AssignmentStatement):
            return self.visit_assignment_statement(statement, indent)
        elif isinstance(statement, statement_ast.ConditionalStatement):
            return self.visit_conditional_statement(statement, indent)
        elif isinstance(statement, statement_ast.BlockStatement):
            return self.visit_block_statement(statement, indent)
        elif isinstance(statement, statement_ast.WhileStatement):
            return self.visit_while_statement(statement, indent)
        elif isinstance(statement, statement_ast.DeleteStatement):
            return self.visit_delete_statement(statement, indent)
        elif isinstance(statement, statement_ast.InvocationStatement):
            return self.visit_invocation_statement(statement, indent)
        elif isinstance(statement, statement_ast.PrintLnStatement):
            return self.visit_println_statement(statement, indent)
        elif isinstance(statement, statement_ast.PrintStatement):
            return self.visit_print_statement(statement, indent)
        elif isinstance(statement, statement_ast.ReturnEmptyStatement):
            return self.visit_return_empty_statement(statement, indent)
        elif isinstance(statement, statement_ast.ReturnStatement):
            return self.visit_return_statement(statement, indent)
        return ""
        
    def visit_assignment_statement(self, assignment_statement: statement_ast.AssignmentStatement, indent):
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        
        result = f"{indent_0}Assignment\n"
        result += f"{indent_1}Target\n"
        result += self.visit_lvalue(assignment_statement.target, indent + 2)
        
        result += f"{indent_1}Source\n"
        result += self.visit_expression(assignment_statement.source, indent + 2)
        
        return result

    def visit_conditional_statement(self, conditional_statement: statement_ast.ConditionalStatement, indent):
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        
        result = f"{indent_0}ConditionalExpression\n"   
             
        result += f"{indent_1}Guard\n"
        result += self.visit_expression(conditional_statement.guard, indent + 2)
        
        result += f"{indent_1}ThenBlock\n"
        result += self.visit_block_statement(conditional_statement.then_block, indent + 2)
        
        if conditional_statement.else_block:
            result += f"{indent_1}ElseBlock\n"
            result += self.visit_block_statement(conditional_statement.else_block, indent + 2)
            
        return result

    def visit_block_statement(self, block_statement: statement_ast.BlockStatement, indent):
        indent_0 = "\t" * indent
        
        result = f"{indent_0}Block\n"
        for stmt in block_statement.statements:
            result += stmt.accept(self) if hasattr(stmt, 'accept') else str(stmt)
            
        return result

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