from collections import namedtuple
from miniast import mini_ast, statement_ast, expression_ast, lvalue_ast

Symbol = namedtuple("Symbol", "type kind")   # kind: "global" | "param" | "local"
ERR = "<error>"                              # can't collide with a legal identifier


class SymbolTable:
    """Stack of scopes; index 0 is global. Each scope maps name -> Symbol."""

    def __init__(self):
        self.scope = [{"scope": "global", "symbols": {}}]
        self.history = []                    # popped scopes, kept for the -s debug option

    def enter_scope(self, scope_name):
        self.scope.append({"scope": scope_name, "symbols": {}})

    def exit_scope(self):
        if len(self.scope) > 1:
            self.history.append(self.scope.pop())

    def depth(self):
        return len(self.scope)

    def insert(self, name, type_, kind):
        """Insert into the current scope; False if the name is already there."""
        symbols = self.scope[-1]["symbols"]
        if name in symbols:
            return False
        symbols[name] = Symbol(type_, kind)
        return True

    def lookup(self, name):
        """Search innermost scope outward. Returns a Symbol or None."""
        for s in reversed(self.scope):
            if name in s["symbols"]:
                return s["symbols"][name]
        return None


class StaticSemanticASTVisitor(mini_ast.ASTVisitor):
    """Single-pass static semantic analysis. Expression/type visitors return a
    type string: "int", "bool", "void", "null", a struct name, or ERR."""

    def __init__(self):
        self.error_count = 0
        self.symbols = SymbolTable()
        self.functions = {}      # name -> (param_types, return_type); separate namespace
        self.structs = {}        # name -> {field: type};              separate namespace
        self.curr_ret = None     # return type of the function being checked

    # ---------- helpers ----------
    def report_error(self, msg, line):
        self.error_count += 1
        print(f"ERROR. {msg} #{line}")

    def _compatible(self, expected, actual):
        """May a value of type `actual` be used where `expected` is required?"""
        if ERR in (expected, actual) or expected == actual:
            return True
        return actual == "null" and expected in self.structs

    def _declare(self, decl, kind):
        t = decl.type.accept(self)
        if not self.symbols.insert(decl.name.id, t, kind):
            self.report_error(f"redeclaration of '{decl.name.id}'", decl.linenum)
        return t

    def _returns(self, s):
        """Does every path through statement `s` hit a return? (while counts as no, as in Java)"""
        if isinstance(s, (statement_ast.ReturnStatement, statement_ast.ReturnEmptyStatement)):
            return True
        if isinstance(s, statement_ast.BlockStatement):
            return any(self._returns(x) for x in s.statements)
        if isinstance(s, statement_ast.ConditionalStatement):
            return (s.else_block is not None
                    and self._returns(s.then_block) and self._returns(s.else_block))
        return False

    # ---------- program level ----------
    def visit_program(self, program):
        # Types, globals, functions are visited in source order, which gives the
        # "scope starts at definition" rule for free.
        for t in program.types:
            t.accept(self)
        for d in program.declarations:
            d.accept(self)
        for f in program.functions:
            f.accept(self)
        if "main" not in self.functions:
            self.report_error("program has no main function", 0)   # TODO: confirm which line the grader expects
        return self.error_count

    def visit_type_declaration(self, td):
        name = td.name.id
        if name in self.structs:
            self.report_error(f"duplicate struct '{name}'", td.linenum)
            return
        fields = {}
        self.structs[name] = fields          # register first: a struct may contain itself
        for f in td.fields:
            t = f.type.accept(self)          # unknown/later structs are reported here
            if f.name.id in fields:
                self.report_error(f"duplicate field '{f.name.id}' in struct '{name}'", f.linenum)
            else:
                fields[f.name.id] = t

    def visit_declaration(self, decl):
        # Reached only for globals; params/locals go through _declare directly.
        return self._declare(decl, "global")

    def visit_function(self, func):
        name = func.name.id
        ret = func.ret_type.accept(self)

        self.symbols.enter_scope(name)       # params and locals share this scope
        ptypes = [self._declare(p, "param") for p in func.params]

        if name in self.functions:
            self.report_error(f"duplicate function '{name}'", func.linenum)
        else:
            self.functions[name] = (ptypes, ret)   # before the body, so recursion works

        if name == "main" and (ptypes or ret != "int"):
            self.report_error("main must take no arguments and return int", func.linenum)

        for l in func.locals:
            self._declare(l, "local")

        self.curr_ret = ret
        for s in func.body:
            s.accept(self)

        if ret != "void" and ret != ERR and not any(self._returns(s) for s in func.body):
            self.report_error(f"function '{name}' does not return a value on all paths", func.linenum)

        self.curr_ret = None
        self.symbols.exit_scope()

    # ---------- types ----------
    def visit_int_type(self, t):  return "int"
    def visit_bool_type(self, t): return "bool"

    def visit_struct_type(self, t):
        name = t.name.id
        if name not in self.structs:
            self.report_error(f"unknown struct type '{name}'", t.linenum)
            return ERR
        return name

    def visit_return_type_real(self, t): return t.type_.accept(self)
    def visit_return_type_void(self, t): return "void"

    # ---------- statements ----------
    def visit_assignment_statement(self, s):
        # Non-struct parameters are values and can't be assigned; struct params are references and can.
        if isinstance(s.target, lvalue_ast.LValueID):
            sym = self.symbols.lookup(s.target.id.id)
            if sym and sym.kind == "param" and sym.type not in self.structs:
                self.report_error(f"cannot assign to parameter '{s.target.id.id}'", s.linenum)
        target = s.target.accept(self)
        source = s.source.accept(self)
        if not self._compatible(target, source):
            self.report_error(f"cannot assign {source} to {target}", s.linenum)

    def visit_block_statement(self, s):
        for st in s.statements:
            st.accept(self)

    def visit_conditional_statement(self, s):
        if s.guard.accept(self) not in ("bool", ERR):
            self.report_error("if guard must be boolean", s.linenum)
        s.then_block.accept(self)
        if s.else_block:
            s.else_block.accept(self)

    def visit_while_statement(self, s):
        if s.guard.accept(self) not in ("bool", ERR):
            self.report_error("while guard must be boolean", s.linenum)
        s.body.accept(self)

    def visit_delete_statement(self, s):
        t = s.expression.accept(self)
        if t != ERR and t not in self.structs:
            self.report_error(f"delete requires a struct, got {t}", s.linenum)

    def visit_invocation_statement(self, s):
        s.expression.accept(self)

    def visit_println_statement(self, s):
        if s.expression.accept(self) not in ("int", ERR):
            self.report_error("print requires an integer argument", s.linenum)

    def visit_print_statement(self, s):
        self.visit_println_statement(s)

    def visit_return_empty_statement(self, s):
        if self.curr_ret not in ("void", ERR):
            self.report_error(f"empty return in function returning {self.curr_ret}", s.linenum)

    def visit_return_statement(self, s):
        t = s.expression.accept(self) if s.expression else "void"
        if self.curr_ret == "void":
            self.report_error("void function must not return a value", s.linenum)
        elif not self._compatible(self.curr_ret, t):
            self.report_error(f"returning {t}, expected {self.curr_ret}", s.linenum)

    # ---------- expressions ----------
    def visit_integer_expression(self, e): return "int"
    def visit_true_expression(self, e):    return "bool"
    def visit_false_expression(self, e):   return "bool"
    def visit_null_expression(self, e):    return "null"
    def visit_read_expression(self, e):    return "int"

    def visit_identifier_expression(self, e):
        sym = self.symbols.lookup(e.id)
        if sym is None:
            self.report_error(f"undeclared variable '{e.id}'", e.linenum)
            return ERR
        return sym.type

    def visit_new_expression(self, e):
        if e.id.id not in self.structs:
            self.report_error(f"new of undefined struct '{e.id.id}'", e.linenum)
            return ERR
        return e.id.id

    def visit_dot_expression(self, e):
        return self._field_type(e.left.accept(self), e.id.id, e.linenum)

    def _field_type(self, struct_type, field, line):
        if struct_type == ERR:
            return ERR
        if struct_type not in self.structs:
            self.report_error(f"field access '.{field}' on non-struct type {struct_type}", line)
            return ERR
        if field not in self.structs[struct_type]:
            self.report_error(f"struct {struct_type} has no field '{field}'", line)
            return ERR
        return self.structs[struct_type][field]

    def visit_invocation_expression(self, e):
        name = e.name.id
        arg_types = [a.accept(self) for a in e.arguments]
        if name not in self.functions:
            self.report_error(f"call to undefined function '{name}'", e.linenum)
            return ERR
        params, ret = self.functions[name]
        if len(params) != len(arg_types):
            self.report_error(f"'{name}' expects {len(params)} argument(s), got {len(arg_types)}", e.linenum)
        else:
            for p, a in zip(params, arg_types):
                if not self._compatible(p, a):
                    self.report_error(f"argument of type {a} where {p} expected in call to '{name}'", e.linenum)
        return ret

    def visit_unary_expression(self, e):
        t = e.operand.accept(self)
        want = "bool" if e.operator == expression_ast.Operator.NOT else "int"
        if t not in (want, ERR):
            self.report_error(f"operator {e.operator.value} requires {want} operand", e.linenum)
            return ERR
        return want

    def visit_binary_expression(self, e):
        O = expression_ast.Operator
        l, r = e.left.accept(self), e.right.accept(self)
        if ERR in (l, r):
            return ERR
        op = e.operator
        if op in (O.TIMES, O.DIVIDE, O.PLUS, O.MINUS):
            need, result = "int", "int"
        elif op in (O.LT, O.LE, O.GT, O.GE):
            need, result = "int", "bool"
        elif op in (O.AND, O.OR):
            need, result = "bool", "bool"
        else:  # EQ, NE: int or struct (null allowed), types must match
            ok = lambda t: t == "int" or t == "null" or t in self.structs
            if not (ok(l) and ok(r)):
                self.report_error(f"operator {op.value} requires int or struct operands", e.linenum)
                return ERR
            if not (self._compatible(l, r) or self._compatible(r, l)):
                self.report_error(f"cannot compare {l} with {r}", e.linenum)
                return ERR
            return "bool"
        if l != need or r != need:
            self.report_error(f"operator {op.value} requires {need} operands", e.linenum)
            return ERR
        return result

    # ---------- lvalues ----------
    def visit_lvalue_id(self, lv):
        return self.visit_identifier_expression(lv.id)

    def visit_lvalue_dot(self, lv):
        return self._field_type(lv.left.accept(self), lv.id.id, lv.linenum)