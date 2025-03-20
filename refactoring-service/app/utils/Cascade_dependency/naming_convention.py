import ast 
import astor
from app.utils.utils.Def_Collector import DefinitionCollector
from app.utils.cascade_refactor.NamingRefactorer import CascadeNamingRefactorer

def cascade_naming_refactor_values(dependency, mappings):
    for dep in dependency: 
        dep_list = []
        for w in dep.weight:
            if w.source == "Exporting":
                dep_list.append(w.name)
        dep_ast = ast.parse(dep.fileContent)
        print("testing")
        # Get definitions from this dependency's AST
        def_tree = DefinitionCollector()
        def_tree.visit(dep_ast)
        definitions = def_tree.get_definitions()
        if 'imports' not in definitions:
            definitions['imports'] = set()
        if 'functions' not in definitions:
            definitions['functions'] = set()
        if 'classes' not in definitions:
            definitions['classes'] = set()
        if 'variables' not in definitions:
            definitions['variables'] = set()
 
        dep_refactorer = CascadeNamingRefactorer(mappings, dep_list, definitions)
       
        dep_refactorer.name_mappings = mappings
 
        refactored_dep_ast = dep_refactorer.visit(dep_ast)
        ast.fix_missing_locations(refactored_dep_ast)
        dep.fileContent = astor.to_source(refactored_dep_ast)
    return dependency