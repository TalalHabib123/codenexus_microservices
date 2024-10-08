import ast
from app.utils.visitors.field_visitor import TemporaryFieldAnalyzer

def analyze_temporary_fields(parsed_code) -> list:
    try:
        analyzer = TemporaryFieldAnalyzer()
        analyzer.visit(parsed_code)
        results = analyzer.analyze()
        
        return results
    
    except Exception as e:
        return []