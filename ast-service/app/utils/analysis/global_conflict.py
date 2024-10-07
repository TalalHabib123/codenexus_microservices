from app.utils.visitors.global_visitor import GlobalVariableConflictAnalyzer

def global_variable_conflicts(code: str, global_variables: list) -> dict:
    try:
        analyzer = GlobalVariableConflictAnalyzer(code, global_variables)
        return analyzer.get_conflicts()
    except Exception as e:
        return []