"""Exercise the development boundary through real local child processes."""
from pathlib import Path
import sys
import os
import socket
import subprocess
import threading
import time
from unittest.mock import patch
import tempfile
import unittest

from harness.boundary import Limits, run
from harness.boundary import BoundaryUnavailable


class BoundaryTest(unittest.TestCase):
    def test_can_write_only_in_disposable_workspace(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            base = Path(temporary).resolve()
            workspace = base / 'execution'
            workspace.mkdir()
            outside = base / 'daily.txt'
            outside.write_text('keep')
            command = [sys.executable, '-c',
                'from pathlib import Path; import sys; '
                'Path("inside.txt").write_text("ok"); '
                'Path(sys.argv[1]).write_text("bad")', str(outside)]
            result = run(command, workspace=workspace, limits=Limits())
            self.assertEqual(result.status, 'completed')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((workspace / 'inside.txt').read_text(), 'ok')
            self.assertEqual(outside.read_text(), 'keep')

    def test_existing_output_alias_cannot_overwrite_daily_file(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            base = Path(temporary).resolve()
            workspace = base / 'execution'
            workspace.mkdir()
            daily = base / 'daily.txt'
            daily.write_text('keep')
            (workspace / '.stdout').symlink_to(daily)
            with self.assertRaises((ValueError, FileExistsError)):
                run([sys.executable, '-c', 'print("bad")'], workspace=workspace)
            self.assertEqual(daily.read_text(), 'keep')

    def execute(self, code, *arguments, limits=Limits(), cancel=None):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            return run([sys.executable, '-c', code, *arguments],
                       workspace=Path(temporary).resolve(), limits=limits, cancel=cancel)

    def test_real_loopback_listener_is_unreachable(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen(1)
            port = listener.getsockname()[1]
            result = self.execute('import socket,sys; socket.create_connection(("127.0.0.1",int(sys.argv[1])))', str(port))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('PermissionError', result.stderr)

    def test_runtime_symlink_cannot_escape_write_scope(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            base = Path(temporary).resolve()
            daily = base / 'daily.txt'
            daily.write_text('keep')
            workspace = base / 'execution'; workspace.mkdir()
            result = run([sys.executable, '-c',
                'from pathlib import Path;import sys; '
                'Path("escape").symlink_to(sys.argv[1]); '
                'Path("escape").write_text("bad")', str(daily)], workspace=workspace)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(daily.read_text(), 'keep')

    def test_child_receives_only_isolated_state_and_explicit_toolchain(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'boundary-test-not-a-key', 'PYTHONPATH': '/nonexistent'}):
            result = self.execute('import os;print(os.environ.get("OPENAI_API_KEY")); '
                                  'print(os.environ.get("PYTHONPATH")); '
                                  'print(os.environ["HOME"]);print(os.environ["TMPDIR"])')
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[:2], ['None', 'None'])
        self.assertIn('harness-boundary-', lines[2])
        self.assertTrue(lines[3].endswith('/tmp'))

    def test_memory_cpu_and_process_count_guards_stop_owned_job(self):
        cases = [
            ('import time; data=bytearray(100*1024*1024);time.sleep(3)', Limits(memory_mb=64), 'memory_limit'),
            ('while True: pass', Limits(cpu_seconds=.1), 'cpu_limit'),
            ('import subprocess,time; p=subprocess.Popen(["/bin/sleep","3"]);time.sleep(3)', Limits(max_processes=1), 'process_limit'),
        ]
        for code, limits, expected in cases:
            with self.subTest(expected=expected):
                result = self.execute(code, limits=limits)
                self.assertEqual(result.status, expected, result.stderr)
                self.assertEqual(result.remaining_pids, ())

    def test_timeout_and_cancel_reap_children_without_touching_unrelated_worker(self):
        for cancel_job in (False, True):
            with self.subTest(cancel=cancel_job), tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
                base=Path(temporary).resolve()
                outsider=subprocess.Popen(['/bin/sleep','10'], start_new_session=True)
                cancel=threading.Event()
                timer=threading.Timer(.2, cancel.set) if cancel_job else None
                if timer: timer.start()
                try:
                    workspace=base/'execution';workspace.mkdir()
                    code=('import subprocess,time;from pathlib import Path; '
                          'child=subprocess.Popen(["/bin/sleep","10"]); '
                          'Path("child.pid").write_text(str(child.pid));time.sleep(10)')
                    result=run([sys.executable,'-c',code],workspace=workspace,
                               limits=Limits(wall_seconds=.4),cancel=cancel)
                    self.assertEqual(result.status, 'cancelled' if cancel_job else 'timeout')
                    self.assertEqual(result.remaining_pids, ())
                    self.assertIsNone(outsider.poll())
                    child=int((workspace/'child.pid').read_text())
                    with self.assertRaises(ProcessLookupError): os.kill(child,0)
                finally:
                    if timer: timer.cancel();timer.join()
                    outsider.terminate();outsider.wait(timeout=2)

    def test_parent_exit_and_failure_also_reap_remaining_child(self):
        for exit_code in (0, 3):
            with self.subTest(exit_code=exit_code), tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
                workspace=Path(temporary).resolve()
                code=('import subprocess,sys;from pathlib import Path; '
                      'child=subprocess.Popen(["/bin/sleep","10"]); '
                      'Path("child.pid").write_text(str(child.pid));sys.exit(int(sys.argv[1]))')
                result=run([sys.executable,'-c',code,str(exit_code)],workspace=workspace)
                self.assertEqual(result.returncode, exit_code)
                self.assertEqual(result.remaining_pids, ())
                child=int((workspace/'child.pid').read_text())
                with self.assertRaises(ProcessLookupError): os.kill(child,0)

    def test_unknown_daily_root_and_model_command_are_rejected(self):
        with self.assertRaises(ValueError):
            run([sys.executable, '-c', 'pass'], workspace=Path.home())
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            with self.assertRaises(ValueError):
                run(['/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex', 'app-server'],
                    workspace=Path(temporary).resolve())

    def test_unavailable_sandbox_fails_closed_before_child_execution(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            workspace = Path(temporary).resolve()
            with patch('harness.boundary.sys.platform', 'unsupported'):
                with self.assertRaises(BoundaryUnavailable):
                    run([sys.executable, '-c', 'open("bad","w").write("bad")'],workspace=workspace)
            self.assertEqual(list(workspace.iterdir()), [])

    def test_existing_attempt_is_not_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            workspace = Path(temporary).resolve()
            self.assertEqual(run(['/usr/bin/true'],workspace=workspace).returncode,0)
            original=(workspace/'.stdout').read_bytes()
            with self.assertRaises(ValueError):
                run(['/usr/bin/true'],workspace=workspace)
            self.assertEqual((workspace/'.stdout').read_bytes(),original)

    def test_file_size_guard_bounds_writable_output(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            workspace = Path(temporary).resolve()
            result=run([sys.executable,'-c','open("blob","wb").write(b"x"*(17*1024*1024))'],workspace=workspace)
            self.assertNotEqual(result.returncode,0)
            self.assertLessEqual((workspace/'blob').stat().st_size,16*1024*1024)

    def test_only_one_owned_job_runs_at_a_time(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            base = Path(temporary).resolve()
            first=base/'first';first.mkdir()
            second=base/'second';second.mkdir()
            results=[]
            worker=threading.Thread(target=lambda: results.append(run(['/bin/sleep','.5'],workspace=first)))
            worker.start()
            try:
                deadline=time.monotonic()+2
                while not (first/'.stdout').exists() and time.monotonic()<deadline:
                    time.sleep(.01)
                with self.assertRaises(BoundaryUnavailable):
                    run(['/usr/bin/true'],workspace=second)
            finally:
                worker.join(timeout=3)
            self.assertFalse(worker.is_alive())
            self.assertEqual(results[0].returncode,0)


    def test_monitor_failure_still_terminates_owned_group_and_preserves_unrelated_worker(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            base = Path(temporary).resolve()
            workspace = base / 'execution'; workspace.mkdir()
            pid_file = workspace / 'pids'
            outsider = subprocess.Popen(['/bin/sleep', '10'], start_new_session=True)
            original_run = subprocess.run
            parent = None
            def unavailable(command, *args, **kwargs):
                if command[0] != '/bin/ps':
                    return original_run(command, *args, **kwargs)
                deadline = time.monotonic() + 1
                while not pid_file.exists() and time.monotonic() < deadline:
                    time.sleep(.01)
                raise subprocess.CalledProcessError(1, command, stderr='monitor unavailable')
            try:
                code = ('import os,subprocess,time;from pathlib import Path; '
                        'child=subprocess.Popen(["/bin/sleep","10"]); '
                        'Path("pids").write_text(str(os.getpid())+" "+str(child.pid));time.sleep(10)')
                started = time.monotonic()
                with patch('harness.boundary.subprocess.run', side_effect=unavailable):
                    with self.assertRaises(BoundaryUnavailable):
                        run([sys.executable, '-c', code], workspace=workspace,
                            limits=Limits(wall_seconds=3))
                self.assertLess(time.monotonic() - started, 3)
                pids = [int(value) for value in pid_file.read_text().split()]
                parent = pids[0]
                deadline = time.monotonic() + 2
                for pid in pids:
                    while time.monotonic() < deadline:
                        try:
                            os.kill(pid, 0)
                        except ProcessLookupError:
                            break
                        time.sleep(.01)
                    with self.assertRaises(ProcessLookupError):
                        os.kill(pid, 0)
                self.assertIsNone(outsider.poll())
            finally:
                if pid_file.exists():
                    parent = int(pid_file.read_text().split()[0])
                if parent is not None:
                    try:
                        os.killpg(parent, 9)
                    except ProcessLookupError:
                        pass
                outsider.terminate(); outsider.wait(timeout=2)


    def test_threaded_launch_needs_no_preexec_callback_and_remains_bounded(self):
        with tempfile.TemporaryDirectory(prefix='harness-boundary-') as temporary:
            workspace = Path(temporary).resolve()
            original_popen = subprocess.Popen
            results, errors = [], []
            def safe_popen(*args, **kwargs):
                if kwargs.get('preexec_fn') is not None:
                    raise RuntimeError('pre-exec callbacks unavailable in a threaded caller')
                return original_popen(*args, **kwargs)
            def execute():
                try:
                    results.append(run(['/bin/sleep', '10'], workspace=workspace,
                                       limits=Limits(wall_seconds=.15)))
                except Exception as error:
                    errors.append(error)
            with patch('harness.boundary.subprocess.Popen', side_effect=safe_popen):
                worker = threading.Thread(target=execute)
                worker.start(); worker.join(timeout=2)
            self.assertFalse(worker.is_alive())
            self.assertEqual(errors, [])
            self.assertEqual(results[0].status, 'timeout')
            self.assertEqual(results[0].remaining_pids, ())


if __name__ == '__main__':
    unittest.main()
