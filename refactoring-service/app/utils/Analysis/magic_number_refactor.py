import ast 
import astor

from app.utils.Transformers.MagicNumberTransformer import MagicNumberTransformer, AssignmentInserter

def magic_numbers_refactor(magic_numbers_details, source_code):
    # Extract just the magic number values
    magic_numbers = [detail.magic_number for detail in magic_numbers_details]
    
    tree = ast.parse(source_code)
    transformer = MagicNumberTransformer(magic_numbers)
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    inserter = AssignmentInserter(transformer.assignments)
    final_tree = inserter.visit(transformed_tree)
    ast.fix_missing_locations(final_tree)
    
    return astor.to_source(final_tree)