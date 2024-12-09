import ast 
import astor 

from app.utils.Transformers.DeadCodeTransformer import DeadObjectRemover

def dead_code_refactor(dead_object, entity_type, code):
    """Remove dead code from the given code snippet."""
    # Parse the code into an AST
    tree = ast.parse(code)
    # Apply the DeadObjectRemover to the AST
    transformer = DeadObjectRemover(dead_object, entity_type)
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    # Convert the modified AST back to code
    return astor.to_source(tree)
