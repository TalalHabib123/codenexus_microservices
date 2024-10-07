import ast
from app.utils.visitors.conditional_visitor import ConditionComplexityAnalyzer

def analyze_condition_complexity(code) -> list:
    try:
        lines = code.splitlines(keepends=True)
        tree = ast.parse(code)

        analyzer = ConditionComplexityAnalyzer(lines)
        analyzer.visit(tree)
        results = analyzer.analyze()
        
        return results
    
    except Exception as e:
        return []