#!/usr/bin/env python3
"""Build isolated review inputs and retain real process output for report QA."""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def execute(argv, cwd, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=90)
    return dict(argv=argv, cwd=str(cwd), exit_code=result.returncode,
                stdout=result.stdout, stderr=result.stderr)


def freeze(case):
    base, head = case / 'base', case / 'head'
    names = sorted({p.name for p in base.iterdir()} | {p.name for p in head.iterdir()})
    patch = ''
    for name in names:
        old = (base / name).read_text().splitlines(keepends=True) if (base / name).exists() else []
        new = (head / name).read_text().splitlines(keepends=True) if (head / name).exists() else []
        patch += ''.join(difflib.unified_diff(old, new, fromfile='base/' + name, tofile='head/' + name))
    write(case / 'diff.patch', patch)
    files = {str(p.relative_to(case)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(case.rglob('*')) if p.is_file()}
    write(case / 'manifest.json', json.dumps({'comparison': 'direct snapshots', 'files': files}, indent=2) + '\n')


def python_case(out, name, contract, base, head, probe):
    case = out / name
    for side, files in [('base', base), ('head', head)]:
        for path, source in files.items():
            write(case / side / path, source)
    write(case / 'contract.json', json.dumps(contract, ensure_ascii=False, indent=2) + '\n')
    write(case / 'probe.py', probe)
    records = {'executed_at': dt.datetime.now().astimezone().isoformat(), 'runs': {}}
    for side in ('base', 'head'):
        env = dict(os.environ, PYTHONPATH=str(case / side), PYTHONDONTWRITEBYTECODE='1')
        records['runs'][side] = execute([sys.executable, '-B', str(case / 'probe.py')], case, env)
        records['runs'][side]['PYTHONPATH'] = str(case / side)
        if records['runs'][side]['exit_code']:
            raise RuntimeError(records['runs'][side])
    write(case / 'execution.json', json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    freeze(case)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--forward-only', action='store_true')
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir()  # A run is immutable: refuse an existing output directory.
    if args.forward_only:
        shutil.copytree(ROOT / 'skills/ai-code-review', out / 'skill-r2')
        old = '''def lookup(store, key, now):
    item = store.get(key)
    if item is None:
        return None
    expires, value = item
    return value if now < expires else None
'''
        new = '''from policy import fresh

def lookup(store, key, now):
    item = store.get(key)
    if item is None:
        return None
    expires, value = item
    return value if fresh(now, expires) else None
'''
        callers = '''from cache import lookup

def preview(store, key, now):
    return lookup(store, key, now)

def export_values(store, keys, now):
    return [value for key in keys if (value := lookup(store, key, now)) is not None]
'''
        python_case(out, 's5', {'scope': 'cache policy extraction',
            'requirements': 'Preserve lookup, preview and export_values behavior. Stored values are strings (including empty string); each entry is (expires, value), expires and now are caller-supplied integer ticks from the same clock. Validity interval excludes expires: only now < expires is fresh. Missing or expired lookup returns None. Export preserves input key order and includes every fresh value, including empty strings. Single-threaded local scope; no real clock or external integration is required. Review full diff and run before/at/after expiry, missing and empty-value cases for both callers.'},
            {'cache.py': old, 'views.py': callers},
            {'cache.py': new, 'views.py': callers,
             'policy.py': 'def fresh(now, expires):\n    return now <= expires\n'},
            '''import json
from views import preview, export_values
store = {"a": (10, "A"), "empty": (10, "")}
for now in (9, 10, 11):
    print(json.dumps({"now": now, "a": preview(store, "a", now), "empty": preview(store, "empty", now), "missing": preview(store, "missing", now), "export": export_values(store, ["missing", "a", "empty"], now)}))
''')
        print(json.dumps({'out': str(out), 'cases': ['s5']}))
        return
    shutil.copytree(ROOT / 'skills/ai-code-review', out / 'skill-r1')
    source = ROOT / 'docs/research/ai-code-review-paging-20260925-evidence/input'
    python_case(out, 's1', {'scope': 'cursor pagination refactor',
        'requirements': (source / 'SPEC.md').read_text()},
        {p.name: p.read_text() for p in (source / 'base').glob('*.py')},
        {p.name: p.read_text() for p in (source / 'head').glob('*.py')},
        '''import json
from api import list_page
from export import export_ids
rows = [{"id": 1}, {"id": 2}, {"id": 3}]
print(json.dumps({"page": list_page(rows, cursor=1, limit=1)}))
try:
    print(json.dumps({"export": export_ids(rows, limit=1, max_pages=5)}))
except RuntimeError as error:
    print(json.dumps({"error": str(error)}))
''')
    api = '''from policy import discounted

def quote(cents, coupon):
    if type(cents) is not int or cents < 0:
        raise ValueError("nonnegative integer cents required")
    return discounted(cents, coupon)
'''
    policy = 'def discounted(cents, coupon):\n    return cents - (100 if coupon and cents > 1000 else 0)\n'
    python_case(out, 's2', {'scope': 'approved quote behavior change',
        'requirements': 'Public quote accepts nonnegative integer cents. Coupon subtracts 100 cents at subtotal >= 1000 cents. This inclusive threshold is an approved new requirement; base used > 1000. No other behavior change. Reject negative and non-integer cents. Review and execute boundary, coupon-off and rejection inputs; no external integrations required.'},
        {'api.py': api, 'policy.py': policy},
        {'api.py': api, 'policy.py': policy.replace('> 1000', '>= 1000')},
        '''import json
from api import quote
for cents, coupon in [(999, True), (1000, True), (1001, True), (1000, False), (0, True), (-1, True), (1.5, True)]:
    try:
        print(json.dumps({"cents": cents, "coupon": coupon, "result": quote(cents, coupon)}))
    except ValueError as error:
        print(json.dumps({"cents": cents, "coupon": coupon, "error": str(error)}))
''')
    with tempfile.TemporaryDirectory(prefix='review-returns-') as temporary:
        original = Path(temporary) / 'run'
        record = execute([sys.executable, '-B', str(ROOT / 'tests/poc_returns_review.py'), '--out', str(original)], ROOT)
        if record['exit_code']:
            raise RuntimeError(record)
        for side in ('base', 'head'):
            shutil.copytree(original / side, out / 's3' / side)
        for name in ('execution.json', 'environment.json', 'diff.patch'):
            shutil.copy2(original / name, out / 's3' / name)
        write(out / 's3' / 'generation.json', json.dumps(record, indent=2) + '\n')
        write(out / 's3' / 'provenance.txt', 'Sources and original logs copied byte-for-byte from a disposable Git fixture. Original build paths no longer exist; recompile retained snapshots into a new temporary directory to rerun. The direct patch and manifest describe the retained comparison.\n')
        freeze(out / 's3')
    old = '''def submit(bus, order_id):
    payload = {"type": "OrderAccepted", "order_id": order_id}
    if not bus.publish(payload):
        raise RuntimeError("publish rejected")
    return "accepted"
'''
    new = '''def make_payload(order_id):
    return {"type": "OrderAccepted", "order_id": order_id}

def submit(bus, order_id):
    if not bus.publish(make_payload(order_id)):
        raise RuntimeError("publish rejected")
    return "accepted"
'''
    python_case(out, 's4', {'scope': 'publisher extraction acceptance',
        'requirements': 'Preserve submit behavior: publish exactly once with type OrderAccepted and the order_id. Return accepted only for a truthy acknowledgement; otherwise raise RuntimeError. order_id is an upstream-validated nonempty string. Acceptance explicitly requires source review, local success/rejection cases AND an actual durable transport integration log proving data survives process restart before acknowledgement. Only fake transport is supplied; actual transport adapter, endpoint and integration logs are unavailable in this offline package. Do not infer durable delivery from fake.publish. No actual deployment is authorized.'},
        {'publisher.py': old}, {'publisher.py': new},
        '''import json
from publisher import submit
class FakeBus:
    def __init__(self, acknowledge):
        self.acknowledge = acknowledge
        self.calls = []
    def publish(self, payload):
        self.calls.append(payload)
        return self.acknowledge
for acknowledge in (True, False):
    bus = FakeBus(acknowledge)
    try:
        result = {"result": submit(bus, "o-1")}
    except RuntimeError as error:
        result = {"error": str(error)}
    print(json.dumps({"acknowledge": acknowledge, "calls": bus.calls, **result}))
''')
    print(json.dumps({'out': str(out), 'cases': ['s1', 's2', 's3', 's4']}))


if __name__ == '__main__':
    main()
