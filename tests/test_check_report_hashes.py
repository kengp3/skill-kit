import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/ai-code-review/scripts/check_report_hashes.py"


class CheckReportHashesTest(unittest.TestCase):
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
