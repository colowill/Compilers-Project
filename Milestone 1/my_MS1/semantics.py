from miniast import mini_ast, statement_ast, expression_ast, lvalue_ast

ERROR = "<error>"


class SymbolTable:
    """
    Stack of scopes where index 0 is global. Each scope contains dict of symbols. 
    For each symbol name, there is a dict with data type, and scope origin

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
        Pops the current scope into history
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
        Returns False if the name already exists
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
        Returns the symbol dict for a name searching from the current scope outward, else None.
        """
        for s in reversed(self.scope):
            if name in s["symbols"]:
                return s["symbols"][name]
        return None


class StaticSemanticASTVisitor(mini_ast.ASTVisitor):
    """
    Single-pass static semantic analysis where visitors return a type string.
    """

    def __init__(self):
        self.error_count = 0
        self.symbols = SymbolTable()
        self.functions = {}
        self.structs = {}
        self.curr_ret = None

    def report_error(self, msg, line):
        """
        Prints an error as "ERROR. <msg> #<line>" and increments the error count.
        """
        self.error_count += 1
        print(f"ERROR. {msg} #{line}")

    def _compatible(self, expected, actual):
        """
        Returns True if a value of type actual can be used where expected is required.
        """
        if ERROR in (expected, actual) or expected == actual:
            return True
        return actual == "null" and expected in self.structs

    def _declare(self, decl, kind):
        """
        Inserts a declaration into the current scope, reports a redeclaration, and returns its type.
        """
        t = decl.type.accept(self)
        if not self.symbols.insert(decl.name.id, t, kind):
            self.report_error(f"redeclaration of '{decl.name.id}'", decl.linenum)
        return t

    def _returns(self, s):
        """
        Returns True if every path through statement s reaches a return.
        """
        if isinstance(s, (statement_ast.ReturnStatement, statement_ast.ReturnEmptyStatement)):
            return True
        if isinstance(s, statement_ast.BlockStatement):
            return any(self._returns(x) for x in s.statements)
        if isinstance(s, statement_ast.ConditionalStatement):
            return (
                s.else_block is not None
                and self._returns(s.then_block)
                and self._returns(s.else_block)
            )
        return False

    def visit_program(self, program):
        """
        Visits structs, globals, then functions in source order and returns the error count.
        """
        for t in program.types:
            t.accept(self)
        for d in program.declarations:
            d.accept(self)
        for f in program.functions:
            f.accept(self)

        if "main" not in self.functions:
            self.report_error("program has no main function", 0)
        return self.error_count

    def visit_type_declaration(self, td):
        """
        Registers a struct and its fields, reporting duplicate structs and fields.
        """
        name = td.name.id
        if name in self.structs:
            self.report_error(f"duplicate struct '{name}'", td.linenum)
            return

        fields = {}
        self.structs[name] = fields
        for f in td.fields:
            t = f.type.accept(self)
            if f.name.id in fields:
                self.report_error(f"duplicate field '{f.name.id}' in struct '{name}'", f.linenum)
            else:
                fields[f.name.id] = t

    def visit_declaration(self, decl):
        """
        Declares a global variable in the global scope.
        """
        return self._declare(decl, "global")

    def visit_function(self, func):
        """
        Checks a function's signature, locals, body, and return paths in its own scope.
        """
        name = func.name.id
        ret = func.ret_type.accept(self)

        self.symbols.enter_scope(name)
        ptypes = [self._declare(p, "param") for p in func.params]

        if name in self.functions:
            self.report_error(f"duplicate function '{name}'", func.linenum)
        else:
            self.functions[name] = (ptypes, ret)

        if name == "main" and (ptypes or ret != "int"):
            self.report_error("main must take no arguments and return int", func.linenum)

        for l in func.locals:
            self._declare(l, "local")

        self.curr_ret = ret
        for s in func.body:
            s.accept(self)

        if ret != "void" and ret != ERROR and not any(self._returns(s) for s in func.body):
            self.report_error(f"function '{name}' does not return a value on all paths", func.linenum)

        self.curr_ret = None
        self.symbols.exit_scope()

    def visit_int_type(self, t):
        """
        Returns the type string for int.
        """
        return "int"

    def visit_bool_type(self, t):
        """
        Returns the type string for bool.
        """
        return "bool"

    def visit_struct_type(self, t):
        """
        Returns the struct's name if it is defined, else reports an error and returns ERROR.
        """
        name = t.name.id
        if name not in self.structs:
            self.report_error(f"unknown struct type '{name}'", t.linenum)
            return ERROR
        return name

    def visit_return_type_real(self, t):
        """
        Returns the type wrapped by a non-void return type.
        """
        return t.type_.accept(self)

    def visit_return_type_void(self, t):
        """
        Returns the type string for void.
        """
        return "void"

    def visit_assignment_statement(self, s):
        """
        Checks that the source is compatible with the target and that no value parameter is assigned.
        """
        if isinstance(s.target, lvalue_ast.LValueID):
            sym = self.symbols.lookup(s.target.id.id)
            if sym and sym["kind"] == "param" and sym["type"] not in self.structs:
                self.report_error(f"cannot assign to parameter '{s.target.id.id}'", s.linenum)

        target = s.target.accept(self)
        source = s.source.accept(self)
        if not self._compatible(target, source):
            self.report_error(f"cannot assign {source} to {target}", s.linenum)

    def visit_block_statement(self, s):
        """
        Visits each statement in the block in order.
        """
        for st in s.statements:
            st.accept(self)

    def visit_conditional_statement(self, s):
        """
        Checks for a boolean guard, then visits the then and else blocks.
        """
        if s.guard.accept(self) not in ("bool", ERROR):
            self.report_error("if guard must be boolean", s.linenum)
        s.then_block.accept(self)
        if s.else_block:
            s.else_block.accept(self)

    def visit_while_statement(self, s):
        """
        Checks for a boolean guard, then visits the body.
        """
        if s.guard.accept(self) not in ("bool", ERROR):
            self.report_error("while guard must be boolean", s.linenum)
        s.body.accept(self)

    def visit_delete_statement(self, s):
        """
        Checks that the deleted expression is a struct.
        """
        t = s.expression.accept(self)
        if t != ERROR and t not in self.structs:
            self.report_error(f"delete requires a struct, got {t}", s.linenum)

    def visit_invocation_statement(self, s):
        """
        Checks a function call used as a statement and discards its result.
        """
        s.expression.accept(self)

    def visit_println_statement(self, s):
        """
        Checks that the printed expression is an int.
        """
        if s.expression.accept(self) not in ("int", ERROR):
            self.report_error("print requires an integer argument", s.linenum)

    def visit_print_statement(self, s):
        """
        Applies the same check as println.
        """
        self.visit_println_statement(s)

    def visit_return_empty_statement(self, s):
        """
        Reports an empty return unless the current function is void.
        """
        if self.curr_ret not in ("void", ERROR):
            self.report_error(f"empty return in function returning {self.curr_ret}", s.linenum)

    def visit_return_statement(self, s):
        """
        Checks the returned value against the current function's return type.
        """
        t = s.expression.accept(self) if s.expression else "void"
        if self.curr_ret == "void":
            self.report_error("void function must not return a value", s.linenum)
        elif not self._compatible(self.curr_ret, t):
            self.report_error(f"returning {t}, expected {self.curr_ret}", s.linenum)

    def visit_integer_expression(self, e):
        """
        Returns the type string for an integer literal.
        """
        return "int"

    def visit_true_expression(self, e):
        """
        Returns the type string for true.
        """
        return "bool"

    def visit_false_expression(self, e):
        """
        Returns the type string for false.
        """
        return "bool"

    def visit_null_expression(self, e):
        """
        Returns the type string for null.
        """
        return "null"

    def visit_read_expression(self, e):
        """
        Returns the type string for read, which evaluates to an int.
        """
        return "int"

    def visit_identifier_expression(self, e):
        """
        Returns the variable's type, else reports an undeclared variable and returns ERROR.
        """
        sym = self.symbols.lookup(e.id)
        if sym is None:
            self.report_error(f"undeclared variable '{e.id}'", e.linenum)
            return ERROR
        return sym["type"]

    def visit_new_expression(self, e):
        """
        Returns the struct's name if it is defined, else reports an error and returns ERROR.
        """
        if e.id.id not in self.structs:
            self.report_error(f"new of undefined struct '{e.id.id}'", e.linenum)
            return ERROR
        return e.id.id

    def visit_dot_expression(self, e):
        """
        Returns the type of the accessed field.
        """
        return self._field_type(e.left.accept(self), e.id.id, e.linenum)

    def _field_type(self, struct_type, field, line):
        """
        Returns a field's type if struct_type is a struct with that field, else reports an error and returns ERROR.
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

    def visit_invocation_expression(self, e):
        """
        Checks a call against the function's signature and returns its return type.
        """
        name = e.name.id
        arg_types = [a.accept(self) for a in e.arguments]

        if name not in self.functions:
            self.report_error(f"call to undefined function '{name}'", e.linenum)
            return ERROR

        params, ret = self.functions[name]
        if len(params) != len(arg_types):
            self.report_error(f"'{name}' expects {len(params)} argument(s), got {len(arg_types)}", e.linenum)
        else:
            for p, a in zip(params, arg_types):
                if not self._compatible(p, a):
                    self.report_error(f"argument of type {a} where {p} expected in call to '{name}'", e.linenum)
        return ret

    def visit_unary_expression(self, e):
        """
        Checks that the operand matches the operator and returns the resulting type.
        """
        t = e.operand.accept(self)
        want = "bool" if e.operator == expression_ast.Operator.NOT else "int"
        if t not in (want, ERROR):
            self.report_error(f"operator {e.operator.value} requires {want} operand", e.linenum)
            return ERROR
        return want

    def visit_binary_expression(self, e):
        """
        Checks both operands against the operator and returns the resulting type.
        """
        O = expression_ast.Operator
        l, r = e.left.accept(self), e.right.accept(self)
        if ERROR in (l, r):
            return ERROR

        op = e.operator
        if op in (O.TIMES, O.DIVIDE, O.PLUS, O.MINUS):
            need, result = "int", "int"
        elif op in (O.LT, O.LE, O.GT, O.GE):
            need, result = "int", "bool"
        elif op in (O.AND, O.OR):
            need, result = "bool", "bool"
        else:
            ok = lambda t: t == "int" or t == "null" or t in self.structs
            if not (ok(l) and ok(r)):
                self.report_error(f"operator {op.value} requires int or struct operands", e.linenum)
                return ERROR
            if not (self._compatible(l, r) or self._compatible(r, l)):
                self.report_error(f"cannot compare {l} with {r}", e.linenum)
                return ERROR
            return "bool"

        if l != need or r != need:
            self.report_error(f"operator {op.value} requires {need} operands", e.linenum)
            return ERROR
        return result

    def visit_lvalue_id(self, lv):
        """
        Returns the type of a plain variable on the left of an assignment.
        """
        return self.visit_identifier_expression(lv.id)

    def visit_lvalue_dot(self, lv):
        """
        Returns the type of a field access on the left of an assignment.
        """
        return self._field_type(lv.left.accept(self), lv.id.id, lv.linenum)