from miniast import mini_ast, program_ast, type_ast, statement_ast, expression_ast, lvalue_ast

class SymbolTable:
    """
    SymbolTable uses a structured of nested dictionaries. The top level dictionary maintains the key-value pair
    between a scope level (index 0 being global) and it's symbol table. Within a scope's symbol table is a dictionary to map
    identifiers to their scope and symbol details.  
    """
    
    def __init__(self):
        self.scope = [
            {
                "scope": "global", "symbols": {}
            }
        ]
        
    def enter_scope(self, scope_name):
        """
        Adds a new scope to the upper-level dict
        """
        self.scope.append(
            {
                "scope": scope_name,
                "symbols": {}
            }
        )
        
    def exit_scope(self):
        """
        Once a scope has been traversed, we can safely pop it and check the next scope
        """
        if len(self.scope) > 1:
            self.scope.pop()
            
    def insert(self, symbol_name, symbol_type):
        """
        Inserts a new symbol into the current scopes table
        Returns False if a symbol by the same name already exists
        else Returns True
        """
        
        curr_scope_symbols = self.scope[-1]['symbols']
        if symbol_name in curr_scope_symbols:
            return False
        curr_scope_symbols[symbol_name] = symbol_type
        return True
    
    def lookup(self, symbol_name):
        """
        Looks up a symbol by its name in reverse scope order (starting with current scope)
        """
        for scope_dict in reversed(self.scope):
            if symbol_name in scope_dict['symbols']:
                return scope_dict[symbol_name]
        return None
        
class StaticSemanticASTVisitor(mini_ast.ASTVisitor):
  """AST Visitor executing static semantic analysis and type checking."""

  def __init__(self):
    self.error_count = 0
    self.errors = []  # List of tuples: line_num, error_message
    self.symbols = SymbolTable()
    self.functions = {}
    self.structs = {}
    self.curr_func = None

  def report_error(self, msg: str, line: int):
    """
    Adds an error to error array
    """
    self.error_count += 1
    self.errors.append((line, msg))
