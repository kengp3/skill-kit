import importlib, itertools, json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
version = sys.argv[1]
sys.path.insert(0, str(root / 'snapshots' / version))
views = importlib.import_module('views')
checks = 0
failures = []
for now, expires, value in itertools.product((-1, 0, 1), (-1, 0, 1), ('', 'value')):
    store = {'a': (expires, value), 'b': (now + 1, 'B'), 'c': (now - 1, 'C')}
    for key in ('a', 'missing'):
        expected = value if key == 'a' and now < expires else None
        actual = views.preview(store, key, now)
        checks += 1
        if actual != expected:
            failures.append(dict(caller='preview', now=now, expires=expires, value=value, key=key, expected=expected, actual=actual))
    keys = ['b', 'a', 'missing', 'c', 'a', 'b']
    expected = [store[k][1] for k in keys if k in store and now < store[k][0]]
    actual = views.export_values(store, keys, now)
    checks += 1
    if actual != expected:
        failures.append(dict(caller='export_values', now=now, expires=expires, value=value, keys=keys, expected=expected, actual=actual))
checks += 2
assert views.export_values({}, [], 0) == []
assert views.preview({}, 'missing', 0) is None
print(json.dumps(dict(version=version, checks=checks, failures=failures), ensure_ascii=False, indent=2))
raise SystemExit(1 if failures else 0)
