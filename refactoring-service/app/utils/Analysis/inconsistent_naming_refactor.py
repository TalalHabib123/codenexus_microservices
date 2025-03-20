import ast
import astor
import json 

from app.utils.Transformers.InconsistentNamingTransformer import NamingRefactorer
from app.utils.Cascade_dependency.naming_convention import cascade_naming_refactor_values
from app.utils.utils.Def_Collector import DefinitionCollector

def inconsistent_naming_refactor(code, target_convention, dependencies=None):  
    tree = ast.parse(code)
    def_tree = DefinitionCollector()
    def_tree.visit(tree)
    definitions = def_tree.get_definitions()
    # Fix: Pass the definitions parameter to NamingRefactorer
    refactorer = NamingRefactorer(target_convention, definitions=definitions)
    refactored_tree = refactorer.visit(tree)
    ast.fix_missing_locations(refactored_tree)
    
    mappings = refactorer.get_name_mappings()
    if dependencies:
        dependency = cascade_naming_refactor_values(dependencies, mappings)
    else:
        dependency = None
    # Fix: Return proper values, not using variables as dictionary keys
    return astor.to_source(refactored_tree), dependency
