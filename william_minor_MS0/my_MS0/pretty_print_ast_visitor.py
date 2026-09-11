from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast

class PPASTVisitor(mini_ast.ASTVisitor):
    """Print the AST using indentation to show its structure."""

    def visit_program(self, program: program_ast.Program, indent=0):
        indent += 1
        indent_base = "\t" * indent
        program_str = "Program\n"
        program_str += f"{indent_base}Types\n"
        for tdecls in program.types:
            program_str += self.visit_type_declaration(tdecls, indent + 1)
        program_str += f"{indent_base}Declarations\n"
        for decls in program.declarations:
            program_str += self.visit_declaration(decls, indent + 1)
        program_str += f"\n{indent_base}Functions\n"
        for funcs in program.functions:
            program_str += self.visit_function(funcs, indent + 1)
        return program_str

    def visit_declaration(self, declaration: program_ast.Declaration, indent):
        indent_0 = "\t" * indent
        type_str = declaration.type.accept(self) if hasattr(declaration.type, 'accept') else str(declaration.type)
        name_str = declaration.name.accept(self) if hasattr(declaration.name, 'accept') else str(declaration.name)
        result = f"{indent_0}Declaration: {type_str} {name_str}\n"
        return result

    def visit_type_declaration(self, type_declaration: program_ast.TypeDeclaration, indent):
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        type_dec_name_str = type_declaration.name.accept(self) if hasattr(type_declaration.name, 'accept') else str(type_declaration.name)
        
        result = f"{indent_0}TypeDeclaration: {type_dec_name_str}\n"
        result += f"{indent_1}Fields\n"
        
        for field in type_declaration.fields:
            result += self.visit_declaration(field, indent + 2)
        return result

    def visit_function(self, function: program_ast.Function, indent):
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        indent_2 = "\t" * (indent + 2)
        function_name = function.name.accept(self) if hasattr(function.name, 'accept') else str(function.name)
        function_return_type = function.ret_type.accept(self) if hasattr(function.ret_type, 'accept') else str(function.ret_type)
        result = f"{indent_0}Function: {function_name}\n"
        
        result += f"{indent_1}Parameters:\n"
        if not function.params:
            result += f"{indent_2}(none)\n"
        else:
            for params in function.params:
                result += self.visit_declaration(params, indent + 2)
                
        result += f"{indent_1}Return Type: {function_return_type}\n"
        result += f"{indent_1}Body\n"
        for statement in function.body:
            result += self.visit_statement(statement, indent + 2)
                                
        return result
   
    def visit_type(self, type_: type_ast.Type):
        if isinstance(type_, type_ast.IntType):
            return self.visit_int_type(type_)
        elif isinstance(type_, type_ast.BoolType):
            return self.visit_bool_type(type_)
        elif isinstance(type_, type_ast.StructType):
            return self.visit_struct_type(type_)
        return ""

    def visit_int_type(self, int_type: type_ast.IntType):
        return "int"

    def visit_bool_type(self, bool_type: type_ast.BoolType):
        return "bool"

    def visit_struct_type(self, struct_type: type_ast.StructType):
        return struct_type.name.accept(self) if hasattr(struct_type.name, 'accept') else str(struct_type.name)
    
    def visit_return_type_real(self, return_type_real: type_ast.ReturnTypeReal):
        return return_type_real.type.accept(self) if hasattr(return_type_real.type, 'accept') else str(return_type_real.type)
    
    def visit_return_type_void(self, return_type_void) -> mini_ast.Any:
        return "void"

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
            result += self.visit_statement(stmt, indent + 1)
            
        return result

    def visit_while_statement(self, while_statement: statement_ast.WhileStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        
        result = f"{indent_0}While\n"
        result += f"{indent_1}Guard\n"
        result += self.visit_expression(while_statement.guard, indent + 2)
        
        result += f"{indent_1}Body\n"
        if isinstance(while_statement.body, statement_ast.BlockStatement):
            result += self.visit_block_statement(while_statement.body, indent + 2)
        else:
            result += self.visit_statement(while_statement.body, indent + 2)
            
        return result

    def visit_delete_statement(self, delete_statement: statement_ast.DeleteStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        result = f"{indent_0}Delete\n"
        result += self.visit_expression(delete_statement.expression, indent + 1)
        return result

    def visit_invocation_statement(self, invocation_statement: statement_ast.InvocationStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        result = f"{indent_0}InvocationStatement\n"
        result += self.visit_expression(invocation_statement.expression, indent + 1)
        return result

    def visit_println_statement(self, println_statement: statement_ast.PrintLnStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        result = f"{indent_0}PrintLn\n"
        result += self.visit_expression(println_statement.expression, indent + 1)
        return result

    def visit_print_statement(self, print_statement: statement_ast.PrintStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        result = f"{indent_0}Print\n"
        result += self.visit_expression(print_statement.expression, indent + 1)
        return result

    def visit_return_empty_statement(self, return_empty_statement: statement_ast.ReturnEmptyStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        return f"{indent_0}Return\n"

    def visit_return_statement(self, return_statement: statement_ast.ReturnStatement, indent: int) -> str:
        indent_0 = "\t" * indent
        result = f"{indent_0}Return\n"
        if return_statement.expression:
            result += self.visit_expression(return_statement.expression, indent + 1)
        return result

    def visit_expression(self, expression: expression_ast.Expression, indent: int) -> str:
        if isinstance(expression, expression_ast.BinaryExpression):
            return self.visit_binary_expression(expression, indent)
        elif isinstance(expression, expression_ast.UnaryExpression):
            return self.visit_unary_expression(expression, indent)
        elif isinstance(expression, expression_ast.IntegerExpression):
            return self.visit_integer_expression(expression, indent)
        elif isinstance(expression, expression_ast.IdentifierExpression):
            return self.visit_identifier_expression(expression, indent)
        elif isinstance(expression, expression_ast.DotExpression):
            return self.visit_dot_expression(expression, indent)
        elif isinstance(expression, expression_ast.InvocationExpression):
            return self.visit_invocation_expression(expression, indent)
        elif isinstance(expression, expression_ast.NewExpression):
            return self.visit_new_expression(expression, indent)
        elif isinstance(expression, expression_ast.TrueExpression):
            return self.visit_true_expression(expression, indent)
        elif isinstance(expression, expression_ast.FalseExpression):
            return self.visit_false_expression(expression, indent)
        elif isinstance(expression, expression_ast.NullExpression):
            return self.visit_null_expression(expression, indent)
        elif isinstance(expression, expression_ast.ReadExpression):
            return self.visit_read_expression(expression, indent)
        return ""

    def visit_dot_expression(self, dot_expression: expression_ast.DotExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        result = f"{indent_0}DotExpression\n"
        result += f"{indent_1}Left\n"
        result += self.visit_expression(dot_expression.left, indent + 2)
        id_str = dot_expression.id.id if hasattr(dot_expression.id, 'id') else dot_expression.id
        result += f"{indent_1}Id: {id_str}\n"
        return result

    def visit_false_expression(self, false_expression: expression_ast.FalseExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        return f"{indent_0}False\n"

    def visit_true_expression(self, true_expression: expression_ast.TrueExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        return f"{indent_0}True\n"

    def visit_identifier_expression(self, identifier_expression: expression_ast.IdentifierExpression, indent: int = 0) -> str:
        if indent == 0:
            return identifier_expression.id
        indent_0 = "\t" * indent
        return f"{indent_0}{identifier_expression.id}\n"

    def visit_new_expression(self, new_expression: expression_ast.NewExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        id_str = new_expression.id.id if hasattr(new_expression.id, 'id') else new_expression.id
        return f"{indent_0}New: {id_str}\n"

    def visit_null_expression(self, null_expression: expression_ast.NullExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        return f"{indent_0}Null\n"

    def visit_read_expression(self, read_expression: expression_ast.ReadExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        return f"{indent_0}Read\n"

    def visit_integer_expression(self, integer_expression: expression_ast.IntegerExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        return f"{indent_0}Integer: {integer_expression.value}\n"

    def visit_invocation_expression(self, invocation_expression: expression_ast.InvocationExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        name_str = invocation_expression.name.id if hasattr(invocation_expression.name, 'id') else invocation_expression.name
        
        result = f"{indent_0}InvocationExpression: {name_str}\n"
        result += f"{indent_1}Arguments\n"
        for arg in invocation_expression.arguments:
            result += self.visit_expression(arg, indent + 2)
        return result

    def visit_unary_expression(self, unary_expression: expression_ast.UnaryExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        op_str = unary_expression.operator.value if hasattr(unary_expression.operator, 'value') else str(unary_expression.operator)
        
        result = f"{indent_0}UnaryExpression\n"
        result += f"{indent_1}Operator: {op_str}\n"
        result += self.visit_expression(unary_expression.operand, indent + 2)
        return result

    def visit_binary_expression(self, binary_expression: expression_ast.BinaryExpression, indent: int) -> str:
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        op_str = binary_expression.operator.value if hasattr(binary_expression.operator, 'value') else str(binary_expression.operator)
        
        result = f"{indent_0}BinaryExpression\n"
        result += f"{indent_1}Operator: {op_str}\n"
        result += f"{indent_1}Left\n"
        result += self.visit_expression(binary_expression.left, indent + 2)
        result += f"{indent_1}Right\n"
        result += self.visit_expression(binary_expression.right, indent + 2)
        return result

    def visit_lvalue(self, lvalue: lvalue_ast.LValue, indent: int) -> str:
        if isinstance(lvalue, lvalue_ast.LValueID):
            return self.visit_lvalue_id(lvalue, indent)
        elif isinstance(lvalue, lvalue_ast.LValueDot):
            return self.visit_lvalue_dot(lvalue, indent)
        return ""
        
    def visit_lvalue_dot(self, lvalue_dot: lvalue_ast.LValueDot, indent: int) -> str:
        indent_0 = "\t" * indent
        indent_1 = "\t" * (indent + 1)
        id_str = lvalue_dot.id.id if hasattr(lvalue_dot.id, 'id') else lvalue_dot.id
        
        result = f"{indent_0}LValue (LvalueDot)\n"
        result += self.visit_lvalue(lvalue_dot.left, indent + 1)
        result += f"{indent_1}Id: {id_str}\n"
        return result

    def visit_lvalue_id(self, lvalue_id: lvalue_ast.LValueID, indent: int) -> str:
        indent_0 = "\t" * indent
        id_str = lvalue_id.id.id if hasattr(lvalue_id.id, 'id') else lvalue_id.id
        return f"{indent_0}LValue (LvalueId): {id_str}\n"