#!/usr/bin/env python3
"""Check SHA-256 values written next to local Markdown file links."""

import hashlib
import re
import sys
from pathlib import Path


LINK_HASH = re.compile(
    r"\[[^\]\n]+\]\((<[^>\n]+>|[^)\n]+)\)[ \t]*"
    r"(?:SHA-256\b[ \t]*(?:`([^`\n]*)`)?|`([0-9a-fA-F]+)`)")


def main(report_name):
    report = Path(report_name).resolve()
    try:
        content = report.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"cannot read {report}: {error}", file=sys.stderr)
        return 1
    checked = 0
    errors = []
    for match in LINK_HASH.finditer(content):
        target, labeled, bare = match.groups()
        claimed = labeled or bare or ""
        target = target.strip("<>").split("#", 1)[0]
        target = re.sub(r":\d+$", "", target)
        path = Path(target) if target.startswith("/") else report.parent / target
        line = content.count("\n", 0, match.start()) + 1
        checked += 1
        if not re.fullmatch(r"[0-9a-fA-F]{64}", claimed):
            errors.append(f"line {line}: invalid SHA-256 for {target}")
            continue
        if not path.is_file():
            errors.append(f"line {line}: cannot read {target}: not a regular file")
            continue
        try:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            errors.append(f"line {line}: cannot read {target}: {error}")
            continue
        if actual != claimed.lower():
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
