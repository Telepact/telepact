#!/usr/bin/env python3
"""Validate that public Telepact docs do not contain broken snippet placeholders.

This is intentionally lightweight and targeted: it scans the public-facing
Markdown/docs surfaces that are easy to regress and flags the placeholder
patterns that previously showed up in shipped examples.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_GLOBS = [
    "README.md",
    "doc/*.md",
    "lib/*/README.md",
    "sdk/*/README.md",
    "skills/*/SKILL.md",
]

# Patterns that have historically represented broken copy/paste examples.
BAD_PATTERNS = [
    re.compile(r"\bauth_required\s*=\s*\*\*\*"),
    re.compile(r"\bauthRequired\s*=\s*\*\*\*"),
    re.compile(r"\ballow_credentials\s*=\s*\*\*\*"),
    re.compile(r"^\s*\*\*\*\s*$"),
]


def iter_candidate_files() -> list[Path]:
    files: list[Path] = []
    for pattern in CANDIDATE_GLOBS:
        files.extend(sorted(ROOT.glob(pattern)))
    # Keep only real files and de-duplicate while preserving order.
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in files:
        if path.is_file() and path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def main() -> int:
    problems: list[str] = []

    for path in iter_candidate_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"{path}: unreadable as UTF-8")
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in BAD_PATTERNS:
                if pattern.search(line):
                    problems.append(f"{path}:{lineno}: {line.strip()}")
                    break

    if problems:
        print("Broken docs snippet placeholders found:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"Checked {len(iter_candidate_files())} public docs files: no broken placeholders found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
