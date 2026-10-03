"""Verify resulting artifacts; coordination decisions require evidence review."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
baseline = json.loads((root / "baseline.json").read_text())
protected = [p for p in baseline if p.startswith("skill/") or p.endswith(("user-note.txt", "other-plan.md", "project-setting.md", "check.py", "send.py", "deliveries.txt")) or p == "plan/app.py"]
for relative in protected:
    actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    assert actual == baseline[relative], f"Protected input changed: {relative}"
assert {p.name for p in (root / "plan").glob("*.py")} == {"app.py"}
results = {"protected_files": len(protected), "checks": {}}
for case in ("parallel", "resume"):
    completed = subprocess.run([sys.executable, "-B", "check.py"], cwd=root / case, text=True, capture_output=True, timeout=20)
    assert completed.returncode == 0, (case, completed.stdout, completed.stderr)
    results["checks"][case] = completed.stdout.strip()
for name in ("app.py", "user-note.txt", "other-plan.md", "project-setting.md"):
    assert hashlib.sha256((root / "plan-fixed" / name).read_bytes()).hexdigest() == baseline["plan/" + name]
assert {p.name for p in (root / "plan-fixed").glob("*.py")} == {"app.py"}
results["skill_sha256"] = {version: hashlib.sha256((root / version / "SKILL.md").read_bytes()).hexdigest() for version in ("skill", "skill-final")}
if len(sys.argv) > 1:
    current = Path(sys.argv[1])
    for name in ("SKILL.md", "agents/openai.yaml"):
        assert (current / name).read_bytes() == (root / "skill-final" / name).read_bytes(), f"Current skill differs: {name}"
    results["current_skill_matches"] = True
results["artifact_sha256"] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for case in ("plan", "plan-fixed", "parallel", "resume") for p in sorted((root / case).rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
print(json.dumps(results, ensure_ascii=False, indent=2))
