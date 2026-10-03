"""Check artifacts; task decisions require separate independent review."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
baseline = json.loads((root / "baseline.json").read_text())
failures = []
results = {}
for relative in json.loads((root / "protected.json").read_text()):
    p = root / relative
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != baseline[relative]:
        failures.append(f"Protected input changed: {relative}")
if {p.name for p in (root / "plan").glob("*.py")} != {"app.py"}:
    failures.append("plan-only created implementation files")
for case in ("parallel", "resume"):
    run = subprocess.run([sys.executable, "-B", "check.py"], cwd=root / case, text=True, capture_output=True, timeout=20)
    results[case] = {"returncode": run.returncode, "stdout": run.stdout, "stderr": run.stderr}
    if run.returncode:
        failures.append(f"{case} acceptance failed")
for counter in ("probe-attempts.txt", "unavailable-attempts.txt"):
    p = root / "resume" / counter
    results[counter] = p.read_text() if p.exists() else None
    allowed = {"2"} if counter == "probe-attempts.txt" else {"1", "2"}
    if results[counter] not in allowed:
        failures.append(f"Unexpected bounded-retry counter {counter}: {results[counter]}")
if len(sys.argv) > 1:
    current = Path(sys.argv[1])
    for name in ("SKILL.md", "agents/openai.yaml"):
        if (current / name).read_bytes() != (root / "skill" / name).read_bytes():
            failures.append(f"Reviewed skill differs from current: {name}")
results["skill_sha256"] = hashlib.sha256((root / "skill/SKILL.md").read_bytes()).hexdigest()
results["artifact_sha256"] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for case in ("plan", "parallel", "resume") for p in sorted((root / case).rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
results["failures"] = failures
print(json.dumps(results, ensure_ascii=False, indent=2))
sys.exit(bool(failures))
