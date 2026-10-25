"""User-contract regression checks; run from the case root with python3 -B."""
import hashlib
import inspect
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.evidence import summarize_events


def main():
    baseline = json.loads(Path('verification/t1-baseline.json').read_text())
    for name in ('consistent.jsonl', 'conflict.jsonl', 'harness/control.py'):
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == baseline['sha256'][name]
    assert str(inspect.signature(summarize_events)) == '(paths, *, thread_id, turn_ids)'
    reversed_path = Path('verification/conflict-reversed.jsonl')
    lines = Path('conflict.jsonl').read_text().splitlines()
    reversed_path.write_text('\n'.join([lines[1], lines[0], *lines[2:]]) + '\n')
    results = {}
    for name, path, expected in (
        ('normal', 'consistent.jsonl', ('complete', 1, 0)),
        ('conflict', 'conflict.jsonl', ('partial', 0, 1)),
        ('reversed', str(reversed_path), ('partial', 0, 1)),
    ):
        result = summarize_events([path], thread_id='root', turn_ids=['first'])
        metrics = result['metrics']
        assert (result['coverage'], metrics['commands_completed'],
                metrics['command_outcomes_unknown']) == expected
        assert result['final_turn_status'] == 'completed'
        if name != 'normal':
            assert any('Conflicting started/completed item types' in issue
                       for issue in result['unverified'])
            item, = result['items']
            assert item['type'] == 'commandExecution'
            assert item['status'] == 'unknown' and item['exit_code'] is None
            assert {ref['line'] for ref in item['evidence']} == {1, 2}
        results[name] = result
    assert results['conflict']['metrics'] == results['reversed']['metrics']
    report = {
        'passed': True,
        'basis': 'User behavior contract; direct public API assertions',
        'interrupt_check': 'unverified: sole 30-second window exited naturally with code 0',
        'sha256': {name: hashlib.sha256(Path(name).read_bytes()).hexdigest()
                   for name in ('harness/evidence.py', 'harness/control.py',
                                'consistent.jsonl', 'conflict.jsonl', __file__)},
        'results': results,
    }
    output = Path('verification/integration.json')
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert json.loads(output.read_text())['passed'] is True
    print('PASS: normal, conflict, reversed; terminal statuses, references, API and fixture integrity')


if __name__ == '__main__':
    main()
