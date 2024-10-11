from app.utils.visitors.global_visitor import GlobalVariableConflictAnalyzer

def global_variable_conflicts(code: str, global_variables: list) -> list:
    try:
        analyzer = GlobalVariableConflictAnalyzer(global_variables)
        analyzer.visit(code)
        return analyzer.analyze_conflicts()
    except Exception as e:
        print(str(e))
        return []