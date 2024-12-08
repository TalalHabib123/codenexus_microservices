import ast
import astor

from app.utils.Transformers.InconsistentNamingTransformer import NamingRefactorer
def inconsistent_naming_refactor( code, target_convention):
    tree = ast.parse(code)
    # Apply the naming refactorer
    refactorer = NamingRefactorer(target_convention)
    refactored_tree = refactorer.visit(tree)
    ast.fix_missing_locations(refactored_tree)
    # Convert the modified AST back to code
    return astor.to_source(refactored_tree)