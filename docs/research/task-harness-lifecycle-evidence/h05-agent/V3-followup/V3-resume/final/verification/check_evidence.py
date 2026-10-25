"""User-contract regression checks; run from the case root with python3 -B."""
import hashlib
import itertools
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import evidence


def check(path, expected, order=None):
    original = evidence._messages

    def reordered(paths, sources, issues):
        messages = list(original(paths, sources, issues))
        return iter(messages if order is None else [messages[i] for i in order])

    with patch.object(evidence, '_messages', reordered):
        result = evidence.summarize_events([path], thread_id='root', turn_ids=['first'])
    actual = (result['coverage'], result['metrics']['commands_completed'],
              result['metrics']['command_outcomes_unknown'], result['final_turn_status'])
    assert actual == expected, (path, order, actual)
    assert result['turns'][0]['evidence'] == [{'source': path, 'line': 3}]
    if expected[0] == 'partial':
        item, = result['items']
        assert item['type'] == 'commandExecution'
        assert item['status'] == 'unknown' and item['exit_code'] is None
        assert {ref['line'] for ref in item['evidence']} == {1, 2}
        assert any('Conflicting item types' in issue for issue in result['unverified'])
    return result


def main():
    normal = ('complete', 1, 0, 'completed')
    conflict = ('partial', 0, 1, 'completed')
    cases = {
        'normal': check('consistent.jsonl', normal),
        'conflict': check('conflict.jsonl', conflict),
        'reversed_item_conflict': check('conflict.jsonl', conflict, (1, 0, 2)),
    }
    # Exercise every ordering, including a terminal turn preceding its items.
    for order in itertools.permutations(range(3)):
        check('consistent.jsonl', normal, order)
        check('conflict.jsonl', conflict, order)
    paths = ['harness/evidence.py', 'harness/control.py', 'consistent.jsonl',
             'conflict.jsonl', 'verification/check_evidence.py',
             'verification/t1-baseline.json', 'case-control/stop-confirmation.json']
    result = {
        'passed': True,
        'acceptance_source': 'Latest user behavior contract; no maintainer checker provided.',
        'checks': 'Three required cases plus all six permutations of each fixed input.',
        'source_sha256': {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
        'cases': cases,
    }
    Path('verification/integration-result.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('PASS: three required cases and 12 event-order checks; result saved')


if __name__ == '__main__':
    main()
