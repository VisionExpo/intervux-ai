import ast
import os
import sys
from typing import List, Optional, Set

# =============================================================================
# Boundary Policy Configuration
# =============================================================================

# Modules are located under backend/modules/
MODULE_ROOT = "backend.modules"

# Allowed global packages that modules can always import from
ALLOWED_GLOBALS = {
    "backend.core",
    "backend.infrastructure",
    "backend.models",
    "backend.utils",
    "backend.background",
}

# Rule: modules/<A> cannot import from modules/<B> directly.
# Rule: If modules/<A> imports from modules/<B>, it MUST use 'backend.modules.<B>'
#       and NOT any subpackage (e.g. 'backend.modules.<B>.services').
#       This enforces that only what is exposed in <B>/__init__.py is used.

class BoundaryViolation(Exception):
    def __init__(self, message, file, line, module):
        self.message = message
        self.file = file
        self.line = line
        self.module = module
        super().__init__(message)

class ModuleBoundaryChecker(ast.NodeVisitor):
    def __init__(self, file_path: str, current_module: str):
        self.file_path = file_path
        self.current_module = current_module
        self.violations: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self._check_module_access(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.level > 0:
            # Handle relative imports
            # We normalize them to absolute for checking
            parts = self.file_path.replace('.py', '').replace('\\', '/').split('/')
            # Find 'backend' index
            try:
                backend_idx = parts.index('backend')
                base_parts = parts[backend_idx:-node.level]
                module_name = '.'.join(base_parts)
                if node.module:
                    module_name += f".{node.module}"
                self._check_module_access(module_name, node.lineno)
            except ValueError:
                pass
        elif node.module:
            self._check_module_access(node.module, node.lineno)
        self.generic_visit(node)

    def _check_module_access(self, target_module: str, lineno: int):
        # Only care about backend.modules
        if not target_module.startswith(MODULE_ROOT):
            return

        parts = target_module.split('.')
        if len(parts) < 3: # 'backend.modules'
            return

        target_name = parts[2] # backend.modules.<target_name>

        # 1. Check for cross-module direct imports
        if target_name != self.current_module:
            # It's a cross-module import.
            # Check if it's deeper than the module root.
            if len(parts) > 3:
                # Violation: backend.modules.<other>.<something>
                # Must only import backend.modules.<other>
                self.violations.append(
                    f"L{lineno}: Strict Boundary Violation: Module '{self.current_module}' "
                    f"is importing internals of '{target_name}' via '{target_module}'. "
                    f"Import only from 'backend.modules.{target_name}'."
                )

def get_module_info(file_path: str) -> Optional[str]:
    """Extract module name from file path if it's inside a module."""
    normalized = file_path.replace('\\', '/')
    if '/backend/modules/' in normalized:
        parts = normalized.split('/backend/modules/')[1].split('/')
        return parts[0]
    return None

def check_file(file_path: str) -> List[str]:
    module_name = get_module_info(file_path)
    if not module_name:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
    except Exception as e:
        return [f"Error parsing {file_path}: {e}"]

    checker = ModuleBoundaryChecker(file_path, module_name)
    checker.visit(tree)
    return checker.violations

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    all_violations = []
    
    print(f"Checking module boundaries in {root_dir}/backend/modules...")
    
    for root, _, files in os.walk(os.path.join(root_dir, 'backend', 'modules')):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                violations = check_file(path)
                if violations:
                    print(f"\n{os.path.relpath(path, root_dir)}:")
                    for v in violations:
                        print(f"  {v}")
                        all_violations.append(v)

    if all_violations:
        print(f"\nFound {len(all_violations)} boundary violations.")
        sys.exit(1)
    else:
        print("\nAll module boundaries are clean!")
        sys.exit(0)

if __name__ == "__main__":
    main()
