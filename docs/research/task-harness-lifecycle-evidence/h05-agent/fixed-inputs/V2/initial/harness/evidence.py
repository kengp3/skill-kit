"""Development-only summaries of saved native RPC; never executes their contents."""
import hashlib
import json
from pathlib import Path

from .control import TrialControl


def _messages(paths, sources, issues):
    for path in paths:
        path = Path(path)
        try:
            content = path.read_bytes()
            lines = content.decode('utf-8').splitlines()
        except (OSError, UnicodeError) as error:
            issues.append(f'Unreadable source {path}: {error}')
            continue
        sources.append({'path': str(path), 'sha256': hashlib.sha256(content).hexdigest()})
        for line, raw in enumerate(lines, 1):
            ref = {'source': str(path), 'line': line}
            try:
                record = json.loads(raw)
            except ValueError:
                issues.append(f'Invalid JSON record: {ref}')
                continue
            if not isinstance(record, dict):
                issues.append(f'Invalid RPC record: {ref}')
                continue
            if 'response' not in record:
                continue
            message = record['response']
            if not isinstance(message, dict):
                issues.append(f'Invalid response: {ref}')
                continue
            if message.get('method') in ('turn/completed', 'item/completed', 'item/started'):
                yield message, ref


def summarize_events(paths, *, thread_id, turn_ids):
    """Count root items once per (thread, turn, item), retaining raw references."""
    if (not isinstance(thread_id, str) or not thread_id
            or not isinstance(turn_ids, (list, tuple)) or not turn_ids
            or any(not isinstance(turn, str) or not turn for turn in turn_ids)
            or len(set(turn_ids)) != len(turn_ids)):
        raise ValueError('Explicit thread ID and distinct ordered turn IDs required')
    items = {}
    item_values = {}
    pending = {}
    issues = []
    turns = {turn_id: {'id': turn_id, 'status': 'unknown', 'evidence': []}
             for turn_id in turn_ids}
    sources = []
    for message, ref in _messages(paths, sources, issues):
        params = message.get('params')
        if (not isinstance(params, dict) or not isinstance(params.get('threadId'), str)
                or not params['threadId']):
            issues.append(f'Missing event identity: {ref}')
            continue
        if params['threadId'] != thread_id:
            continue
        if message['method'] == 'turn/completed':
            turn = params.get('turn')
            if not isinstance(turn, dict) or not isinstance(turn.get('id'), str):
                issues.append(f'Invalid turn identity: {ref}')
                continue
            if turn['id'] not in turns:
                continue
            target = turns[turn['id']]
            status = turn.get('status')
            if (status not in ('completed', 'failed', 'interrupted')
                    or target['evidence'] and target['status'] != status):
                status = 'unknown'
                issues.append(f'Conflicting or invalid terminal evidence: {ref}')
            target['status'] = status
            if ref not in target['evidence']:
                target['evidence'].append(ref)
        else:
            turn_id = params.get('turnId')
            if not isinstance(turn_id, str):
                issues.append(f'Missing item turn identity: {ref}')
                continue
            if turn_id not in turns:
                continue
            value = params.get('item')
            if (not isinstance(value, dict)
                    or not isinstance(value.get('id'), str) or not value['id']
                    or not isinstance(value.get('type'), str) or not value['type']):
                issues.append(f'Invalid item identity or type: {ref}')
                continue
            key = (thread_id, turn_id, value['id'])
            if message['method'] == 'item/started':
                if value['type'] == 'commandExecution':
                    pending[key] = {'thread_id': thread_id, 'turn_id': turn_id,
                                    'item_id': value['id'], 'type': value['type'],
                                    'status': 'unknown', 'exit_code': None, 'evidence': [ref]}
                continue
            if key not in items:
                item_values[key] = value
                items[key] = {'thread_id': thread_id, 'turn_id': turn_id,
                              'item_id': value['id'], 'type': value['type'],
                              'status': value.get('status'),
                              'exit_code': value.get('exitCode'), 'evidence': []}
            elif item_values[key] != value:
                items[key]['status'] = 'unknown'
                items[key]['exit_code'] = None
                issues.append(f'Conflicting item evidence: {ref}')
            if ref not in items[key]['evidence']:
                items[key]['evidence'].append(ref)
    items.update({key: value for key, value in pending.items() if key not in items})
    commands = [item for item in items.values() if item['type'] == 'commandExecution']
    known = [item for item in commands if item['status'] in ('completed', 'failed')
             and type(item['exit_code']) is int]
    for turn in turns.values():
        if not turn['evidence']:
            issues.append(f'Missing terminal evidence for turn {turn["id"]}')
    if len(known) != len(commands):
        issues.append('Some command outcomes are missing or conflicting.')
    return {'sources': sources, 'turns': list(turns.values()),
            'coverage': 'partial' if issues else 'complete',
            'final_turn_status': turns[turn_ids[-1]]['status'],
            'items': list(items.values()),
            'metrics': {'commands_completed': len(known),
                        'commands_nonzero': sum(item['exit_code'] != 0 for item in known),
                        'command_outcomes_unknown': len(commands) - len(known),
                        'help_requests': None, 'retries': None, 'repairs': None},
            'unverified': issues + [
                'Native command counts do not identify help, retries or repairs.']}


def replay_smoke(archive):
    """Reinterpret the first A/B/C archive; original evidence remains read-only."""
    archive = Path(archive)
    template = Path(__file__).resolve().parents[1] / 'fixtures/harness-run.template.json'
    results = []
    for group in 'ABC':
        result = json.loads(template.read_text())

        def read(relative):
            path = archive / relative
            content = path.read_bytes()
            result['sources'].append({'path': str(path),
                                      'sha256': hashlib.sha256(content).hexdigest()})
            return json.loads(content)

        config = read('frozen-trial-config.json')
        grader_config = read('frozen-trial-grader-v2.json')
        initial = read(f'cli-smoke-{group}/state.json')
        outcome = read('flow-smoke-outcomes.json')['groups'][group]
        state = initial
        turns = [initial['turn_id']]
        paths = [archive / f'cli-smoke-{group}/rpc.jsonl']
        if group == 'C':
            state = read('cli-smoke-C/reconciled-state.json')
            turns.append(state['turn_id'])
            paths.append(archive / 'cli-smoke-C-continuation-1/rpc.jsonl')
            readback = read('cli-smoke-C/interrupted-root-readback.json')
            control = TrialControl(started_at=0, wall_seconds=config['limit_seconds'])
            control.bind(initial['thread_id'], initial['turn_id'])
            reconciled = control.reconcile_readback(readback)
            result['observations']['initial_turn_readback_status'] = (
                control.outcome if reconciled else 'unknown')
        events = summarize_events(paths, thread_id=initial['thread_id'], turn_ids=turns)
        result['sources'].extend(events['sources'])
        grade_path = f'cli-grade-{group}-v2/result.json'
        diagnostic_path = f'cli-diagnostic-{group}-factory-close/result.json'
        grade = read(grade_path)
        diagnostic = read(diagnostic_path)
        result.update(run_id=f'first-smoke-{group}-offline-v2', group=group,
                      task_source=str(archive / 'frozen-input-common/TASK.md'),
                      acceptance_version=grade['grader_version'],
                      host=config['host'], model=state['model'],
                      configuration_evidence=str(archive / 'frozen-trial-config.json'),
                      native_identity={'thread_id': initial['thread_id'], 'turn_ids': turns},
                      event_summary=events, wall_clock_minutes=state['elapsed_seconds'] / 60)
        result['limits'].update(wall_clock_minutes=config['limit_seconds'] / 60,
                                trial_attempts=config['attempts_per_group'],
                                feedback_policy=grader_config['external_feedback_policy'])
        result['observations'].update(
            trial_attempts=outcome['trial_contexts'],
            whole_trial_restarts=outcome['whole_trial_restarts'],
            controller_recoveries=outcome['controller_recoveries'],
            frozen_external_grade={'passed': grade['product_passed'],
                                   'evidence': str(archive / grade_path)},
            later_factory_diagnostic={'passed': diagnostic['product_passed'],
                                      'evidence': str(archive / diagnostic_path)})
        status = events['final_turn_status']
        if status == 'completed' and (grade['product_passed'] is not True
                                      or diagnostic['product_passed'] is not True):
            status = 'completed_with_known_defect'
        result['delivery'].update(status=status, evidence=[str(archive / grade_path),
                                 str(archive / diagnostic_path)], unverified=[
            'Desktop behavior, fair comparison and human benefit are not qualified.',
            'Human takeover, interruptions and help/retry/repair counts are unavailable.',
            *events['unverified']])
        result['interpretation'] = [
            'Root-thread commands only; child activity is excluded.',
            'A continuation turn is not a new trial; recovery is not a human rescue.',
            'Frozen grades and later diagnostics retain their separate scopes.',
            'Wall time is not human active time; no savings or ranking is inferred.']
        results.append(result)
    return results
