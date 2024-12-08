import ast 
import astor

from app.utils.Transformers.MagicNumberTransformer import MagicNumberTransformer


def magic_numbers_refactor (magic_numbers_to_refactor, source_code):
    tree = ast.parse(source_code)
    transformer = MagicNumberTransformer(magic_numbers_to_refactor)
    modified_tree = transformer.visit(tree)
    ast.fix_missing_locations(modified_tree)

    # Insert declarations at the top of the AST (avoiding duplicates)
    for declaration in reversed(transformer.declarations):
        if declaration not in tree.body:
            tree.body.insert(0, declaration)

    # Convert the modified AST back to source code
    return astor.to_source(modified_tree)