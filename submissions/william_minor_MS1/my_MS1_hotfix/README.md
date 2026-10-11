Design Doc for Milestone 1 
COMP520.001.F26 
Professor Sturton 
William Minor

## Project Overview

Milestone 1 of the compilers project was focused on semantic analysis and building a symbol table. The purpose of this is to make sure a program that parses correctly also follows the rules of the Mini language. Building off of my pretty_print_visitor, I created another visitor that traverses the AST, builds the symbol tables, and reports any errors it finds. Errors are printed as ERROR. <message> #<linenum>, and the total is printed at the end as ERRORS FOUND <num-errors>.

## Design Decisions

For this Milestone, I started off with the same visitor pattern as the pretty printer. Instead of passing indentation levels down to lower functions, each visit method returns the data type of the node it visis up to its caller. This lets a parent compare the types of its children. To avoid reporting an error more than once, nodes that flag an error return a static ERROR, which proceeding checks ignore. When reporting an error, program describes simply the error, and remarks its line number. Total error count is printed at the end, per the assignment instructions.

The symbol table is a stack of scopes, where index 0 is the global scope. Each scope is a dictionary with two entries: the scope's name and a dictionary of its symbols. Each symbol name maps to a dictionary holding its type and its kind (global, param, or local). A scope is pushed to the stack when visiting a function, popping it once it leaves. Inserting a name that already exists in the current scope raises an error. Parameters and locals share one scope, so a local cannot redeclare a parameter.

Everything is checked in one traversal in order of: structs >> globals >> functions. This means a struct or function can only be used after it is defined. A struct is added before its fields are visited so it can contain a member of its own type, and a function is added before its body is visited so it can call itself.

## AI Use

I used ClaudeAI in order to create a helper program to run my semantic analysis through all of the provided benchmarks. I also consulted Claude to help with debugging. Also used AI to help with allowing different arguments to perform semantic vs pretty print.