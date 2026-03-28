#!/usr/bin/env python3
"""Fail if tracked source/test files are not UTF-8 encoded."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Focus on files that commonly impact pytest collection and code reviews.
CHECK_EXTENSIONS = {
    ".py",
    ".pyi",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".tsx",
    ".ts",
    ".js",
    ".jsx",
    ".css",
    ".html",
    ".sql",
}

SKIP_SEGMENTS = {
    "frontend/node_modules",
    ".git",
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        if any(segment in line for segment in SKIP_SEGMENTS):
            continue
        path = Path(line)
        if path.suffix in CHECK_EXTENSIONS:
            files.append(path)
    return files


def main() -> int:
    invalid_files: list[Path] = []

    for path in tracked_files():
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            invalid_files.append(path)

    if invalid_files:
        print("Found non-UTF-8 files:", file=sys.stderr)
        for invalid in invalid_files:
            print(f" - {invalid}", file=sys.stderr)
        return 1

    print("UTF-8 check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
