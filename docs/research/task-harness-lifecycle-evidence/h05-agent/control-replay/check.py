"""Offline recognition check; never imports or runs the agent driver."""
import ast
import copy
import json
import re
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent
tree = ast.parse((ROOT / 'driver.py.txt').read_text())
function = next(node for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == 'is_interrupt_window')
namespace = {'shlex': shlex}
exec(compile(ast.Module(body=[function], type_ignores=[]), '<predicate>', 'exec'), namespace)
matches = namespace['is_interrupt_window']
state = json.loads((ROOT.parent / 'V3/state.json').read_text())
thread, turn = state['thread_id'], state['turn_id']
records = [json.loads(line) for line in (ROOT.parent / 'V3/rpc.jsonl').read_text().splitlines()]
events = [record['event'] for record in records if 'event' in record]
hits = [(index, event) for index, event in enumerate(events) if matches(event, thread, turn)]
assert len(hits) == 1
index, started = hits[0]
item = started['params']['item']['id']
completed = next(i for i, event in enumerate(events)
                 if event['method'] == 'item/completed' and event['params']['item']['id'] == item)
assert index < completed
contracts = []
for event in events[:index]:
    raw = event.get('params', {}).get('item', {}).get('aggregatedOutput') or ''
    for block in re.findall(r'```json\s*(.*?)```', raw, re.S):
        contract = json.loads(block)
        if contract.get('owner_session_id') == thread:
            contracts.append(contract)
assert contracts[-1]['authorization']['user_turn_id'] == turn
assert contracts[-1]['status'] == 'in_progress'
assert {r['id']: r['status'] for r in contracts[-1]['requirements']} == {
    'T1': 'done', 'T2': 'pending', 'T3': 'pending'}
for field in ('threadId', 'turnId'):
    event = copy.deepcopy(started)
    event['params'][field] = 'other'
    assert not matches(event, thread, turn)
for field, value in [('status', 'completed'), ('type', 'agentMessage'),
                     ('command', 'echo H05_V3_INTERRUPT_WINDOW'),
                     ('command', "'unterminated")]:
    event = copy.deepcopy(started)
    event['params']['item'][field] = value
    assert not matches(event, thread, turn)
assert not matches(events[completed], thread, turn)
print('PASS: one recorded start, prior saved contract, seven negative cases; no agent execution')
