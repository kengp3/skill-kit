"""Combine cancellation evidence with the same-deadline continuation contract."""
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

from harness.boundary import Limits, run
from harness.control import TrialControl


class P0IntegrationTest(unittest.TestCase):
    def test_cancelled_process_evidence_does_not_replace_native_reconciliation(self):
        control = TrialControl(started_at=time.monotonic(), wall_seconds=5)
        control.bind('recorded-root', 'first-turn')
        deadline = control.deadline
        control.request_cancel()
        cancel = threading.Event()
        timer = threading.Timer(.15, cancel.set)
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp).resolve()
            timer.start()
            try:
                result = run([sys.executable, '-B', '-c',
                    'import subprocess,time; subprocess.Popen(["/bin/sleep","30"]); time.sleep(30)'],
                    workspace=workspace, cancel=cancel,
                    limits=Limits(wall_seconds=3, cpu_seconds=2,
                                  memory_mb=256, max_processes=3))
            finally:
                timer.cancel()
                timer.join()
        self.assertEqual(result.status, 'cancelled')
        self.assertEqual(result.remaining_pids, ())
        control.confirm_writers_stopped(not result.remaining_pids)
        with self.assertRaises(ValueError):
            control.resume('continuation', now=time.monotonic(), allow_after_cancel=True)
        self.assertTrue(control.reconcile_readback({'thread': {
            'id': 'recorded-root', 'turns': [{'id': 'first-turn', 'status': 'interrupted'}]}}))
        with self.assertRaises(ValueError):
            control.resume('continuation', now=time.monotonic(), allow_after_cancel=True)
        control.confirm_writers_stopped(not result.remaining_pids)
        control.resume('continuation', now=time.monotonic(), allow_after_cancel=True)
        self.assertEqual(control.deadline, deadline)
        self.assertLess(control.remaining(now=time.monotonic()), 5)


if __name__ == '__main__':
    unittest.main()
