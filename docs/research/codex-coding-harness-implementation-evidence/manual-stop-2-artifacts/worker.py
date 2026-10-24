import json, os, signal, time
from pathlib import Path
run = Path(__file__).resolve().parent
assert Path.cwd().resolve() == run.parents[1]
stop = [None]
def on_signal(sig, frame):
    stop[0] = sig
signal.signal(signal.SIGINT, on_signal)
signal.signal(signal.SIGTERM, on_signal)
deadline = time.monotonic() + 120
parent = os.getpid()
child = os.fork()
role = "child" if child == 0 else "parent"
def record(event):
    with (run / (role + "-heartbeat.jsonl")).open("a") as f:
        f.write(json.dumps({"event": event, "pid": os.getpid(), "signal": stop[0], "monotonic": time.monotonic()}) + "\n")
if child:
    with (run / "pids.json").open("x") as f:
        json.dump({"parent_pid": parent, "child_pid": child, "limit_seconds": 120, "deadline_monotonic": deadline}, f)
    print("MANUAL_STOP_READY " + json.dumps({"parent_pid": parent, "child_pid": child}), flush=True)
record("started")
while stop[0] is None and time.monotonic() < deadline:
    record("heartbeat")
    time.sleep(0.25)
record("stopped")
if child == 0:
    os._exit(0)
try:
    os.kill(child, signal.SIGTERM)
except ProcessLookupError:
    pass
_, status = os.waitpid(child, 0)
result = {"parent_stop_signal": stop[0], "deadline_expired": time.monotonic() >= deadline, "child_exit_code": os.waitstatus_to_exitcode(status)}
with (run / "final.json").open("x") as f:
    json.dump(result, f)
print("MANUAL_STOP_FINAL " + json.dumps(result), flush=True)
