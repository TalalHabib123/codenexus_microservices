import ast 
import astor

from app.utils.cascade_refactor.NamingRefactorer import NamingRefactorer

def cascade_naming_refactor_values(dependency, mappings):
    for dep in dependency: 
        dep_list = []
        for w in dep.weight:
            if w.source == "Exporting":
                dep_list.append(w.name)
        dep_ast = ast.parse(dep.fileContent)
        
        dep_refactorer = NamingRefactorer(mappings, dep_list)
        refactored_dep_ast = dep_refactorer.visit(dep_ast)
        ast.fix_missing_locations(refactored_dep_ast)
        dep.fileContent = astor.to_source(refactored_dep_ast)
    
    print(dependency)
    return dependency
        