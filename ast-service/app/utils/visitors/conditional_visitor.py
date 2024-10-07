import ast
import astor

class ConditionComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self, lines):
        self.lines = lines
        self.complex_conditions = []

    def visit_If(self, node):
        self._analyze_condition(node.test, node)
        self.generic_visit(node)  
    
    def visit_While(self, node):
        self._analyze_condition(node.test, node)
        self.generic_visit(node)
    
    def visit_For(self, node):
        if node.orelse:
            self._analyze_else_block(node.orelse, node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.generic_visit(node)

    def _analyze_condition(self, test_node, node):
        complexity_score = self._calculate_condition_complexity(test_node)
        line_start = node.lineno
        line_end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno

        if complexity_score > 3:
            condition_details = {
                'line_range': (line_start, line_end),
                'condition_code': astor.to_source(test_node).strip(),
                'complexity_score': complexity_score,
                'code_block': self._get_code_block(line_start, line_end)
            }
            self.complex_conditions.append(condition_details)
    
    def _analyze_else_block(self, orelse_nodes, node):
        for orelse_node in orelse_nodes:
            if isinstance(orelse_node, (ast.If, ast.While, ast.For)):
                self._analyze_condition(orelse_node.test, orelse_node)

    def _calculate_condition_complexity(self, test_node):
        """
        Calculate the complexity score of a condition based on nesting,
        logical operators, and length of expression.
        """
        complexity = 0

        if isinstance(test_node, ast.BoolOp):
            complexity += len(test_node.values) 
        
        # Check for comparisons (==, >, <, etc.)
        elif isinstance(test_node, ast.Compare):
            complexity += len(test_node.comparators) 

        # Check for unary operations (not, ~)
        elif isinstance(test_node, ast.UnaryOp):
            complexity += 1  # Unary operators add to complexity

        # Calculate depth of nested expressions
        complexity += self._calculate_depth(test_node)
        return complexity

    def _calculate_depth(self, node, depth=0):
        """Calculate the nesting depth of the condition."""
        if isinstance(node, (ast.BoolOp, ast.BinOp, ast.Compare)):
            return 1 + max(self._calculate_depth(child) for child in ast.iter_child_nodes(node))
        return 0

    def _get_code_block(self, start_line, end_line):
        """Retrieve the code block for the node using line numbers."""
        return ''.join(self.lines[start_line - 1:end_line])

    def analyze(self):
        return self.complex_conditions