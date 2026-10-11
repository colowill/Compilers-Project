from miniast import mini_ast, statement_ast, expression_ast, lvalue_ast

ERROR = "<error>"


class SymbolTable:
    """
    Stack of scopes where index 0 is global. Each scope contains dict of symbols where: 
    key value is (symbol name : {datatype, scope})

    Example:
        self.scope = [
            {
                "scope": "global",
                "symbols": {
                    "i": {
                        "type": "int",
                        "kind": "global"
                        },
                    "a": {
                        "type": "A", 
                        "kind": "global"
                        }
                }
            }
        ]
    """

    def __init__(self):
        self.scope = [
            {
                "scope": "global",
                "symbols": {}
            }
        ]
        self.history = []

    def enter_scope(self, scope_name):
        """
        Pushes next scope onto stack
        """
        self.scope.append(
            {
                "scope": scope_name,
                "symbols": {}
            }
        )

    def exit_scope(self):
        """
        Pops the current scope
        """
        if len(self.scope) > 1:
            self.history.append(self.scope.pop())

    def depth(self):
        """
        Returns the num of scopes
        """
        return len(self.scope)

    def insert(self, name, type_, kind):
        """
        Inserts a symbol into the current scope, 
        Returns False if symbol by tha name already exists
        """
        symbols = self.scope[-1]["symbols"]
        if name in symbols:
            return False
        symbols[name] = {
            "type": type_,
            "kind": kind
        }
        return True

    def lookup(self, name):
        """
        Returns the symbol dict for a name starting with the current scope
        """
        for s in reversed(self.scope):
            if name in s["symbols"]:
                return s["symbols"][name]
        return None


class StaticSemanticASTVisitor(mini_ast.ASTVisitor):
    """
    ASTVisitor class, similar to pretty print
    """

    def __init__(self):
        self.error_count = 0
        self.symbols = SymbolTable()
        self.functions = {}
        self.structs = {}
        self.curr_ret = None

    def report_error(self, msg, line):
        """
        Called in conditions where there is an error
        """
        self.error_count += 1
        print(f"ERROR. {msg} #{line}")

    def _compatible(self, expected, actual):
        """
        Called when a variable that was already declared is given a new value,
        Returns True if the new assignment is type compatible with the declared variable
        """
        if ERROR in (expected, actual) or expected == actual:
            return True
        if actual == "null" and expected in self.structs:
            return True
        else:
            return False

    def _declare(self, declaration, kind):
        """
        Inserts a declaration into the current scope. If insert returns false, reports error as redeclaration
        """
        type = declaration.type.accept(self)
        if not self.symbols.insert(declaration.name.id, type, kind):
            self.report_error(f"redeclaration of '{declaration.name.id}'", declaration.linenum)
        return type

    def _returns(self, statement):
        """
        Returns True if every path through a statement reaches a return
        """
        if isinstance(statement, (statement_ast.ReturnStatement, statement_ast.ReturnEmptyStatement)):
            return True
        if isinstance(statement, statement_ast.BlockStatement):
            return any(self._returns(x) for x in statement.statements)
        if isinstance(statement, statement_ast.ConditionalStatement):
            if statement.else_block is None:
                return False
            
            return (
                self._returns(statement.then_block) and self._returns(statement.else_block)
            )
        return False

    def visit_program(self, program):
        """
        Visits structs, globals, then functions in order
        """
        for type_declaration in program.types:
            type_declaration.accept(self)
        for declaration in program.declarations:
            declaration.accept(self)
        for func in program.functions:
            func.accept(self)

        if "main" not in self.functions:
            self.report_error("program has no main function", 0)
        return self.error_count

    def visit_type_declaration(self, type_declaration):
        """
        Registers a struct and its fields, reporting duplicate structs and fields
        """
        name = type_declaration.name.id
        if name in self.structs:
            self.report_error(f"duplicate struct '{name}'", type_declaration.linenum)
            return

        fields = {}
        self.structs[name] = fields
        for field in type_declaration.fields:
            type = field.type.accept(self)
            if field.name.id in fields:
                self.report_error(f"duplicate field '{field.name.id}' in struct '{name}'", field.linenum)
            else:
                fields[field.name.id] = type

    def visit_declaration(self, declaration):
        """
        Declares a global variable in the global scope
        """
        return self._declare(declaration, "global")

    def visit_function(self, function):
        """
        Checks a function's signature, locals, body, and return paths in its own scope
        """
        name = function.name.id
        ret = function.ret_type.accept(self)

        self.symbols.enter_scope(name)
        ptypes = [self._declare(p, "param") for p in function.params]

        if name in self.functions:
            self.report_error(f"duplicate function '{name}'", function.linenum)
        else:
            self.functions[name] = (ptypes, ret)

        if name == "main" and (ptypes or ret != "int"):
            self.report_error("main must take no arguments and return int", function.linenum)

        for l in function.locals:
            self._declare(l, "local")

        self.curr_ret = ret
        for s in function.body:
            s.accept(self)

        if ret != "void" and ret != ERROR and not any(self._returns(s) for s in function.body):
            self.report_error(f"function '{name}' does not return a value on all paths", function.linenum)

        self.curr_ret = None
        self.symbols.exit_scope()

    def visit_int_type(self, int_type):
        return "int"

    def visit_bool_type(self, bool_type):
        return "bool"

    def visit_struct_type(self, struct_type):
        name = struct_type.name.id
        if name not in self.structs:
            self.report_error(f"unknown struct type '{name}'", struct_type.linenum)
            return ERROR
        return name

    def visit_return_type_real(self, return_type):
        return return_type.type_.accept(self)

    def visit_return_type_void(self, return_type_void):
        return "void"

    def visit_assignment_statement(self, statement):
        """
        Checks that the source is compatible with the target and that no value parameter is assigned
        """
        if isinstance(statement.target, lvalue_ast.LValueID):
            sym = self.symbols.lookup(statement.target.id.id)
            if sym and sym["kind"] == "param" and sym["type"] not in self.structs:
                self.report_error(f"cannot assign to parameter '{statement.target.id.id}'", statement.linenum)

        target = statement.target.accept(self)
        source = statement.source.accept(self)
        if not self._compatible(target, source):
            self.report_error(f"cannot assign {source} to {target}", statement.linenum)

    def visit_block_statement(self, block):
        """
        Visits each statement in the block in order
        """
        for statement in block.statements:
            statement.accept(self)

    def visit_conditional_statement(self, statement):
        """
        Checks for a boolean guard, then visits the then and else blocks
        """
        if statement.guard.accept(self) not in ("bool", ERROR):
            self.report_error("if guard must be boolean", statement.linenum)
        statement.then_block.accept(self)
        if statement.else_block:
            statement.else_block.accept(self)

    def visit_while_statement(self, statement):
        """
        Checks for a boolean guard, then visits the body
        """
        if statement.guard.accept(self) not in ("bool", ERROR):
            self.report_error("while guard must be boolean", statement.linenum)
        statement.body.accept(self)

    def visit_delete_statement(self, statement):
        """
        Checks that the deleted expression is a struct.
        """
        type_exp = statement.expression.accept(self)
        if type_exp != ERROR and type_exp not in self.structs:
            self.report_error(f"delete requires a struct, got {type_exp}", s.linenum)

    def visit_invocation_statement(self, statement):
        """
        Checks a function call used as a statement and discards its result
        """
        statement.expression.accept(self)

    def visit_println_statement(self, statement):
        """
        Checks that the printed expression is an int
        """
        if statement.expression.accept(self) not in ("int", ERROR):
            self.report_error("print requires an integer argument", statement.linenum)

    def visit_print_statement(self, statement):
        """
        Applies the same check as println
        """
        self.visit_println_statement(statement)

    def visit_return_empty_statement(self, statement):
        """
        Reports an empty return unless the current function is void
        """
        if self.curr_ret not in ("void", ERROR):
            self.report_error(f"empty return in function returning {self.curr_ret}", statement.linenum)

    def visit_return_statement(self, s):
        """
        Checks the returned value against the current function's return type
        """
        t = s.expression.accept(self) if s.expression else "void"
        if self.curr_ret == "void":
            self.report_error("void function must not return a value", s.linenum)
        elif not self._compatible(self.curr_ret, t):
            self.report_error(f"returning {t}, expected {self.curr_ret}", s.linenum)

    def visit_integer_expression(self, exp):
        """
        Returns the type string for an integer literal
        """
        return "int"

    def visit_true_expression(self, exp):
        """
        Returns the type string for true
        """
        return "bool"

    def visit_false_expression(self, exp):
        """
        Returns the type string for false
        """
        return "bool"

    def visit_null_expression(self, exp):
        """
        Returns the type string for null
        """
        return "null"

    def visit_read_expression(self, exp):
        """
        Returns the type string for read, which evaluates to an int
        """
        return "int"

    def visit_identifier_expression(self, exp):
        """
        Returns the variable's type, else reports an undeclared variable and returns ERROR
        """
        sym = self.symbols.lookup(exp.id)
        if sym is None:
            self.report_error(f"undeclared variable '{exp.id}'", exp.linenum)
            return ERROR
        return sym["type"]

    def visit_new_expression(self, exp):
        """
        Returns the struct's name if it is defined, else reports an error and returns ERROR
        """
        if exp.id.id not in self.structs:
            self.report_error(f"new of undefined struct '{exp.id.id}'", exp.linenum)
            return ERROR
        return exp.id.id

    def visit_dot_expression(self, exp):
        """
        Returns the type of the accessed field
        """
        return self._field_type(exp.left.accept(self), exp.id.id, exp.linenum)

    def _field_type(self, struct_type, field, line):
        """
        Returns a field's type if struct_type is a struct with that field, else reports an error and returns ERROR
        """
        if struct_type == ERROR:
            return ERROR
        if struct_type not in self.structs:
            self.report_error(f"field access '.{field}' on non-struct type {struct_type}", line)
            return ERROR
        if field not in self.structs[struct_type]:
            self.report_error(f"struct {struct_type} has no field '{field}'", line)
            return ERROR
        return self.structs[struct_type][field]

    def visit_invocation_expression(self, exp):
        """
        Checks a call against the function's signature and returns its return type
        """
        name = exp.name.id
        arg_types = [a.accept(self) for a in exp.arguments]

        if name not in self.functions:
            self.report_error(f"call to undefined function '{name}'", exp.linenum)
            return ERROR

        params, ret = self.functions[name]
        if len(params) != len(arg_types):
            self.report_error(f"'{name}' expects {len(params)} argument(s), got {len(arg_types)}", exp.linenum)
        else:
            for p, a in zip(params, arg_types):
                if not self._compatible(p, a):
                    self.report_error(f"argument of type {a} where {p} expected in call to '{name}'", exp.linenum)
        return ret

    def visit_unary_expression(self, exp):
        """
        Checks that the operand matches the operator and returns the resulting type
        """
        t = exp.operand.accept(self)
        want = "bool" if exp.operator == expression_ast.Operator.NOT else "int"
        if t not in (want, ERROR):
            self.report_error(f"operator {e.operator.value} requires {want} operand", e.linenum)
            return ERROR
        return want

    def visit_binary_expression(self, exp):
        """
        Checks both operands against the operator and returns the resulting type
        """
        O = expression_ast.Operator
        l, r = exp.left.accept(self), exp.right.accept(self)
        if ERROR in (l, r):
            return ERROR

        op = exp.operator
        if op in (O.TIMES, O.DIVIDE, O.PLUS, O.MINUS):
            need, result = "int", "int"
        elif op in (O.LT, O.LE, O.GT, O.GE):
            need, result = "int", "bool"
        elif op in (O.AND, O.OR):
            need, result = "bool", "bool"
        else:
            ok = lambda t: t == "int" or t == "null" or t in self.structs
            if not (ok(l) and ok(r)):
                self.report_error(f"operator {op.value} requires int or struct operands", exp.linenum)
                return ERROR
            if not (self._compatible(l, r) or self._compatible(r, l)):
                self.report_error(f"cannot compare {l} with {r}", exp.linenum)
                return ERROR
            return "bool"

        if l != need or r != need:
            self.report_error(f"operator {op.value} requires {need} operands", exp.linenum)
            return ERROR
        return result

    def visit_lvalue_id(self, lvalue):
        """
        Returns the type of a plain variable on the left of an assignment
        """
        return self.visit_identifier_expression(lvalue.id)

    def visit_lvalue_dot(self, lvalue):
        """
        Returns the type of a left assignment
        """
        return self._field_type(lvalue.left.accept(self), lvalue.id.id, lvalue.linenum)