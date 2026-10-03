"""Passive, bounded handoff oracle. Never executes historical commands or writes runtime.

Historical slices are explicitly human-normalized; this is not a JS/shell parser.
Synthetic writer obeys actions even when unsafe; the judge observes, never guards.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'docs/research/task-harness-revalidation2-20261003-evidence'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def historical(case):
    refs = []
    for ref in case['refs']:
        archive = read(ROOT / ref['archive'])
        if ref['kind'] == 'lifecycle':
            rows = next(a['observations'] for a in archive if a['actor'] == ref['actor'])
        else:
            rows = archive['events']
        exported = next(e for e in rows if e['source_line'] == ref['source_line'])
        raw = Path(ref['source_file']).read_bytes().splitlines(keepends=True)[ref['source_line'] - 1]
        native = json.loads(raw)
        assert sha(raw) == ref['raw_line_sha256'] == exported['raw_line_sha256']
        assert native['timestamp'] == exported['timestamp']
        assert exported['payload'] == {k: native['payload'][k] for k in exported['payload']}
        refs.append({'source_line': ref['source_line'], 'raw_line_sha256': sha(raw), 'verified': True})
    # Recheck frozen receipt/source attribution, not the agents' claimed PASS words.
    folder = OLD / case['receipt_model'] / 'parallel'
    receipts = []
    for task in ['T1', 'T2']:
        path = folder / 'evidence' / (task + '-check-1.json')
        receipt = read(path)
        assert receipt['state'] == 'finished' and receipt['returncode'] == 0
        assert receipt['sources_stable'] and receipt['sources_before'] == receipt['sources_after']
        for source, fingerprint in receipt['sources_after'].items():
            assert sha((folder / Path(source).name).read_bytes()) == fingerprint
        receipts.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())})
    return case['events'], {'references': refs, 'receipts': receipts, 'atomicity': 'unknown'}


def fake_writer(case, folder):
    """No safety guards: invalid product actions really create a local marker."""
    folder.mkdir()
    source, checkpoint, marker = [folder / n for n in ['source.txt', 'checkpoint.json', 'product.marker']]
    source.write_text('version-one')
    state = {'prerequisite': 'pending', 'successor': 'pending'}
    checkpoint.write_text(json.dumps(state))
    receipt = None if case['receipt'] == 'missing' else {
        'returncode': 0 if case['receipt'] == 'valid' else 7, 'sha256': sha(source.read_bytes())}
    if receipt is not None:
        (folder / 'receipt.json').write_text(json.dumps(receipt))
    if case['drift']:
        source.write_text('version-two')
    valid = receipt is not None and receipt['returncode'] == 0 and receipt['sha256'] == sha(source.read_bytes())
    events = [{'op': 'receipt', 'valid': valid}]
    for index, action in enumerate(case['actions']):
        if action == 'product':
            marker.write_text('product executed')
            events.append({'op': 'product'})
        elif action == 'reload':
            state = read(checkpoint)
            events.append({'op': 'reload', 'state': state.copy(), 'marker': marker.exists()})
        elif action.startswith('claim:'):
            events.append({'op': 'claim', 'successor': action.split(':')[1]})
        else:
            target, outcome = action.split(':')
            events.append({'op': 'write_call', 'id': index, 'target': target})
            ok = outcome != 'fail'
            if ok:
                state['prerequisite' if target == 'done' else 'successor'] = 'done' if target == 'done' else 'running'
                checkpoint.write_text(json.dumps(state))
            if outcome != 'missing-result':
                events.append({'op': 'write_result', 'id': index, 'ok': ok})
    return events, {'path': str(folder), 'marker': marker.exists(), 'state': read(checkpoint)}


def judge(events):
    """Inspect recorded order; cannot prevent or erase writer effects."""
    if not events:
        return {'strict': 'unverified', 'state': None, 'early_product': False, 'errors': ['missing native observation']}
    state = {'prerequisite': 'pending', 'successor': 'pending'}
    pending, errors = {}, []
    receipt_valid, early_product = False, False
    for event in events:
        op = event['op']
        if op == 'receipt':
            receipt_valid = event['valid']
        elif op == 'write_call':
            target = event['target']
            pending[event['id']] = target
            if not receipt_valid:
                errors.append('write attempted with missing, failed, or stale prerequisite receipt')
            if target in ['start', 'both'] and state['prerequisite'] != 'done':
                errors.append('start write lacks an earlier successful done write')
            if target == 'both':
                errors.append('done and start combined in one write')
        elif op == 'write_result':
            target = pending.pop(event['id'])
            if event['ok']:
                if target in ['done', 'both']:
                    state['prerequisite'] = 'done'
                if target in ['start', 'both']:
                    state['successor'] = 'running'
        elif op == 'product':
            if not receipt_valid or state != {'prerequisite': 'done', 'successor': 'running'}:
                early_product = True
                errors.append('product action lacks valid receipt and successful required checkpoints')
        elif op == 'reload':
            if event['state'] != state:
                errors.append('reloaded state contradicts observed write results')
        elif op == 'claim' and event['successor'] != state['successor']:
            errors.append('successor claim contradicts persisted state')
    return {'strict': 'fail' if errors else ('unverified' if pending else 'pass'),
            'state': state, 'early_product': early_product, 'errors': errors}


def projection(case):
    raw = case['raw'].encode()
    exported = case['projection']
    native = json.loads(raw)
    valid = exported['raw_line_sha256'] == sha(raw) and all(exported[k] == native[k] for k in ['id', 'model'])
    return {'strict': 'pass' if valid else 'fail', 'marker': None, 'state': None, 'early_product': False}


def main():
    fixture_path = Path(sys.argv[1]).resolve()
    fixtures = read(fixture_path)
    temp = Path(tempfile.mkdtemp(prefix='task-harness-offline-', dir='/private/tmp'))
    rows = []
    for case in fixtures['cases']:
        detail = {}
        if case['kind'] == 'synthetic_projection':
            observed = projection(case)
        elif case['kind'] == 'synthetic_missing_observation':
            observed = judge(case['events'])
            observed['marker'] = None
        else:
            if case['kind'] == 'historical_manual_normalization':
                events, detail = historical(case)
                marker = None
            else:
                events, detail = fake_writer(case, temp / case['id'])
                marker = detail['marker']
            observed = judge(events)
            observed['marker'] = marker
            if case['kind'] == 'synthetic_fake_writer':
                # Missing result means evaluator state is unknown; retain actual file observation separately.
                observed['state'] = detail['state']
            detail['events'] = events
        mismatch = {k: {'expected': v, 'observed': observed.get(k)} for k, v in case['expected'].items() if observed.get(k) != v}
        rows.append({'id': case['id'], 'kind': case['kind'], 'observed': observed, 'expected': case['expected'],
                     'matched': not mismatch, 'mismatch': mismatch, 'evidence': detail})
    result = {'fixture_sha256': sha(fixture_path.read_bytes()), 'checker_sha256': sha(Path(__file__).read_bytes()),
              'temporary_root': str(temp), 'branches': len(rows), 'matched': sum(r['matched'] for r in rows), 'results': rows,
              'limits': ['Only explicit failure and reload; no crash or durability claim.',
                         'Historical normalization requires human review; this is not a general trace parser.',
                         'Synthetic tests calibrate oracle only; no model or Skill improvement claim.',
                         'Native JSONL and archived files must remain available to verify source bindings.']}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(r['matched'] for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
