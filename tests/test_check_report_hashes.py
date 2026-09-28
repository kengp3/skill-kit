import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/ai-code-review/scripts/check_report_hashes.py"


class CheckReportHashesTest(unittest.TestCase):
    def test_malformed_entry_cannot_hide_beside_valid_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.py"
            source.write_text("value = 1\n")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            report = root / "report.md"
            for entry in ('SHA-256 `xyz`', 'SHA-256 ``', 'SHA-256 missing',
                          'SHA-256 `' + digest, '`abcd`', '`' + 'a' * 69 + '`'):
                with self.subTest(entry=entry):
                    report.write_text(f"[valid](source.py) SHA-256 `{digest}`\n"
                                      f"[invalid](source.py) {entry}\n")
                    result = subprocess.run([sys.executable, str(SCRIPT), str(report)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn("line 2:", result.stderr)

    def test_angle_path_with_parentheses_spaces_and_line_anchor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source (copy).py"
            source.write_text("value = 1\n")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            report = root / "report.md"
            report.write_text(f"[source](<source (copy).py:1#code>) SHA-256 `{digest.upper()}`\n")
            result = subprocess.run([sys.executable, str(SCRIPT), str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("checked 1", result.stdout)

    def test_unreadable_or_invalid_index_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = root / "invalid.md"
            invalid.write_bytes(b"\xff")
            for report in (root / "missing.md", root, invalid):
                with self.subTest(report=report):
                    result = subprocess.run([sys.executable, str(SCRIPT), str(report)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("cannot read", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_missing_or_directory_evidence_fails_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.md"
            targets = ["missing.py", "."]
            if hasattr(os, "mkfifo"):
                os.mkfifo(Path(directory) / "pipe")
                targets.append("pipe")
            for target in targets:
                with self.subTest(target=target):
                    report.write_text(f"[source]({target}) SHA-256 `{'0' * 64}`\n")
                    result = subprocess.run([sys.executable, str(SCRIPT), str(report)], capture_output=True, text=True, timeout=2)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("line 1: cannot read", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_linked_hash_must_match_local_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.py"
            source.write_text("value = 1\n")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            report = root / "report.md"

            for claimed, label, expected_exit in ((digest, "SHA-256 ", 0), (digest[:-1], "SHA-256 ", 1),
                                                  (digest[:-1], "", 1), ("0" * 64, "", 1)):
                report.write_text(f"[source.py](source.py) {label}`{claimed}`\n")
                result = subprocess.run([sys.executable, str(SCRIPT), str(report)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected_exit, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
