import importlib.util
import itertools
import pathlib
import sys

snapshot = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(snapshot))
from api import page

cases = [
    ('exact-boundary', [1, 3, 5], 3, 2, [5]),
    ('empty', [], 3, 2, []),
    ('before-first', [1, 3, 5], 0, 2, [1, 3]),
    ('after-last', [1, 3, 5], 6, 2, []),
    ('exact-last', [1, 3, 5], 5, 2, []),
    ('between', [1, 3, 5], 2, 1, [3]),
    ('cap', [1, 3, 5], 1, 1, [3]),
]
failures = []
for label, ids, cursor, limit, expected in cases:
    original = ids[:]
    actual = page(ids, cursor, limit)
    ok = actual == expected and ids == original
    print(f'{label}: input={(ids,cursor,limit)!r} expected={expected!r} actual={actual!r} unchanged={ids == original} pass={ok}')
    if not ok:
        failures.append(label)
for limit in [0, -1, True, False, 1.5, '2', None]:
    try:
        page([1, 3, 5], 1, limit)
    except ValueError as exc:
        assert str(exc) == 'limit'
        print(f'invalid-limit {limit!r}: ValueError("limit") PASS')
    else:
        failures.append(f'invalid-limit {limit!r}')
# Finite independent oracle: filtering and cap expressed as sequential admission.
count = 0
for size in range(6):
    for seq in itertools.combinations(range(-2, 3), size):
        for cursor in range(-3, 4):
            for limit in range(1, 7):
                expected = []
                for value in seq:
                    if value <= cursor:
                        continue
                    if len(expected) == limit:
                        break
                    expected.append(value)
                actual = page(list(seq), cursor, limit)
                count += 1
                if actual != expected:
                    failures.append(f'oracle {seq,cursor,limit}: {actual} != {expected}')
print(f'oracle cases={count}; total failures={len(failures)}')
assert not failures, repr(failures[:10])
