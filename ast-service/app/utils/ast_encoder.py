import ast
import json


class ASTEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ast.AST):
            fields = {k: self.default(v) for k, v in ast.iter_fields(obj)}
            return {
                '_type': obj.__class__.__name__,
                **fields
            }
        elif isinstance(obj, list):
            return [self.default(v) for v in obj]
        elif isinstance(obj, str):
            return obj
        elif isinstance(obj, int):
            return obj
        elif isinstance(obj, float):
            return obj
        elif isinstance(obj, bool):
            return obj
        elif obj is None:
            return obj
        elif obj is Ellipsis:
            return "..."
        else:
            return super().default(obj)
