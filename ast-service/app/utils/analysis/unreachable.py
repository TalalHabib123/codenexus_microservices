import ast
from app.utils.visitors.unreachable_visitor import UnreachableCodeAnalyzer, correct_unreachable_lines, correct_unreachable_unique

def unreachable_code_analysis(code: str) -> list:
    try:
        tree = ast.parse(code)
        analyzer = UnreachableCodeAnalyzer()
        analyzer.visit(tree)
        return correct_unreachable_unique(correct_unreachable_lines(analyzer.unreachable_blocks, code))
    except Exception as e:
        return []