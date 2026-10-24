"""Local development subprocesses; no model sessions or Desktop state changes."""
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import tempfile
import time


class BoundaryUnavailable(RuntimeError):
    """The requested restrictions could not be established."""


@dataclass(frozen=True)
class Limits:
    wall_seconds: float = 10
    cpu_seconds: float = 5
    memory_mb: int = 512
    max_processes: int = 8


@dataclass(frozen=True)
class RunResult:
    returncode: int
    status: str
    stdout: str
    stderr: str
    elapsed_seconds: float
    remaining_pids: tuple


_ACTIVE = threading.Lock()


def _processes(group):
    result = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid=,rss=,time=,stat='],
                            capture_output=True, text=True, check=True)
    processes = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 5 or int(fields[1]) != group or fields[4].startswith('Z'):
            continue
        minutes, seconds = fields[3].split(':')
        processes.append((int(fields[0]), int(fields[2]), int(minutes) * 60 + float(seconds)))
    return processes


def run(argv, *, workspace, limits=Limits(), cancel=None, env=None):
    """Run one owned process group with filesystem/network and sampled resource guards.

    CPU has an inherited kernel limit and a group watchdog; each file is capped at
    16 MiB by RLIMIT_FSIZE. RSS and process count
    are sampled every 20ms; their thresholds can overshoot between samples.
    Descendants must remain in the owned process group; this is not a hostile-code
    container. A detached child is outside the supported execution contract.
    """
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise BoundaryUnavailable('macOS sandbox-exec is required')
    if (not isinstance(argv, (list, tuple)) or not argv
            or any(not isinstance(value, str) or not value for value in argv)):
        raise ValueError('argv must be a nonempty argument list')
    if Path(argv[0]).name in ('codex', 'codex-cli') or 'app-server' in argv:
        raise ValueError('model/native server execution is outside this boundary')
    if any(not math.isfinite(value) or value <= 0 for value in
           (limits.wall_seconds, limits.cpu_seconds, limits.memory_mb, limits.max_processes)):
        raise ValueError('all limits must be positive and finite')
    original = Path(workspace).absolute()
    root = original.resolve(strict=True)
    if (root != original or not root.is_dir()
            or not any(parent in root.parents for parent in
                       (Path(tempfile.gettempdir()).resolve(), Path('/private/tmp')))):
        raise ValueError('workspace must be a real disposable directory inside system temp')
    if any(root.iterdir()):
        raise ValueError('workspace must be empty; reconcile an existing attempt first')
    # These are the only persistent paths exposed to the child as writable state.
    for name in ('home', 'tmp', 'cache', 'config', 'data'):
        target = root / name
        if target.is_symlink():
            raise ValueError('workspace state directory cannot be a symlink')
        target.mkdir(exist_ok=True)
    child_env = {'PATH': os.defpath, 'LANG': 'en_US.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1',
                 'HOME': str(root / 'home'), 'TMPDIR': str(root / 'tmp'),
                 'TMP': str(root / 'tmp'), 'TEMP': str(root / 'tmp'),
                 'XDG_CACHE_HOME': str(root / 'cache'), 'XDG_CONFIG_HOME': str(root / 'config'),
                 'XDG_DATA_HOME': str(root / 'data')}
    allowed_env = {'PATH', 'JAVA_HOME', 'JAVA_TOOL_OPTIONS', 'MAVEN_OPTS'}
    if env:
        if set(env) - allowed_env or any(not isinstance(v, str) for v in env.values()):
            raise ValueError('only explicit toolchain environment is accepted')
        child_env.update(env)
    # shortcut: detached descendants are unsupported; use stronger containment before testing them.
    profile = ('(version 1) (allow default) (deny network*) (deny file-write*) '
               '(allow file-write* (subpath ' + json.dumps(str(root)) + ')) '
               '(deny process-exec (regex #".*/codex(-cli)?$"))')

    def set_limits():
        import resource
        ceiling = max(1, math.ceil(limits.cpu_seconds))
        resource.setrlimit(resource.RLIMIT_CPU, (ceiling, ceiling))
        resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))
        os.nice(10)

    if not _ACTIVE.acquire(blocking=False):
        raise BoundaryUnavailable('another owned development job is active')
    started = time.monotonic()
    process = None
    status = 'completed'
    try:
        with (root / '.stdout').open('x+') as output, (root / '.stderr').open('x+') as errors:
            process = subprocess.Popen(['/usr/bin/sandbox-exec', '-p', profile, *argv],
                                       cwd=root, env=child_env, stdin=subprocess.DEVNULL,
                                       stdout=output, stderr=errors, start_new_session=True,
                                       preexec_fn=set_limits)
            while process.poll() is None:
                members = _processes(process.pid)
                if cancel is not None and cancel.is_set():
                    status = 'cancelled'
                elif time.monotonic() - started >= limits.wall_seconds:
                    status = 'timeout'
                elif sum(p[2] for p in members) >= limits.cpu_seconds:
                    status = 'cpu_limit'
                elif sum(p[1] for p in members) > limits.memory_mb * 1024:
                    status = 'memory_limit'
                elif len(members) > limits.max_processes:
                    status = 'process_limit'
                if status != 'completed':
                    break
                time.sleep(.02)
            # Cleanup runs even if the parent exits while descendants retain outputs.
            if _processes(process.pid):
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                until = time.monotonic() + .3
                while _processes(process.pid) and time.monotonic() < until:
                    process.poll()
                    time.sleep(.02)
                if _processes(process.pid):
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            process.wait(timeout=2)
            remaining = tuple(p[0] for p in _processes(process.pid))
            if remaining:
                raise BoundaryUnavailable('owned processes remain after cleanup')
            output.seek(0); errors.seek(0)
            stdout, stderr = output.read(), errors.read()
            if 'sandbox_apply:' in stderr:
                raise BoundaryUnavailable(stderr.strip())
            if status == 'completed' and process.returncode == -signal.SIGXCPU:
                status = 'cpu_limit'
            return RunResult(process.returncode, status, stdout, stderr,
                             time.monotonic() - started, remaining)
    finally:
        if process is not None:
            try:
                if _processes(process.pid):
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            except (ProcessLookupError, subprocess.SubprocessError):
                pass
            finally:
                try:
                    process.wait(timeout=2)
                finally:
                    _ACTIVE.release()
        else:
            _ACTIVE.release()
