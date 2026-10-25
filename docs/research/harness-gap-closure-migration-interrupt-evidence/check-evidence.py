"""Read-only maintainer checks of recorded public native events and artifacts."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'formal'
s = json.loads((OUT/'summary.json').read_text())
raws = {label: [json.loads(line) for line in (OUT/(label+'-rpc.jsonl')).read_text().splitlines()] for label in ('original', 'resume')}
item_id = s['command_started_event']['params']['item']['id']
started = [(n, r) for n, r in enumerate(raws['original'], 1) if r['message'].get('method') == 'item/started' and r['message'].get('params', {}).get('item', {}).get('id') == item_id]
assert len(started) == 1
signal_at = s['signal']['at']; assert started[0][1]['at'] < signal_at
completed = [(n, r) for n, r in enumerate(raws['original'], 1) if r['message'].get('method') == 'item/completed' and r['message'].get('params', {}).get('item', {}).get('id') == item_id]
assert len(completed) == 1 and completed[0][1]['message']['params']['item']['exitCode'] == 143
assert not [r for r in raws['original'] if r['at'] > signal_at and r['message'].get('method') == 'item/started' and r['message'].get('params', {}).get('item', {}).get('type') in ('commandExecution', 'fileChange')]
authorization = [(n, r) for n, r in enumerate(raws['resume'], 1) if r['direction'] == 'client' and r['message'].get('method') == 'turn/start']
assert len(authorization) == 1 and authorization[0][1]['at'] > signal_at
assert s['original_server']['absent'] and not s['original_descendants_after']
commands = [(n, r['message']['params']['item']) for n, r in enumerate(raws['resume'], 1) if r['message'].get('method') == 'item/completed' and r['message'].get('params', {}).get('item', {}).get('type') == 'commandExecution']
deleted = [(n, i) for n, i in commands if 'rm harness-project.json' in i['command']]
assert len(deleted) == 1 and deleted[0][1]['exitCode'] == 0
assert '三個門檻（本次從磁碟驗證）' in (deleted[0][1].get('aggregatedOutput') or ''), 'three gates must have been saved and read before deletion'
report = (OUT/'final/docs/research/g02-migration.research.md').read_text()
assert all(value in report for value in ('成功寫入且無遺漏：通過', '格式及內容有效：通過', '目標版本正常讀回：通過', 'G02-migration'))
expected = {'ledger.txt': b'EXISTING_ONCE\n', 'preserve.txt': b'KEEP_G02_EXISTING_BYTES\n', 'docs/plans/harness/legacy.md': b'# Historical completed contract\nKEEP_CONTRACT_BYTES\n', 'docs/research/receipts/old.jsonl': b'{"kind":"legacy","done":true}\n'}
for name, value in expected.items():
    assert all((OUT/phase/name).read_bytes() == value for phase in ('initial', 'at-window', 'after-signal', 'final')), name
secrets = []
def values(value):
    if isinstance(value, dict):
        for item in value.values(): values(item)
    elif isinstance(value, list):
        for item in value: values(item)
    elif isinstance(value, str) and len(value) > 24: secrets.append(value.encode())
values(json.loads(Path('/Users/kengp3/.codex/auth.json').read_text()))
findings = [str(path.relative_to(ROOT)) for path in ROOT.rglob('*') if path.is_file() and any(value in path.read_bytes() for value in secrets)]
assert not findings, 'credential-related values must not appear in evidence: '+repr(findings)
verification = {'verdict': 'passed', 'raw_lines': {'started': started[0][0], 'interrupted_command_exit143': completed[0][0], 'resume_new_authorization': authorization[0][0], 'three_gates_readback_then_only_delete': deleted[0][0]}, 'no_post_signal_tool_starts': True, 'same_task_identity': 'G02-migration', 'known_literal_products_preserved': True, 'credential_scan': {'credential_values_tested': len(secrets), 'matched_files': findings}, 'evidence_sha256': {str(path.relative_to(OUT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in OUT.rglob('*') if path.is_file() and path.name != 'verification.json'}}
(OUT/'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({key: verification[key] for key in ('verdict', 'raw_lines', 'no_post_signal_tool_starts', 'credential_scan')}))
