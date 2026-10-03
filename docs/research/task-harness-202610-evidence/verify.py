"""Recheck fixture behavior; task decisions also require reading each plan."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
results = {}
assert (root / "plan/app.py").read_text() == "def total(values):\n    return sum(values)\n"
assert {p.name for p in (root / "plan").glob("*.py")} == {"app.py"}
results["plan_source_unchanged"] = True
for case in ("plan", "execute", "resume"):
    assert (root / case / "user-note.txt").read_text() == "Keep this unrelated note unchanged.\n"
for case in ("execute", "resume"):
    result = subprocess.run(
        [sys.executable, "-B", "check.py"], cwd=root / case,
        text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, (case, result.stdout, result.stderr)
    results[case] = {"returncode": result.returncode, "stdout": result.stdout.strip()}
assert (root / "resume/deliveries.txt").read_text() == "sent receipt\n"
results["exactly_one_delivery"] = True
results["source_sha256"] = {
    str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
    for case in ("plan", "execute", "resume")
    for p in sorted((root / case).glob("*.py"))
}
print(json.dumps(results, ensure_ascii=False, indent=2))
