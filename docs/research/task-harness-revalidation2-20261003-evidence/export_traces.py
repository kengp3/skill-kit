"""Export bounded native tool evidence; this does not decide behavioral correctness."""
import hashlib
import json
from pathlib import Path
import sys

PREFIXES = tuple('/root/reval2_' + model + '_' + case for model in ('61', '56') for case in ('plan', 'parallel', 'resume', 'misleading'))
CALLS = {'function_call', 'custom_tool_call'}
OUTPUTS = {'function_call_output', 'custom_tool_call_output'}


def select(lines):
    rows = [json.loads(line) for line in lines]
    meta = rows[0]['payload']
    actor = meta.get('agent_path', '')
    if not any(actor == p or actor.startswith(p + '/') for p in PREFIXES):
        return None
    events = []
    for number, (raw, row) in enumerate(zip(lines, rows), 1):
        payload = row.get('payload', {})
        if row['type'] != 'response_item' or payload.get('type') not in CALLS | OUTPUTS:
            continue
        events.append({
            'source_line': number, 'raw_line_sha256': hashlib.sha256(raw.encode()).hexdigest(),
            'timestamp': row['timestamp'], 'ordinal': row.get('ordinal'),
            'payload': {k: v for k, v in payload.items() if k in
                        {'type', 'id', 'status', 'call_id', 'name', 'namespace', 'input', 'arguments', 'output'}}})
    calls = [e['payload']['call_id'] for e in events if e['payload']['type'] in CALLS]
    outputs = [e['payload']['call_id'] for e in events if e['payload']['type'] in OUTPUTS]
    if not calls or len(calls) != len(set(calls)) or sorted(calls) != sorted(outputs):
        raise ValueError(f'Incomplete or duplicate tool call/result pairs: {actor}')
    return {'identity': {k: meta.get(k) for k in ('id', 'parent_thread_id', 'agent_path', 'source')},
            'identity_raw_line_sha256': hashlib.sha256(lines[0].encode()).hexdigest(),
            'events': events}


def self_test():
    rows = [{'type': 'session_meta', 'payload': {'agent_path': PREFIXES[1]}}]
    rows += [{'type': 'response_item', 'timestamp': 'test', 'payload': {'type': t, 'call_id': 'c'}}
             for t in ('function_call', 'function_call_output')]
    lines = [json.dumps(row) + '\n' for row in rows]
    assert len(select(lines)['events']) == 2
    try:
        select(lines[:-1])
    except ValueError:
        pass
    else:
        raise AssertionError('Missing result was accepted')
    rows[0]['payload']['agent_path'] = '/root/unrelated'
    assert select([json.dumps(row) + '\n' for row in rows]) is None
    print('PASS complete pair, missing-result rejection, unrelated-actor exclusion')


if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        self_test()
    else:
        source, destination = map(Path, sys.argv[1:])
        destination.mkdir(exist_ok=True)
        manifest = []
        for path in sorted(source.rglob('*.jsonl')):
            with path.open() as stream:
                first = stream.readline()
                actor = json.loads(first).get('payload', {}).get('agent_path', '')
                if not any(actor == p or actor.startswith(p + '/') for p in PREFIXES):
                    continue
                result = select([first, *stream.readlines()])
            target = destination / (actor.removeprefix('/root/').replace('/', '--') + '.json')
            result['source_file'] = str(path.relative_to(source))
            target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            manifest.append({'actor': actor, 'file': target.name, 'events': len(result['events'])})
        (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps(manifest, indent=2))
