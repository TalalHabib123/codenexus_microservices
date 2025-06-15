from __future__ import annotations

from app.utils.Mappers import (
    class_mapper,
    function_mapper
)
from app.utils.code_validator import is_valid_python_code

import re
import ast
from typing import List, Tuple

SEP_OBJ   = "# === PARAM_OBJECT_SECTION ==="      # surrounds parameter object
SEP_CALLS = "# --- CALL_SITE_SEPARATOR ---"       # separates call‑site pairs

def map_class(orginal_code, class_name, refactor_snippet):
    try:    
        code = class_mapper.replace_class_in_code(orginal_code, class_name, refactor_snippet)
        if not is_valid_python_code(code):
            raise Exception("Invalid Python code")
        
        return {
            "refactored_code": code,
            "success": True
        }  
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }   
        
def map_function(orginal_code, function_name, refactor_snippet):
    try:
        code = function_mapper.replace_function_in_code(orginal_code, function_name, refactor_snippet)
        if not is_valid_python_code(code):
            raise Exception("Invalid Python code")
        return {
            "refactored_code": code,
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 
        
def map_orginal_code(orginal_code):
    # if not is_valid_python_code(orginal_code):
    #     return {
    #         "success": False,
    #         "error": "Invalid Python code"
    #     }
    return {
        "refactored_code": orginal_code,
        "success": True
    }    
    
def _parse_llm_block(block: str) -> tuple[str, List[Tuple[str, str]]]:
    """Extract the parameter-object definition and call-site pairs.

    The LLM returns blocks like::

        # === PARAM_OBJECT_SECTION ===
        class ParamObj: ...
        # === PARAM_OBJECT_SECTION ===
        # --- CALL_SITE_SEPARATOR ---
        # a = foo(1, 2, 3)
        a = foo(ParamObj(1, 2, 3))
        # --- CALL_SITE_SEPARATOR ---
        # b = foo(4, 5, 6)
        b = foo(ParamObj(4, 5, 6))
        # --- CALL_SITE_SEPARATOR ---

    We split on the separators and build *(original, updated)* tuples.
    """
    parts = block.split(SEP_OBJ)
    if len(parts) >= 3:
        _, param_obj, calls_part = parts[:3]
        param_obj = param_obj.strip("\n")
    else:
        param_obj = ""
        calls_part = parts[0]

    chunks = [c.strip() for c in calls_part.split(SEP_CALLS) if c.strip()]
    pairs: List[Tuple[str, str]] = []

    for chunk in chunks:
        lines = [ln for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        # First non-blank line should be the commented original
        first = lines[0].lstrip()
        if first.startswith("#"):
            orig = first.lstrip("# ").rstrip()
            updated = "\n".join(lines[1:]).rstrip()
        else:
            # Fallback if comment was stripped – assume 1-line original
            orig = first.rstrip()
            updated = "\n".join(lines[1:]).rstrip()
        if orig and updated:
            pairs.append((orig, updated))
    return param_obj, pairs


# ──────────────────────────────────────────────────────────────────────────────
# Helper: canonicalise python snippet (strip ALL whitespace)
# ──────────────────────────────────────────────────────────────────────────────

def _canonical(text: str) -> str:
    return re.sub(r"\s+", "", text)


# ──────────────────────────────────────────────────────────────────────────────
# Core – apply patch
# ──────────────────────────────────────────────────────────────────────────────

def apply_llm_patch(
    original_code: str,
    llm_response_block: str,
    skip_param_object: bool = False,
) -> str:
    """Merge an LLM refactor block back into *original_code*.

    Parameters
    ----------
    original_code:
        The full source of the file **before** refactor.
    llm_response_block:
        One block from the LLM (for this file) containing the parameter object
        and updated call‑sites in the agreed format.
    skip_param_object:
        When *True*, the parameter‑object definition (if any) is NOT injected.
    """
    print(llm_response_block)
    param_obj, call_pairs = _parse_llm_block(llm_response_block)
    print(call_pairs)

    # Early exit if nothing to do
    if not call_pairs and (not param_obj or skip_param_object):
        return original_code

    try:
        tree = ast.parse(original_code)
    except Exception as e:
        return {
            "sucess": False,
            "error": str(e)
        }
    try:
        lines = original_code.splitlines()
        targets: List[Tuple[int, int, str]] = []  # (start_lineno, end_lineno, new_call)
        remaining_pairs = call_pairs.copy()

        # Utility to attempt matching a code segment with remaining_pairs
        def _match(segment: str) -> Tuple[str, str] | None:
            canon_seg = _canonical(segment)
            for idx, (orig, new) in enumerate(remaining_pairs):
                canon_full = _canonical(orig)
                canon_rhs  = _canonical(orig.split("=", 1)[-1])  # handle assignment‑free call
                if canon_seg in {canon_full, canon_rhs}:
                    return remaining_pairs.pop(idx)
            return None

        # Walk AST: capture Assign, Expr(Call) and naked Call nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                seg = ast.get_source_segment(original_code, node) or ""
                match = _match(seg)
                if match:
                    targets.append((node.lineno, node.end_lineno, match[1]))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                seg = ast.get_source_segment(original_code, node) or ""
                match = _match(seg)
                if match:
                    targets.append((node.lineno, node.end_lineno, match[1]))
            elif isinstance(node, ast.Call):
                # Fallback for inline calls (e.g., passed as arg to another call)
                seg = ast.get_source_segment(original_code, node) or ""
                match = _match(seg)
                if match:
                    targets.append((node.lineno, node.end_lineno, match[1]))

        # Sort bottom‑up to keep line numbers stable during replacement
        targets.sort(key=lambda t: (t[0], t[1]), reverse=True)

        for start, end, replacement in targets:
            indent = re.match(r"^\s*", lines[start - 1]).group(0)
            repl_lines = [indent + ln for ln in replacement.splitlines()]
            lines[start - 1 : end] = repl_lines

        # Inject parameter object after last import (unless skipped)
        if param_obj and not skip_param_object:
            imp_idxs = [i for i, ln in enumerate(lines) if re.match(r"^\s*(import|from)\s+", ln)]
            insert_at = (imp_idxs[-1] + 1) if imp_idxs else 0
            needs_nl  = insert_at > 0 and lines[insert_at - 1].strip() != ""
            obj_block = ("\n" if needs_nl else "") + param_obj + "\n"
            lines.insert(insert_at, obj_block)

        return {
            "refactored_code":"\n".join(lines) + ("\n" if not original_code.endswith("\n") else ""),
            "success" : True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ──────────────────────────────────────────────────────────────────────────────
# Minimal self‑test (remove or replace with proper unit tests in production)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    _orig = (
        "import math\n\n"
        "discount1 = calculate_discount(100, \"regular\", \"Monday\", True, \"VIP123\")\n"
        "discount2 = calculate_discount(200, \"regular\", \"Saturday\", False, \"SAVE20\")\n"
    )

    _llm = (
        "# === PARAM_OBJECT_SECTION ===\n"
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class DiscountParameters:\n"
        "    price: float\n"
        "    customer_type: str\n"
        "    day_of_week: str\n"
        "    is_member: bool\n"
        "    coupon_code: str\n"
        "# === PARAM_OBJECT_SECTION ===\n"
        "# --- CALL_SITE_SEPARATOR ---\n"
        "# discount1 = calculate_discount(100, \"regular\", \"Monday\", True, \"VIP123\")\n"
        "discount1 = calculate_discount(DiscountParameters(100, \"regular\", \"Monday\", True, \"VIP123\"))\n"
        "# --- CALL_SITE_SEPARATOR ---\n"
        "# discount2 = calculate_discount(200, \"regular\", \"Saturday\", False, \"SAVE20\")\n"
        "discount2 = calculate_discount(DiscountParameters(200, \"regular\", \"Saturday\", False, \"SAVE20\"))\n"
        "# --- CALL_SITE_SEPARATOR ---"
    )

    print(apply_llm_patch(_orig, _llm))