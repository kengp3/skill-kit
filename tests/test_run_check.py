"""Check evidence validity and replay protection at the helper's public CLI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import signal
import tempfile
import time
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'skills/task-harness/scripts/run_check.py'


class CheckEvidenceTest(unittest.TestCase):
    @unittest.skipUnless(os.name == 'posix', 'process-group interruption uses POSIX signals')
    def test_interrupted_process_keeps_unknown_outcome(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = Path(temp) / 'result.json'
            marker = Path(temp) / 'started'
            command = [sys.executable, str(HELPER), '--output', str(receipt), '--',
                sys.executable, '-c',
                'from pathlib import Path; import sys,time; Path(sys.argv[1]).touch(); time.sleep(30)',
                str(marker)]
            process = subprocess.Popen(command, start_new_session=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 5
                while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(marker.exists(), 'checker must actually start before interruption')
                os.killpg(process.pid, signal.SIGINT)
                process.communicate(timeout=5)
                self.assertEqual(process.returncode, 130)
                data = json.loads(receipt.read_text())
                self.assertEqual(data['state'], 'unknown')
                self.assertIsNone(data['returncode'])
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()

    def test_inner_failure_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = Path(temp) / 'result.json'
            result = subprocess.run([sys.executable, str(HELPER), '--output', str(receipt),
                '--', sys.executable, '-c', 'print("PASS"); raise SystemExit(7)'],
                capture_output=True)
            self.assertEqual(result.returncode, 7)
            self.assertEqual(json.loads(receipt.read_text())['returncode'], 7)

    def test_existing_receipt_prevents_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = Path(temp) / 'result.json'
            receipt.write_text('{"state":"unknown"}')
            marker = Path(temp) / 'side-effect'
            result = subprocess.run([sys.executable, str(HELPER), '--output', str(receipt),
                '--', sys.executable, '-c',
                'from pathlib import Path; import sys; Path(sys.argv[1]).touch()', str(marker)],
                capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            self.assertEqual(json.loads(receipt.read_text())['state'], 'unknown')

    def test_changed_source_invalidates_success(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source'
            source.write_text('before')
            receipt = Path(temp) / 'result.json'
            result = subprocess.run([sys.executable, str(HELPER), '--output', str(receipt),
                '--source', str(source), '--', sys.executable, '-c',
                'from pathlib import Path; import sys; Path(sys.argv[1]).write_text("after")',
                str(source)], capture_output=True)
            self.assertEqual(result.returncode, 3)
            data = json.loads(receipt.read_text())
            self.assertEqual(data['returncode'], 0)
            self.assertFalse(data['sources_stable'])


if __name__ == '__main__':
    unittest.main()
