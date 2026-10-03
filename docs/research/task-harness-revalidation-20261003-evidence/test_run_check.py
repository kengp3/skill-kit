"""Small isolated regression check for command receipts; no third-party packages."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

runner = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix="task-harness-receipt-") as directory:
    root = Path(directory).resolve()
    source = root / "subject.txt"
    source.write_text("input\n")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    def run(name, command, sources=None):
        argv = [sys.executable, str(runner), "--output", str(root / name)]
        for path in [source] if sources is None else sources:
            argv += ["--source", str(path)]
        return subprocess.run(argv + ["--", *command], cwd=root, capture_output=True, text=True)

    literal = "$(no-shell-expansion); data with spaces"
    command = [sys.executable, "-c", "import sys;print(sys.argv[1]);print('stderr',file=sys.stderr)", literal]
    assert run("ok.json", command).returncode == 0
    receipt = json.loads((root / "ok.json").read_text())
    assert receipt["argv"] == command and receipt["cwd"] == str(root)
    assert receipt["returncode"] == 0 and receipt["stdout"] == literal + "\n"
    assert receipt["stderr"] == "stderr\n" and receipt["sources_stable"] is True
    assert receipt["sources_before"] == receipt["sources_after"] == {str(source): digest}

    assert run("bad.json", [sys.executable, "-c", "print('PASS');raise SystemExit(7)"]).returncode == 7
    assert json.loads((root / "bad.json").read_text())["returncode"] == 7
    previous = (root / "bad.json").read_bytes()
    assert run("bad.json", [sys.executable, "-c", "open('replayed','w').close()"]).returncode == 2
    assert not (root / "replayed").exists() and (root / "bad.json").read_bytes() == previous

    assert run("absent.json", [str(root / "missing-executable")]).returncode == 125
    receipt = json.loads((root / "absent.json").read_text())
    assert receipt["state"] == "not_started" and receipt["returncode"] is None
    assert run("no-source.json", [sys.executable, "-c", "open('replayed','w').close()"], [root / "missing-source"]).returncode == 2
    assert not (root / "replayed").exists() and not (root / "no-source.json").exists()

    assert run("drift.json", [sys.executable, "-c", "open('subject.txt','w').write('changed')"]).returncode == 3
    receipt = json.loads((root / "drift.json").read_text())
    assert receipt["state"] == "finished" and receipt["returncode"] == 0
    assert receipt["sources_stable"] is False and receipt["sources_before"] != receipt["sources_after"]
print("PASS: exact receipts, exit7, no replay, launch failure, preflight failure, source drift")
