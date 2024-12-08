import ast 
import astor

from app.utils.Transformers.UnreachableCodeTransformer import UnreachableLineRemover

def unreachable_code_refactor(code, unreachable_lines):
    tree = ast.parse(code)

    # Remove nodes with line numbers in unreachable_line_numbers
    remover = UnreachableLineRemover(unreachable_lines)
    refactored_tree = remover.visit(tree)
    ast.fix_missing_locations(refactored_tree)

    # Convert the modified AST back to code
    return astor.to_source(refactored_tree)