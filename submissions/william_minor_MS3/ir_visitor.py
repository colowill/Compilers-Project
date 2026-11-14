import mini_ast, statement_ast, expression_ast, lvalue_ast

class IRVisitor(mini_ast.ASTVisitor):
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
        self.current_func = None

    def new_temp(self):
        t = f"%t{self.temp_count}"
        self.temp_count += 1
        return t

    def new_label(self, name="label"):
        label = f"_{name}_{self.label_count}"
        self.label_count += 1
        return label

    def get_ir_text(self):
        return "\n".join(self.instructions)

    def visit_program(self, program):
        for type_decl in program.types:
            type_decl.accept(self)
        for decl in program.declarations:
            decl.accept(self)
        for func in program.functions:
            func.accept(self)
        return self.get_ir_text()

    def visit_type_declaration(self, type_declaration):
        name = type_declaration.name.id
        self.instructions.append(f"struct {name}:")
        for field in type_declaration.fields:
            ftype = field.type.accept(self)
            self.instructions.append(f"  field {field.name.id} : {ftype}")
        return None

    def visit_declaration(self, declaration):
        var_name = declaration.name.id
        vtype = declaration.type.accept(self)
        self.instructions.append(f"global @{var_name} : {vtype}")
        return None

    def visit_function(self, function):
        func_name = function.name.id
        self.current_func = func_name
        self.instructions.append(f"function {func_name}:")
        
        self.instructions.append("  # Prologue")
        self.instructions.append("  addi sp, sp, -8")
        self.instructions.append("  sw ra, 4(sp)")
        self.instructions.append("  sw s0, 0(sp)")
        self.instructions.append("  addi s0, sp, 8")

        for i, param in enumerate(function.params):
            pname = param.name.id
            self.instructions.append(f"  sw a{i}, @{pname}")

        for local in function.locals:
            lname = local.name.id
            self.instructions.append(f"  alloc @{lname}")

        for stmt in function.body:
            stmt.accept(self)

        self.instructions.append(f"_{func_name}_exit:")
        self.instructions.append("  # Epilogue")
        self.instructions.append("  lw s0, 0(sp)")
        self.instructions.append("  lw ra, 4(sp)")
        self.instructions.append("  addi sp, sp, 8")
        self.instructions.append("  ret")
        return None

    def visit_int_type(self, int_type):
        return "int"

    def visit_bool_type(self, bool_type):
        return "bool"

    def visit_struct_type(self, struct_type):
        return struct_type.name.id

    def visit_return_type_real(self, return_type_real):
        return return_type_real.type_.accept(self)

    def visit_return_type_void(self, return_type_void):
        return "void"

    def visit_assignment_statement(self, statement):
        src_result = statement.source.accept(self)
        
        if isinstance(statement.target, lvalue_ast.LValueID):
            var_name = statement.target.id.id
            self.instructions.append(f"  sw {src_result}, @{var_name}")
        elif isinstance(statement.target, lvalue_ast.LValueDot):
            left_result = statement.target.left.accept(self)
            field_name = statement.target.id.id
            self.instructions.append(f"  store_field {src_result}, {left_result}, {field_name}")
        return None

    def visit_block_statement(self, block_statement):
        for stmt in block_statement.statements:
            stmt.accept(self)
        return None

    def visit_conditional_statement(self, statement):
        guard_res = statement.guard.accept(self)
        else_label = self.new_label("else")
        end_label = self.new_label("endif")

        self.instructions.append(f"  beqz {guard_res}, {else_label}")
        statement.then_block.accept(self)
        self.instructions.append(f"  j {end_label}")
        
        self.instructions.append(f"{else_label}:")
        if statement.else_block:
            statement.else_block.accept(self)
        
        self.instructions.append(f"{end_label}:")
        return None

    def visit_while_statement(self, while_statement):
        loop_label = self.new_label("while_loop")
        end_label = self.new_label("while_end")

        self.instructions.append(f"{loop_label}:")
        guard_res = while_statement.guard.accept(self)
        self.instructions.append(f"  beqz {guard_res}, {end_label}")
        
        while_statement.body.accept(self)
        self.instructions.append(f"  j {loop_label}")
        self.instructions.append(f"{end_label}:")
        return None

    def visit_delete_statement(self, delete_statement):
        exp_res = delete_statement.expression.accept(self)
        self.instructions.append(f"  delete {exp_res}")
        return None

    def visit_invocation_statement(self, invocation_statement):
        invocation_statement.expression.accept(self)
        return None

    def visit_println_statement(self, println_statement):
        val_res = println_statement.expression.accept(self)
        self.instructions.append(f"  println {val_res}")
        return None

    def visit_print_statement(self, print_statement):
        val_res = print_statement.expression.accept(self)
        self.instructions.append(f"  print {val_res}")
        return None

    def visit_return_empty_statement(self, return_empty_statement):
        self.instructions.append(f"  j _{self.current_func}_exit")
        return None

    def visit_return_statement(self, return_statement):
        val_res = return_statement.expression.accept(self)
        self.instructions.append(f"  mv a0, {val_res}")
        self.instructions.append(f"  j _{self.current_func}_exit")
        return None

    def visit_integer_expression(self, integer_expression):
        t = self.new_temp()
        self.instructions.append(f"  li {t}, {integer_expression.value}")
        return t

    def visit_true_expression(self, true_expression):
        t = self.new_temp()
        self.instructions.append(f"  li {t}, 1")
        return t

    def visit_false_expression(self, false_expression):
        t = self.new_temp()
        self.instructions.append(f"  li {t}, 0")
        return t

    def visit_null_expression(self, null_expression):
        t = self.new_temp()
        self.instructions.append(f"  li {t}, 0")
        return t

    def visit_read_expression(self, read_expression):
        t = self.new_temp()
        self.instructions.append(f"  call read_int, {t}")
        return t

    def visit_identifier_expression(self, identifier_expression):
        t = self.new_temp()
        var_name = identifier_expression.id
        self.instructions.append(f"  lw {t}, @{var_name}")
        return t

    def visit_new_expression(self, new_expression):
        t = self.new_temp()
        struct_name = new_expression.id.id
        self.instructions.append(f"  new {t}, {struct_name}")
        return t

    def visit_dot_expression(self, dot_expression):
        left_result = dot_expression.left.accept(self)
        field_name = dot_expression.id.id
        t = self.new_temp()
        self.instructions.append(f"  load_field {t}, {left_result}, {field_name}")
        return t

    def visit_invocation_expression(self, invocation_expression):
        func_name = invocation_expression.name.id
        arg_results = [arg.accept(self) for arg in invocation_expression.arguments]
        
        for i, arg_res in enumerate(arg_results):
            self.instructions.append(f"  mv a{i}, {arg_res}")
            
        self.instructions.append(f"  jal {func_name}")
        t = self.new_temp()
        self.instructions.append(f"  mv {t}, a0")
        return t

    def visit_unary_expression(self, unary_expression):
        operand_res = unary_expression.operand.accept(self)
        t = self.new_temp()
        
        if unary_expression.operator == expression_ast.Operator.NOT:
            self.instructions.append(f"  seqz {t}, {operand_res}")
        else: # MINUS
            self.instructions.append(f"  neg {t}, {operand_res}")
        return t

    def visit_binary_expression(self, binary_expression):
        left_result = binary_expression.left.accept(self)
        right_res = binary_expression.right.accept(self)
        t = self.new_temp()
        
        op = binary_expression.operator
        op_map = {
            expression_ast.Operator.PLUS: "add",
            expression_ast.Operator.MINUS: "sub",
            expression_ast.Operator.TIMES: "mul",
            expression_ast.Operator.DIVIDE: "div",
            expression_ast.Operator.LT: "slt",
            expression_ast.Operator.LE: "sle",
            expression_ast.Operator.GT: "sgt",
            expression_ast.Operator.GE: "sge",
            expression_ast.Operator.AND: "and",
            expression_ast.Operator.OR: "or",
            expression_ast.Operator.EQ: "seq",
            expression_ast.Operator.NE: "sne"
        }
        
        inst = op_map.get(op, "add")
        self.instructions.append(f"  {inst} {t}, {left_result}, {right_res}")
        return t

    # --- LValues ---

    def visit_lvalue_id(self, lvalue_id):
        return f"@{lvalue_id.id.id}"

    def visit_lvalue_dot(self, lvalue_dot):
        left_result = lvalue_dot.left.accept(self)
        field_name = lvalue_dot.id.id
        return (left_result, field_name)