from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast

class PPASTVisitor(mini_ast.ASTVisitor):
    """Print the AST using a visual ASCII tree structure to display nesting."""

    def _format_node(self, label: str, children: list, prefix: str = "") -> str:
        """Helper to render a parent node and format its child nodes with tree connectors."""
        lines = [f"{prefix}{label}"]
        count = len(children)
        for i, child in enumerate(children):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            if isinstance(child, str):
                lines.append(f"{prefix}{connector}{child}")
            elif child is not None:
                # If child is an AST node, visit it using the new child prefix
                if hasattr(child, 'accept'):
                    lines.append(child.accept(self, prefix=prefix + connector, child_prefix=child_prefix))
                else:
                    lines.append(f"{prefix}{connector}{str(child)}")
        return "\n".join(lines)

    # ==========================================
    # PROGRAM & DECLARATIONS
    # ==========================================

    def visit_program(self, program: program_ast.Program, prefix="", child_prefix=""):
        lines = ["Program"]
        
        all_children = []
        if hasattr(program, 'types') and program.types:
            all_children.extend(program.types)
        if hasattr(program, 'declarations') and program.declarations:
            all_children.extend(program.declarations)
        if hasattr(program, 'functions') and program.functions:
            all_children.extend(program.functions)

        count = len(all_children)
        for i, child in enumerate(all_children):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            next_child_prefix = "    " if is_last else "│   "
            if hasattr(child, 'accept'):
                lines.append(child.accept(self, prefix=connector, child_prefix=next_child_prefix))
            else:
                lines.append(f"{connector}{str(child)}")

        return "\n".join(lines)

    def visit_declaration(self, declaration: program_ast.Declaration, prefix="", child_prefix=""):
        type_str = declaration.type.accept(self) if hasattr(declaration.type, 'accept') else str(declaration.type)
        return f"{prefix}Decl ({declaration.name}: {type_str})"

    def visit_type_declaration(self, type_declaration: program_ast.TypeDeclaration, prefix="", child_prefix=""):
        lines = [f"{prefix}TypeDecl (struct {type_declaration.name})"]
        fields = getattr(type_declaration, 'fields', [])
        count = len(fields)
        for i, field in enumerate(fields):
            is_last = (i == count - 1)
            connector = child_prefix + ("└── " if is_last else "├── ")
            field_type = field.type.accept(self) if hasattr(field.type, 'accept') else str(field.type)
            lines.append(f"{connector}Field ({field.name}: {field_type})")
        return "\n".join(lines)

    def visit_function(self, function: program_ast.Function, prefix="", child_prefix=""):
        ret_type = function.return_type.accept(self) if hasattr(function.return_type, 'accept') else str(function.return_type)
        label = f"Function ({function.name} -> {ret_type})"
        
        children = []
        params = getattr(function, 'parameters', [])
        for p in params:
            p_type = p.type.accept(self) if hasattr(p.type, 'accept') else str(p.type)
            children.append(f"Param ({p.name}: {p_type})")
            
        decls = getattr(function, 'declarations', [])
        children.extend(decls)
        
        stmts = getattr(function, 'statements', [])
        children.extend(stmts)

        return self._format_node(label, children, prefix, child_prefix)

    # ==========================================
    # TYPES
    # ==========================================

    def visit_type(self, type_: type_ast.Type, prefix="", child_prefix=""):
        return f"{prefix}Type"

    def visit_int_type(self, int_type: type_ast.IntType, prefix="", child_prefix=""):
        return "int"

    def visit_bool_type(self, bool_type: type_ast.BoolType, prefix="", child_prefix=""):
        return "bool"

    def visit_struct_type(self, struct_type: type_ast.StructType, prefix="", child_prefix=""):
        return f"struct {struct_type.name}"

    def visit_return_type_real(self, return_type_real: type_ast.ReturnTypeReal, prefix="", child_prefix=""):
        return return_type_real.type.accept(self) if hasattr(return_type_real.type, 'accept') else str(return_type_real.type)

    def visit_return_type_void(self, return_type_void, prefix="", child_prefix=""):
        return "void"

    # ==========================================
    # STATEMENTS
    # ==========================================

    def visit_statement(self, statement: statement_ast.Statement, prefix="", child_prefix=""):
        return f"{prefix}Statement"

    def visit_assignment_statement(self, assignment_statement: statement_ast.AssignmentStatement, prefix="", child_prefix=""):
        return self._format_node("Assignment", [assignment_statement.target, assignment_statement.source], prefix, child_prefix)

    def visit_conditional_statement(self, conditional_statement: statement_ast.ConditionalStatement, prefix="", child_prefix=""):
        children = [conditional_statement.guard, conditional_statement.then_clause]
        if getattr(conditional_statement, 'else_clause', None):
            children.append(conditional_statement.else_clause)
        return self._format_node("Conditional (if-else)", children, prefix, child_prefix)

    def visit_block_statement(self, block_statement: statement_ast.BlockStatement, prefix="", child_prefix=""):
        stmts = getattr(block_statement, 'statements', [])
        return self._format_node("Block", stmts, prefix, child_prefix)

    def visit_while_statement(self, while_statement: statement_ast.WhileStatement, prefix="", child_prefix=""):
        return self._format_node("WhileLoop", [while_statement.guard, while_statement.body], prefix, child_prefix)

    def visit_delete_statement(self, delete_statement: statement_ast.DeleteStatement, prefix="", child_prefix=""):
        return self._format_node("Delete", [delete_statement.expression], prefix, child_prefix)

    def visit_invocation_statement(self, invocation_statement: statement_ast.InvocationStatement, prefix="", child_prefix=""):
        return self._format_node(f"InvokeStmt ({invocation_statement.name})", getattr(invocation_statement, 'arguments', []), prefix, child_prefix)

    def visit_println_statement(self, println_statement: statement_ast.PrintLnStatement, prefix="", child_prefix=""):
        return self._format_node("PrintLn", [println_statement.expression], prefix, child_prefix)

    def visit_print_statement(self, print_statement: statement_ast.PrintStatement, prefix="", child_prefix=""):
        return self._format_node("Print", [print_statement.expression], prefix, child_prefix)

    def visit_return_empty_statement(self, return_empty_statement: statement_ast.ReturnEmptyStatement, prefix="", child_prefix=""):
        return f"{prefix}Return (void)"

    def visit_return_statement(self, return_statement: statement_ast.ReturnStatement, prefix="", child_prefix=""):
        return self._format_node("Return", [return_statement.expression], prefix, child_prefix)

    # ==========================================
    # EXPRESSIONS
    # ==========================================

    def visit_expression(self, expression: expression_ast.Expression, prefix="", child_prefix=""):
        return f"{prefix}Expression"

    def visit_dot_expression(self, dot_expression: expression_ast.DotExpression, prefix="", child_prefix=""):
        return self._format_node(f"DotExpr (.{dot_expression.id})", [dot_expression.left], prefix, child_prefix)

    def visit_false_expression(self, false_expression: expression_ast.FalseExpression, prefix="", child_prefix=""):
        return f"{prefix}BoolLiteral (false)"

    def visit_true_expression(self, true_expression: expression_ast.TrueExpression, prefix="", child_prefix=""):
        return f"{prefix}BoolLiteral (true)"

    def visit_identifier_expression(self, identifier_expression: expression_ast.IdentifierExpression, prefix="", child_prefix=""):
        return f"{prefix}IdExpr ({identifier_expression.id})"

    def visit_new_expression(self, new_expression: expression_ast.NewExpression, prefix="", child_prefix=""):
        return f"{prefix}NewExpr ({new_expression.id})"

    def visit_null_expression(self, null_expression: expression_ast.NullExpression, prefix="", child_prefix=""):
        return f"{prefix}NullLiteral"

    def visit_read_expression(self, read_expression: expression_ast.ReadExpression, prefix="", child_prefix=""):
        return f"{prefix}ReadExpr"

    def visit_integer_expression(self, integer_expression: expression_ast.IntegerExpression, prefix="", child_prefix=""):
        return f"{prefix}IntLiteral ({integer_expression.value})"

    def visit_invocation_expression(self, invocation_expression: expression_ast.InvocationExpression, prefix="", child_prefix=""):
        return self._format_node(f"InvokeExpr ({invocation_expression.name})", getattr(invocation_expression, 'arguments', []), prefix, child_prefix)

    def visit_unary_expression(self, unary_expression: expression_ast.UnaryExpression, prefix="", child_prefix=""):
        return self._format_node(f"UnaryExpr ({unary_expression.operator})", [unary_expression.operand], prefix, child_prefix)

    def visit_binary_expression(self, binary_expression: expression_ast.BinaryExpression, prefix="", child_prefix=""):
        return self._format_node(f"BinaryExpr ({binary_expression.operator})", [binary_expression.left, binary_expression.right], prefix, child_prefix)

    # ==========================================
    # LVALUES
    # ==========================================

    def visit_lvalue(self, lvalue: lvalue_ast.LValue, prefix="", child_prefix=""):
        return f"{prefix}LValue"

    def visit_lvalue_dot(self, lvalue_dot: lvalue_ast.LValueDot, prefix="", child_prefix=""):
        return self._format_node(f"LValueDot (.{lvalue_dot.id})", [lvalue_dot.left], prefix, child_prefix)

    def visit_lvalue_id(self, lvalue_id: lvalue_ast.LValueID, prefix="", child_prefix=""):
        return f"{prefix}LValueID ({lvalue_id.id})"