#!/usr/bin/env python3
"""Check SHA-256 values written next to local Markdown file links."""

import hashlib
import re
import sys
from pathlib import Path


LINK_HASH = re.compile(r"\[[^\]\n]+\]\(([^)\n]+)\)[ \t]*(?:SHA-256[ \t]*`([0-9a-fA-F]+)`|`([0-9a-fA-F]{60,68})`)")


def main(report_name):
    report = Path(report_name).resolve()
    content = report.read_text()
    checked = 0
    errors = []
    for match in LINK_HASH.finditer(content):
        target, labeled, bare = match.groups()
        claimed = labeled or bare
        target = target.strip("<>").split("#", 1)[0]
        target = re.sub(r":\d+$", "", target)
        path = Path(target) if target.startswith("/") else report.parent / target
        line = content.count("\n", 0, match.start()) + 1
        checked += 1
        if not path.is_file():
            errors.append(f"line {line}: cannot read {target}")
        elif len(claimed) != 64 or hashlib.sha256(path.read_bytes()).hexdigest() != claimed.lower():
            errors.append(f"line {line}: SHA-256 mismatch for {target}")
    if not checked:
        errors.append("no linked SHA-256 values found")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"checked {checked} linked SHA-256 values")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: check_report_hashes.py REPORT.md")
    sys.exit(main(sys.argv[1]))
