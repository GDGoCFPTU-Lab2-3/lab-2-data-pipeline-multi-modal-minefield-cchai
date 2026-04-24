import ast
import re
import os

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    # ------------------------------------------
    
    # Use the 'ast' module to find docstrings for functions safely
    docstrings = []
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                doc = ast.get_docstring(node)
                if doc:
                    name = getattr(node, 'name', 'module')
                    docstrings.append(f"{name}: {doc}")
    except SyntaxError:
        pass
        
    combined_docstrings = "\n".join(docstrings)
    
    # Use regex to find business rules in comments like "# Business Logic Rule 001"
    business_rules = []
    rule_pattern = re.compile(r'#\s*(Business Logic Rule\s*\d+.*)', re.IGNORECASE)
    for match in rule_pattern.finditer(source_code):
        business_rules.append(match.group(1))
        
    return {
        "document_id": f"code_{os.path.basename(file_path)}",
        "content": combined_docstrings if combined_docstrings else "No docstrings found",
        "source_type": "Code",
        "author": "Legacy Developer",
        "metadata": {
            "business_rules": business_rules,
            "raw_comments": re.findall(r'#.*', source_code)
        }
    }

