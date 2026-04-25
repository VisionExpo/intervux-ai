import ast
import os
import sys
from pathlib import Path

def check_boundaries(root_dir: str):
    root = Path(root_dir)
    backend_dir = root / "backend"
    modules_dir = backend_dir / "modules"
    violations = []

    if not backend_dir.exists():
        print(f"Error: {backend_dir} not found.")
        return False

    # Identify all modules
    module_names = []
    if modules_dir.exists():
        module_names = [d.name for d in modules_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
    
    # Scan all python files in backend
    for py_file in backend_dir.rglob("*.py"):
        relative_path = py_file.relative_to(root)
        
        # Determine if this file is inside a module
        current_module = None
        if str(py_file).startswith(str(modules_dir)):
            parts = py_file.relative_to(modules_dir).parts
            if parts:
                current_module = parts[0]

        with open(py_file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Error parsing {relative_path}: {e}")
                continue

            for node in ast.walk(tree):
                target_module = None
                
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target_module = alias.name
                elif isinstance(node, ast.ImportFrom):
                    target_module = node.module

                if target_module:
                    parts = target_module.split(".")
                    
                    # 1. Check for cross-module imports (Module A -> Module B)
                    if len(parts) >= 3 and parts[0] == "backend" and parts[1] == "modules":
                        imported_module = parts[2]
                        if current_module and imported_module != current_module and imported_module in module_names:
                            violations.append(
                                f"CROSS-MODULE VIOLATION: {relative_path} imports from '{imported_module}'"
                            )
                        
                        # 2. Check for internal access (starts with _)
                        # If any part after the module name starts with _
                        # e.g. backend.modules.interview._internal
                        if len(parts) > 3:
                            for part in parts[3:]:
                                if part.startswith("_"):
                                    # Violation if importing from OUTSIDE that specific module
                                    if imported_module != current_module:
                                        violations.append(
                                            f"PRIVATE ACCESS VIOLATION: {relative_path} imports internal '{part}' from '{imported_module}'"
                                        )
                                        break
                        
                        # Special case: backend.modules.interview._something
                        elif len(parts) == 3:
                            # If it's a "from backend.modules import _interview" (unlikely but possible)
                            pass

                    # Also check ImportFrom names for private access
                    if isinstance(node, ast.ImportFrom) and node.module:
                        m_parts = node.module.split(".")
                        if len(m_parts) >= 3 and m_parts[0] == "backend" and m_parts[1] == "modules":
                            imp_mod = m_parts[2]
                            if imp_mod != current_module:
                                for alias in node.names:
                                    if alias.name.startswith("_"):
                                        violations.append(
                                            f"PRIVATE ACCESS VIOLATION: {relative_path} imports internal '{alias.name}' from '{imp_mod}'"
                                        )

    if violations:
        print("\n".join(violations))
        print(f"\nTotal violations: {len(violations)}")
        return False
    
    print("No module boundary violations found.")
    return True

if __name__ == "__main__":
    success = check_boundaries(".")
    if not success:
        sys.exit(1)
    sys.exit(0)
