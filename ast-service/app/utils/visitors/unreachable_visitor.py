import ast

class UnreachableCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.unreachable_blocks = []

    def visit_FunctionDef(self, node):
        # Check within function for unreachable code
        self.check_unreachable_code(node.body)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        # Check within async function for unreachable code
        self.check_unreachable_code(node.body)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        # Check within class methods for unreachable code
        for body_node in node.body:
            if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.check_unreachable_code(body_node.body)
        self.generic_visit(node)

    def visit_If(self, node):
        # Check for constant conditions and unreachable branches
        self.handle_if_statement(node)
        self.generic_visit(node)

    def visit_While(self, node):
        # Check for while loops with constant conditions
        self.handle_while_loop(node)
        self.generic_visit(node)
    
    def visit_For(self, node):
        # Check for for loops with empty iterables
        self.check_unreachable_code(node.body)
        self.generic_visit(node)

    def visit_Try(self, node):
        # Check for redundant exception handlers and code after raise
        self.handle_try_except(node)
        self.generic_visit(node)

    def check_unreachable_code(self, body):
        # Check for unreachable code after return, break, continue, raise within any scope
        reachable = True
        for idx, child in enumerate(body):
            if isinstance(child, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
                reachable = False
            elif not reachable:
                # Any code after return, break, continue, raise is unreachable
                self.unreachable_blocks.append(
                    f"Unreachable code at line {child.lineno} after {body[idx-1].__class__.__name__.lower()} statement"
                )
                reachable = False  # Remain in unreachable state until the end of the block

    def handle_if_statement(self, node, is_elif=False):
        # Check if node is truly an `elif` by checking its context
        block_type = 'elif' if is_elif else 'if'
        
        # Check for constant conditions and unreachable branches
        if isinstance(node.test, ast.Constant):
            if node.test.value is False:
                # Unreachable block due to a constant `False` condition
                self.unreachable_blocks.append(f"Unreachable '{block_type}' block at line {node.lineno}")
                self.mark_unreachable_code(node.body)
            elif node.test.value is True:
                # If condition is `True`, mark `else` and `elif` blocks as unreachable
                if node.orelse:
                    if isinstance(node.orelse[0], ast.If):
                        self.unreachable_blocks.append(f"Unreachable 'elif' block at line {node.orelse[0].lineno}")
                        self.mark_unreachable_code(node.orelse[0].body)
                    else:
                        self.unreachable_blocks.append(f"Unreachable 'else' block at line {node.orelse[0].lineno}")
                        self.mark_unreachable_code(node.orelse)
                # Continue checking reachable code in the block
                self.check_unreachable_code(node.body)
        else:
            # Normal condition, check reachable code
            self.check_unreachable_code(node.body)
            for else_node in node.orelse:
                if isinstance(else_node, ast.If):
                    # Handle `elif` as a nested `if`, and pass `is_elif=True`
                    self.handle_if_statement(else_node, is_elif=True)
                else:
                    # `else` block handling
                    self.check_unreachable_code([else_node])

    def mark_unreachable_code(self, body):
        # Marks all child nodes in the body as unreachable
        for child in body:
            self.unreachable_blocks.append(
                f"Unreachable code at line {child.lineno}"
            )
            if hasattr(child, 'body'):
                self.mark_unreachable_code(child.body)

                
    def handle_while_loop(self, node):
        # Check for while loops that will never execute due to constant conditions
        if isinstance(node.test, ast.Constant):
            if node.test.value is False:
                self.unreachable_blocks.append(f"Unreachable 'while' loop at line {node.lineno}")
                self.check_unreachable_code(node.body)
        else:
            self.check_unreachable_code(node.body)

    def handle_try_except(self, node):
        # Check for general 'Exception' catch-all handlers
        has_general_exception = False
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                if not has_general_exception:
                    self.unreachable_blocks.append(
                        f"General 'Exception' catch-all handler at line {handler.lineno}"
                    )
                has_general_exception = True

        # Check for unreachable code in try/except/finally blocks
        self.check_unreachable_code(node.body)
        for handler in node.handlers:
            self.check_unreachable_code(handler.body)
        if node.finalbody:
            self.check_unreachable_code(node.finalbody)
            
            
def correct_unreachable_lines(unreachable_blocks, code):
    corrected = []
    lines = code.splitlines()

    for block in unreachable_blocks:
        # Extract line number from the message
        if "at line" in block:
            try:
                # Try to extract the line number, ignoring any additional context like "after return statement"
                line_part = block.split("at line")[-1].strip().split()[0]  # Extract the first word after "at line"
                line_number = int(line_part)
                
                # Identify if this line starts with `if`, `elif`, or `else`
                line_content = lines[line_number - 1].strip()
                if line_content.startswith("if"):
                    corrected.append(f"Unreachable 'if' block at line {line_number}")
                elif line_content.startswith("elif"):
                    corrected.append(f"Unreachable 'elif' block at line {line_number}")
                elif line_content.startswith("else"):
                    corrected.append(f"Unreachable 'else' block at line {line_number}")
                else:
                    corrected.append(block)
            except ValueError:
                # If parsing fails, keep the original block
                corrected.append(block)
        else:
            corrected.append(block)

    return corrected