"""Exercise each driver's offline export → JSON readback boundary; never launch a model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
DRIVERS = [ROOT/'harness-gap-closure-demo-setup-evidence/native-demo.py', ROOT/'harness-gap-closure-strict-effort-evidence/native-strict.py']
SAMPLE = [
    {'timestamp': '2026-10-26T00:00:00Z', 'type': 'session_meta', 'payload': {
        'id': 'child-thread', 'parent_thread_id': 'parent-thread', 'cwd': '/case',
        'source': {'subagent': {'thread_spawn': {'parent_thread_id': 'parent-thread', 'depth': 1, 'agent_path': '/root/worker', 'creator_account_id': 'SYNTHETIC_ACCOUNT'}, 'unknown': 'SYNTHETIC_SECRET'}, 'api_key': 'SYNTHETIC_KEY'},
        'creator_account_id': 'SYNTHETIC_ACCOUNT', 'creator_user_id': 'SYNTHETIC_USER', 'future_secret': 'SYNTHETIC_SECRET'}},
    {'timestamp': '2026-10-26T00:00:01Z', 'type': 'turn_context', 'payload': {
        'turn_id': 'turn', 'model': 'gpt-6-sol', 'effort': 'low', 'cwd': '/case',
        'future_secret': 'SYNTHETIC_SECRET', 'tokens': {'access_token': 'SYNTHETIC_TOKEN'}}},
    {'timestamp': '2026-10-26T00:00:02Z', 'type': 'response_item', 'payload': {'secret': 'SYNTHETIC_SECRET'}},
]
EXPECTED = [
    {'timestamp': '2026-10-26T00:00:00Z', 'type': 'session_meta', 'payload': {
        'id': 'child-thread', 'parent_thread_id': 'parent-thread', 'cwd': '/case',
        'source': {'subagent': {'thread_spawn': {'parent_thread_id': 'parent-thread', 'depth': 1, 'agent_path': '/root/worker'}}}}},
    {'timestamp': '2026-10-26T00:00:01Z', 'type': 'turn_context', 'payload': {
        'turn_id': 'turn', 'model': 'gpt-6-sol', 'effort': 'low', 'cwd': '/case'}},
]

with tempfile.TemporaryDirectory(prefix='g01-g04-export-check-') as tmp:
    source = Path(tmp)/'input.json'; source.write_text(json.dumps(SAMPLE))
    for driver in DRIVERS:
        target = Path(tmp)/(driver.stem+'.json')
        result = subprocess.run([sys.executable, str(driver), '--export-contexts', str(source), str(target)], capture_output=True, text=True)
        assert result.returncode == 0, f'{driver.name}: offline export unavailable: {result.stderr}'
        assert json.loads(target.read_text()) == EXPECTED, f'{driver.name}: unsafe fields or evidence metadata mismatch'
        print(f'{driver.name}: passed offline export/readback; parent-child and model/effort retained; unknown/account fields absent')
