Design Doc for Milestone 0
COMP520.001.F26
Professor Sturton
William Minor

## Project Overview

Milestone 0 of the compilers project was focused on understanding how a parser creates an Abstract Syntax Tree (AST) to represent a formal grammar. While the parser and lexer was already provided to me, my task was to
complete the AST traversal by implementing recursive visitor methods. These methods traverse the AST top-down, passing indentation levels to subordinate functions in order to represent the grammar in user-friendly way.

## Design Decisions

For this Milestone, I simply used tabs as a way of organizing subexpressions. Identation depth is stored as an integer parameter during recursive descent, allowing subordinate functions to calculate their leading whitespace based on their level in the tree. In order to do this, I simply only made changes in the file 'pretty_print_ast_visitor.py'. Between this Milestone and the next, I think I will create a function that intelligently replaces the tabs with horizontal dashes, and newlines with vertical dashes to make it more aesthetically pleasing.
