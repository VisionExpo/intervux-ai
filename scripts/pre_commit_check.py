#!/usr/bin/env python3
"""
Pre-commit hook: Run architectural boundary check and smoke tests.

Installed at: .git/hooks/pre-commit
Make executable: chmod +x .git/hooks/pre-commit  (Linux/Mac)
                 (Windows: runs via Python directly)

Developer bypass (for WIP commits):
    git commit --no-verify -m "WIP: ..."
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root from .git/hooks/


def run(cmd: list[str], label: str) -> bool:
    """Run a command and return True on success."""
    print(f"\n🔍 pre-commit: {label}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"❌ BLOCKED: {label} failed. Fix violations before committing.")
        print("   (Use 'git commit --no-verify' to bypass for WIP commits)")
        return False
    print(f"✅ {label} passed")
    return True


def main() -> int:
    checks = [
        (
            [sys.executable, "scripts/check_module_boundaries.py"],
            "Module boundary audit",
        ),
        (
            [sys.executable, "-m", "pytest", "-m", "smoke", "-q", "--tb=short", "-W", "error"],
            "Smoke tests (critical path)",
        ),
    ]

    failed = [label for cmd, label in checks if not run(cmd, label)]

    if failed:
        print(f"\n⛔ Commit blocked by {len(failed)} check(s): {failed}")
        return 1

    print("\n✅ All pre-commit checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
