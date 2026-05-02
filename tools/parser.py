import ast

def get_code_structure(code: str):
    tree = ast.parse(code)
    structure = {"functions": [], "classes": [], "imports": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            structure["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            structure["classes"].append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            # Esto es vital para el grafo de NetworkX después
            structure["imports"].append(ast.dump(node)) 
            
    return structure