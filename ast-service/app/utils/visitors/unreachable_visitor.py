import ast

class UnreachableCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.unreachable_blocks = []

    def visit_FunctionDef(self, node):
        self.detect_unreachable_code(node.body)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.detect_unreachable_code(node.body)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        for body_node in node.body:
            if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.detect_unreachable_code(body_node.body)
        self.generic_visit(node)

    def block_always_returns(self, body):
        if not body:
            return False
        for node in body:
            if isinstance(node, (ast.Return, ast.Raise)):
                return True
            elif isinstance(node, ast.If):
                if self.block_always_returns(node.body) and self.block_always_returns(node.orelse):
                    return True
            elif isinstance(node, (ast.For, ast.While)):
                continue  # Assume loops may not terminate
            elif isinstance(node, ast.Try):
                body_returns = self.block_always_returns(node.body)
                handlers_return = all(self.block_always_returns(h.body) for h in node.handlers)
                orelse_returns = self.block_always_returns(node.orelse)
                finalbody_returns = self.block_always_returns(node.finalbody)
                if body_returns and handlers_return and orelse_returns and finalbody_returns:
                    return True
            else:
                continue
        return False

    def detect_unreachable_code(self, body, reachable=True):
        idx = 0
        while idx < len(body):
            node = body[idx]
            if not reachable:
                self.mark_unreachable_code(body[idx:])
                break  # No need to continue
            if isinstance(node, (ast.Return, ast.Raise)):
                reachable = False
            elif isinstance(node, ast.If):
                if isinstance(node.test, ast.Constant):
                    if node.test.value is True:
                        # 'if True', 'else' block is unreachable
                        message = f"Unreachable 'else' block at line {node.orelse[0].lineno - 1}"
                        self.unreachable_blocks.append(message)
                        self.mark_unreachable_code(node.orelse, block_type='else')
                        self.detect_unreachable_code(node.body, reachable)
                    elif node.test.value is False:
                        # 'if False', 'if' body is unreachable
                        message = f"Unreachable 'if' block at line {node.lineno}"
                        self.unreachable_blocks.append(message)
                        self.mark_unreachable_code(node.body, block_type='if')
                        self.detect_unreachable_code(node.orelse, reachable)
                    else:
                        # Process both
                        self.detect_unreachable_code(node.body, reachable)
                        self.detect_unreachable_code(node.orelse, reachable)
                else:
                    # Process both 'if' and 'else' bodies
                    self.detect_unreachable_code(node.body, reachable)
                    self.detect_unreachable_code(node.orelse, reachable)
                # Update reachability after 'if'
                if self.block_always_returns(node.body) and self.block_always_returns(node.orelse):
                    reachable = False
            elif isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is False:
                    # 'while False', body is unreachable
                    message = f"Unreachable 'while' block at line {node.lineno}"
                    self.unreachable_blocks.append(message)
                    self.mark_unreachable_code(node.body, block_type='while')
                else:
                    # Process 'while' body
                    self.detect_unreachable_code(node.body, reachable)
                # Reachability remains the same after 'while'
            elif isinstance(node, ast.For):
                if isinstance(node.iter, (ast.List, ast.Tuple)) and len(node.iter.elts) == 0:
                    # 'for' over empty list or tuple, body is unreachable
                    message = f"Unreachable 'for' block at line {node.lineno}"
                    self.unreachable_blocks.append(message)
                    self.mark_unreachable_code(node.body, block_type='for')
                else:
                    # Process 'for' body
                    self.detect_unreachable_code(node.body, reachable)
                # Reachability remains the same after 'for'
            elif isinstance(node, ast.Try):
                # Process 'try' block and handlers
                self.detect_unreachable_code(node.body, reachable)
                for handler in node.handlers:
                    self.detect_unreachable_code(handler.body, reachable)
                if node.orelse:
                    self.detect_unreachable_code(node.orelse, reachable)
                if node.finalbody:
                    self.detect_unreachable_code(node.finalbody, reachable)
                # Update reachability after 'try-except'
                body_returns = self.block_always_returns(node.body)
                handlers_return = all(self.block_always_returns(h.body) for h in node.handlers)
                orelse_returns = self.block_always_returns(node.orelse)
                finalbody_returns = self.block_always_returns(node.finalbody)
                if body_returns and handlers_return and orelse_returns and finalbody_returns:
                    reachable = False
            else:
                # Process any other nodes with bodies
                if hasattr(node, 'body'):
                    self.detect_unreachable_code(node.body, reachable)
            idx += 1

    def mark_unreachable_code(self, body, block_type=None):
        for node in body:
            message = f"Unreachable code at line {node.lineno}"
            self.unreachable_blocks.append(message)
            # Now, recursively process any nested bodies
            if isinstance(node, ast.If):
                # For 'if' statements, pass 'if' or 'else' as the block type
                message = f"Unreachable 'if' block at line {node.lineno}"
                self.unreachable_blocks.append(message)
                self.mark_unreachable_code(node.body, block_type='if')
                message = f"Unreachable 'else' block at line {node.orelse[0].lineno}"
                self.unreachable_blocks.append(message)
                self.mark_unreachable_code(node.orelse, block_type='else')
            elif isinstance(node, (ast.For, ast.While)):
                # For loops, pass the loop type
                loop_type = 'for' if isinstance(node, ast.For) else 'while'
                message = f"Unreachable '{loop_type}' block at line {node.lineno}"
                self.unreachable_blocks.append(message)
                self.mark_unreachable_code(node.body, block_type=loop_type)
                if node.orelse:
                    message = f"Unreachable 'else' block at line {node.orelse[0].lineno}"
                    self.unreachable_blocks.append(message)
                    self.mark_unreachable_code(node.orelse, block_type='else')
            elif isinstance(node, ast.Try):
                # For 'try' blocks, handle all components
                message = f"Unreachable 'try' block at line {node.lineno}"
                self.unreachable_blocks.append(message)
                self.mark_unreachable_code(node.body, block_type='try')
                for handler in node.handlers:
                    message = f"Unreachable 'except' block at line {handler.lineno}"
                    self.unreachable_blocks.append(message)
                    self.mark_unreachable_code(handler.body, block_type='except')
                if node.orelse:
                    message = f"Unreachable 'else' block at line {node.orelse[0].lineno}"
                    self.unreachable_blocks.append(message)
                    self.mark_unreachable_code(node.orelse, block_type='else')
                if node.finalbody:
                    message = f"Unreachable 'finally' block at line {node.finalbody[0].lineno}"
                    self.unreachable_blocks.append(message)
                    self.mark_unreachable_code(node.finalbody, block_type='finally')
            elif hasattr(node, 'body'):
                # For other nodes with a body, process without block_type
                self.mark_unreachable_code(node.body)
   

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

def correct_unreachable_unique(unreachable_blocks):
    # Remove duplicates and sort by line number
    unique_blocks = list(set(unreachable_blocks))
    unique_blocks.sort(key=lambda x: int(x.split('line')[-1]))
    return unique_blocks