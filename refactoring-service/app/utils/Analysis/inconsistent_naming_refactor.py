import ast
import astor
import json 

from app.utils.Transformers.InconsistentNamingTransformer import NamingRefactorer
from app.utils.Cascade_dependency.naming_convention import cascade_naming_refactor_values
def inconsistent_naming_refactor( code, target_convention, dependencies=None):  
    tree = ast.parse(code)
    refactorer = NamingRefactorer(target_convention)
    refactored_tree = refactorer.visit(tree)
    ast.fix_missing_locations(refactored_tree)
    
    mappings = refactorer.get_name_mappings()
    dependency = cascade_naming_refactor_values(dependencies, mappings)
    return  {code: astor.to_source(refactored_tree), dependencies: dependency}