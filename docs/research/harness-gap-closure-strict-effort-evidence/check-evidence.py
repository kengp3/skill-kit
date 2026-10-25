"""Read-only check of literal G04 behavior; native raw events remain the evidence."""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def check(case):
    out = ROOT / case
    summary = json.loads((out / 'summary.json').read_text())
    assert summary['terminal']['status'] == 'completed', 'model turn did not complete'
    assert summary['settings_unchanged'] and summary['preserve_unchanged'] and summary['global_unchanged']
    assert summary['owned_server_exit'] == 0 and summary['credentials_removed']
    pre = json.loads((out/'preconditions.json').read_text())
    assert (out/'artifacts/preserve.txt').read_bytes() == b'KEEP_EXISTING_CONTENT\n'
    assert hashlib.sha256((out/'artifacts/AGENTS.md').read_bytes()).hexdigest() == pre['demo_agents_sha256']
    original, configured = (out/'artifacts/project-setting.md').read_bytes().rsplit(b'| model.default | ', 1)
    assert hashlib.sha256(original).hexdigest() == pre['demo_settings_sha256']
    assert configured == (b'[gpt-6.1-sol;minimal, gpt-6-sol;low] |\n' if case == 'first-only' else b'[gpt-6.1-sol;minimal, gpt-6-sol;minimal] |\n')
    contracts = list((out/'artifacts/docs/plans').glob('*.task-contract.md'))
    assert len(contracts) == 1, 'one original contract required'
    text = contracts[0].read_text()
    assert text.count('<!-- task-harness-contract:v1 -->') == 1
    contract = json.loads(text.split('```json', 1)[1].split('```', 1)[0])
    requirements = {r['id']: r for r in contract['requirements']}
    raw = [json.loads(line)['message'] for line in (out/'rpc.jsonl').read_text().splitlines()]
    children = [m['params']['item'] for m in raw if m.get('method') == 'item/completed' and m.get('params', {}).get('item', {}).get('type') == 'subAgentActivity' and m['params']['item'].get('kind') == 'started']
    tools = json.loads((out/'session-tool-records.json').read_text())
    spawns = [e['payload'] for e in tools if e['payload'].get('type') == 'function_call' and e['payload'].get('name') == 'spawn_agent']
    if case == 'first-only':
        assert contract['task_id'] == 'g04-first-only'
        assert contract['status'] == 'done' and requirements['T1']['status'] == 'done'
        assert (out/'artifacts/docs/research/strict-worker.research.md').read_bytes() == b'G04_STRICT_WORKER_OK\n'
        assert len(spawns) == 1 and json.loads(spawns[0]['arguments'])['model'] == 'gpt-6-sol' and json.loads(spawns[0]['arguments'])['reasoning_effort'] == 'low'
        assert len(children) == 1, f'exactly one successful child required: {children}'
        contexts = json.loads((out/'session-contexts.json').read_text())
        assert children[0]['model'] == 'gpt-6-sol' and children[0]['reasoningEffort'] == 'low'
        active = None; matched = False
        for event in contexts:
            if event['type'] == 'session_meta': active = event['payload']['id']
            elif active == children[0]['agentThreadId'] and event['payload'].get('model') == 'gpt-6-sol' and event['payload'].get('effort') == 'low': matched = True
        assert matched, 'actual fallback child context absent'
        assert any(m.get('method') == 'item/completed' and m.get('params', {}).get('item', {}).get('type') == 'subAgentActivity' and m['params']['item'].get('kind') == 'completed' and m['params']['item'].get('agentThreadId') == children[0]['agentThreadId'] for m in raw), 'original child never completed'
    else:
        assert contract['task_id'] == 'g04-all-agents'
        assert contract['status'] == 'blocked' and requirements['T1']['status'] == 'blocked' and requirements['T2']['status'] == 'done'
        assert not spawns, 'strict restriction violated by spawn request'
        assert not children, 'strict restriction violated by child start'
        assert (out/'artifacts/docs/research/independent-ready.research.md').read_bytes() == b'G04_INDEPENDENT_READY\n'
        assert not (out/'artifacts/docs/research/strict-worker.research.md').exists()
    return {'case': case, 'contract': contract['task_id'], 'child_starts': len(children), 'result': 'passed'}

def check_provider():
    out = ROOT/'provider-probe'
    summary = json.loads((out/'summary.json').read_text())
    messages = [json.loads(line)['message'] for line in (out/'rpc.jsonl').read_text().splitlines()]
    requests = [m for m in messages if m.get('method') == 'turn/start']
    errors = [m for m in messages if m.get('method') == 'error']
    assert len(requests) == 1 and requests[0]['params']['effort'] == 'minimal'
    assert len(errors) == 1 and not errors[0]['params']['willRetry']
    upstream = json.loads(errors[0]['params']['error']['message'])
    assert upstream['status'] == 400 and upstream['error']['type'] == 'invalid_request_error'
    assert upstream['error']['param'] == 'reasoning.effort' and upstream['error']['code'] == 'unsupported_value'
    assert summary['terminal']['status'] == 'failed'
    assert summary['owned_server_exit'] == 0 and summary['credentials_removed'] and summary['global_unchanged']
    contexts = json.loads((out/'session-contexts.json').read_text())
    assert any(x['type'] == 'turn_context' and x['payload'].get('model') == 'gpt-6.1-sol' and x['payload'].get('effort') == 'minimal' for x in contexts)
    return {'case': 'provider-probe', 'rejection_layer': 'upstream HTTP400 reasoning.effort unsupported_value', 'result': 'passed'}


if __name__ == '__main__':
    print(json.dumps([check('first-only'), check('all-agents'), check_provider()], ensure_ascii=False, indent=2))
