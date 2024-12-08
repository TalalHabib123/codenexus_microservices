
import ast 
import astor

from app.utils.Transformers.UnusedVariableTransformer import UnusedVariableTransformer

def unused_variables_refactor (unused_variables, source_code):
    tree = ast.parse(source_code)
    transformer = UnusedVariableTransformer(unused_variables)
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    # Convert the modified AST back to source code
    return astor.to_source(modified_tree)
