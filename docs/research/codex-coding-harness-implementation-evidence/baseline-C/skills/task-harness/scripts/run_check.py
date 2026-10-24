"""Capture one small, noninteractive check. No shell expansion or automatic retry."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def fingerprints(paths):
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("provide one command after --")
    sources = [path.resolve() for path in args.source]
    try:
        before = fingerprints(sources)
    except OSError as error:
        parser.error(f"source cannot be fingerprinted; command not run: {error}")
    receipt = {"argv": command, "cwd": str(Path.cwd()), "state": "started",
               "returncode": None, "stdout": None, "stderr": None,
               "sources_before": before, "sources_after": None, "sources_stable": None}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Reserve before launching: an existing receipt never causes a replay.
    try:
        with args.output.open("x") as stream:
            json.dump(receipt, stream, indent=2)
    except FileExistsError:
        parser.error("receipt already exists; reconcile it or choose a new authorized attempt")
    try:
        result = subprocess.run(command, capture_output=True, text=True, errors="replace")
        receipt.update(state="finished", returncode=result.returncode,
                       stdout=result.stdout, stderr=result.stderr)
        outcome = result.returncode if result.returncode >= 0 else 128 - result.returncode
    except OSError as error:
        receipt.update(state="not_started", error=str(error))
        outcome = 125
    except KeyboardInterrupt:
        receipt.update(state="unknown", error="Interrupted; inspect resulting state before retrying")
        outcome = 130
    try:
        receipt["sources_after"] = fingerprints(sources)
        receipt["sources_stable"] = before == receipt["sources_after"]
    except OSError as error:
        receipt.update(sources_stable=False, fingerprint_error=str(error))
    if outcome == 0 and not receipt["sources_stable"]:
        outcome = 3
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(args.output.resolve())
    return outcome


if __name__ == "__main__":
    sys.exit(main())
