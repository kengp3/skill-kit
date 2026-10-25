"""Read-only assertions over archived native lifecycle evidence (maintainer-only)."""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
checks = []

def check(name, condition):
    assert condition, name
    checks.append(name)

def load(case):
    root = BASE / case
    summary = json.loads((root / 'summary.json').read_text())
    rows = json.loads((root / 'session-contexts.json').read_text())
    records = [json.loads(line) for line in (root / 'rpc.jsonl').read_text().splitlines()]
    meta = {row['file']: row for row in rows if row['type'] == 'session_meta'}
    workers = {}
    for file, row in meta.items():
        source = row['source']
        spawn = source.get('subagent', {}).get('thread_spawn') if isinstance(source, dict) else None
        if spawn:
            workers[spawn['agent_path']] = {
                'id': row['id'], 'parent': spawn['parent_thread_id'],
                'contexts': [(r['model'], r['effort']) for r in rows if r['type'] == 'turn_context' and r['file'] == file],
            }
    activity = []
    for line, record in enumerate(records, 1):
        message = record['message']; params = message.get('params', {}); item = params.get('item', {})
        if message.get('method') == 'item/completed' and item.get('type') == 'subAgentActivity':
            activity.append((line, item))
    check(case + ': terminal root turns', all(t['turn']['status'] == 'completed' for t in summary['turns']))
    check(case + ': no driver error', 'error' not in summary)
    check(case + ': server exited', summary['owned_server_exit'] == 0)
    for field in ['settings_unchanged', 'preserve_unchanged', 'global_unchanged']:
        check(case + ': ' + field, summary[field] is True)
    temp_root = Path(summary['thread_start']['cwd']).parent
    check(case + ': temporary state and credential copy deleted', not temp_root.exists())
    for artifact in root.glob('artifacts*'):
        check(case + ': preserve bytes ' + artifact.name, (artifact / 'preserve.txt').read_bytes() == b'KEEP_EXISTING_CONTENT\n')
    return root, summary, rows, records, workers, activity

def contract(path):
    return json.loads(re.search(r'```json\n(.*?)\n```', path.read_text(), re.S)[1])

root, summary, rows, records, workers, activity = load('override')
check('override: same conversation restored, new conversation distinct', summary['turns'][0]['thread'] == summary['turns'][1]['thread'] != summary['turns'][2]['thread'])
check('override: exactly three native workers', set(workers) == {'/root/t1_readonly_check', '/root/t2_readonly_check', '/root/preserve_check'})
for name in ['/root/t1_readonly_check', '/root/t2_readonly_check']:
    check('override: actual session ' + name, workers[name]['contexts'] == [('gpt-6-sol', 'low')])
    check('override: parent ' + name, workers[name]['parent'] == summary['turns'][0]['thread'])
check('override: new task actual project default', workers['/root/preserve_check']['contexts'] == [('gpt-6.1-sol', 'low')])
check('override: new task parent', workers['/root/preserve_check']['parent'] == summary['turns'][2]['thread'])
a = contract(root / 'artifacts-phase1/docs/plans/scoped-model.task-contract.md')
b = contract(root / 'artifacts-phase2/docs/plans/scoped-model.task-contract.md')
c = contract(root / 'artifacts-phase3/docs/plans/new-model-task.task-contract.md')
check('override: contract override survives actual later turn', a['model_overrides'] == b['model_overrides'] and 'gpt-6-sol;low' in str(b['model_overrides']))
check('override: new contract does not inherit override', not c.get('model_overrides'))
check('override: phase1 T2 waiting and phase2 done', a['requirements'][1]['status'] == 'pending' and b['status'] == 'done')
settings = [(root / f'artifacts-phase{i}/project-setting.md').read_bytes() for i in (1, 2, 3)]
check('override: saved settings byte-identical all three phases', len(set(settings)) == 1 and b'gpt-6.1-sol;low' in settings[0])
for name in ['t1_readonly_check', 't2_readonly_check', 'preserve_check']:
    check('override: one start and one completion ' + name, [i['kind'] for _, i in activity if i.get('agentPath') == '/root/' + name] == ['started', 'completed'])

root, summary, rows, records, workers, activity = load('switch')
check('switch: same actual root conversation', summary['turns'][0]['thread'] == summary['turns'][1]['thread'])
starts = [(n, r['message']['params']) for n, r in enumerate(records, 1) if r['direction'] == 'client' and r['message'].get('method') == 'turn/start']
check('switch: actual host control on second turn', len(starts) == 2 and starts[1][1]['model'] == 'gpt-6-sol' and starts[1][1]['effort'] == 'medium')
root_contexts = [(r['model'], r['effort']) for r in rows if r['type'] == 'turn_context' and summary['turns'][0]['thread'] in r['file']]
check('switch: host contexts confirm main model and effort changed', root_contexts == [('gpt-6.1-sol', 'low'), ('gpt-6-sol', 'medium')])
check('switch: exactly old and new workers', set(workers) == {'/root/old_worker', '/root/new_worker'})
check('switch: old worker retains actual original model and effort', workers['/root/old_worker']['contexts'] == [('gpt-6.1-sol', 'low')])
check('switch: new worker actually inherits latest model and effort', workers['/root/new_worker']['contexts'] == [('gpt-6-sol', 'medium')])
old = [(n, i) for n, i in activity if i.get('agentPath') == '/root/old_worker']
check('switch: old existing session spans model switch without restart', [i['kind'] for _, i in old] == ['started', 'completed'] and old[0][0] < starts[1][0] < old[1][0] and all(i['agentThreadId'] == workers['/root/old_worker']['id'] for _, i in old))
a = contract(root / 'artifacts-phase1/docs/plans/manual-switch.task-contract.md')
b = contract(root / 'artifacts-phase2/docs/plans/manual-switch.task-contract.md')
check('switch: original task handle retained', a['model_runs'][0]['handle'] == b['model_runs'][0]['handle'] == '/root/old_worker')
check('switch: old in progress before gate, both done after gate', a['requirements'][0]['status'] == 'in_progress' and all(r['status'] == 'done' for r in b['requirements']))
check('switch: no gate before actual second turn', not (root / 'artifacts-phase1/gate-old.txt').exists() and (root / 'artifacts-phase2/gate-old.txt').exists())
check('switch: project settings byte-identical', (root / 'artifacts-phase1/project-setting.md').read_bytes() == (root / 'artifacts-phase2/project-setting.md').read_bytes())

root, summary, rows, records, workers, activity = load('exhausted')
check('exhausted: exactly two attempts with distinct candidates', set(workers) == {'/root/t1_primary', '/root/t1_default'} and len([i for _, i in activity if i['kind'] == 'started']) == 2)
failures = [r['message']['params'] for r in records if r['message'].get('method') == 'turn/completed' and r['message']['params']['turn']['status'] == 'failed']
check('exhausted: two real model_not_found terminal failures', len(failures) == 2 and all('model_not_found' in f['turn']['error']['message'] for f in failures) and {f['threadId'] for f in failures} == {w['id'] for w in workers.values()})
d = contract(root / 'artifacts/docs/plans/exhausted.task-contract.md')
check('exhausted: only affected requirement blocked', {r['id']: r['status'] for r in d['requirements']} == {'T1': 'blocked', 'T2': 'done'})
check('exhausted: unrelated actual output exact bytes', (root / 'artifacts/docs/research/independent-ready.research.md').read_bytes() == b'READY_WORK_DONE\n')
check('exhausted: asks decision after exhaustion', '?' in summary['turns'][0]['turn']['items'][0]['text'] or '？' in summary['turns'][0]['turn']['items'][0]['text'])

# Compare actual secret values without writing or printing them.
def strings(value):
    if isinstance(value, dict):
        for v in value.values(): yield from strings(v)
    elif isinstance(value, list):
        for v in value: yield from strings(v)
    elif isinstance(value, str) and len(value) >= 20: yield value.encode()
secrets = list(strings(json.loads(Path('/Users/kengp3/.codex/auth.json').read_text())))
files = [p for p in BASE.rglob('*') if p.is_file()]
check('archive: no credential file', not any(p.name == 'auth.json' for p in files))
check('archive: no actual auth secret values', not any(secret in p.read_bytes() for p in files for secret in secrets))
result = {'status': 'PASS', 'count': len(checks), 'checks': checks}
print(json.dumps(result, ensure_ascii=False, indent=2))
