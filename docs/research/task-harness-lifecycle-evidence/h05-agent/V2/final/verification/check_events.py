"""Acceptance derived from the user's behavior contract; standard library only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.evidence import summarize_events


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    results = {}
    failures = []
    with tempfile.TemporaryDirectory(dir=ROOT / 'verification') as directory:
        reverse = Path(directory) / 'reversed.jsonl'
        lines = (ROOT / 'conflict.jsonl').read_text().splitlines()
        reverse.write_text('\n'.join([lines[1], lines[0], *lines[2:]]) + '\n')
        cases = [('normal', ROOT / 'consistent.jsonl', 'complete', 1, 0),
                 ('conflict', ROOT / 'conflict.jsonl', 'partial', 0, 1),
                 ('reversed', reverse, 'partial', 0, 1)]
        for name, path, coverage, completed, unknown in cases:
            result = summarize_events([path], thread_id='root', turn_ids=['first'])
            results[name] = result
            expected = {'coverage': coverage, 'final_turn_status': 'completed',
                        'commands_completed': completed, 'command_outcomes_unknown': unknown}
            observed = {key: result.get(key, result['metrics'].get(key)) for key in expected}
            if observed != expected:
                failures.append({'case': name, 'expected': expected, 'observed': observed})
            if name != 'normal':
                commands = [i for i in result['items'] if i['type'] == 'commandExecution']
                if (len(commands) != 1 or commands[0]['status'] != 'unknown'
                        or commands[0]['exit_code'] is not None
                        or {r['line'] for r in commands[0]['evidence']} != {1, 2}
                        or not any('Conflicting' in reason for reason in result['unverified'])):
                    failures.append({'case': name, 'error': 'Missing unresolved command/conflict references'})
        # Compare semantics separately from source paths and reversed line numbers.
        semantic = lambda r: (r['coverage'], r['final_turn_status'], r['metrics'],
                              [{k: v for k, v in i.items() if k != 'evidence'} for i in r['items']])
        if semantic(results['conflict']) != semantic(results['reversed']):
            failures.append({'error': 'Conflict semantics depend on arrival order'})
    report = {'criteria_source': 'Latest user behavior contract, no maintainer checker',
              'source_sha256': sha(ROOT / 'harness/evidence.py'),
              'check_sha256': sha(Path(__file__)),
              'input_sha256': {name: sha(ROOT / name) for name in
                               ['consistent.jsonl', 'conflict.jsonl', 'verification/preseed-normal.json']},
              'reversed_derivation': 'Swap first two conflict item records; retain independent terminal record',
              'passed': not failures, 'failures': failures, 'results': results}
    target = Path(sys.argv[1])
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'failures': failures, 'report': str(target)}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(run())
