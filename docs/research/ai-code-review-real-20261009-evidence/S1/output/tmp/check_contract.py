import importlib.util
import json
from pathlib import Path
import sys

snapshot = Path(sys.argv[1]).resolve()
version = sys.argv[2]
sys.path.insert(0, str(snapshot))
from api import checkout

class IntChild(int):
    pass

valid = [(0, 0), (1, 1), (999, 999), (1000, 900), (1001, 901),
         (10000, 9900), (10**100, 10**100 - 100)]
invalid = [-1, -1000, True, False, 0.0, 1000.0, float('nan'),
           float('inf'), '1000', '', None, [], {}, IntChild(1000)]
failures = []
for value, expected in valid:
    actual = checkout(value)
    ok = type(actual) is dict and actual == {'payable_cents': expected} and type(actual['payable_cents']) is int
    print(json.dumps({'version': version, 'input': repr(value), 'expected': expected, 'actual': actual, 'pass': ok}))
    if not ok:
        failures.append(repr(value))
for value in invalid:
    try:
        result = checkout(value)
    except Exception as exc:
        ok = type(exc) is ValueError and str(exc) == 'amount'
        actual = f'{type(exc).__name__}: {exc}'
    else:
        ok = False
        actual = repr(result)
    print(json.dumps({'version': version, 'input': repr(value), 'input_type': type(value).__name__, 'actual': actual, 'pass': ok}))
    if not ok:
        failures.append(repr(value))
print(json.dumps({'cases': len(valid) + len(invalid), 'failures': failures}))
sys.exit(bool(failures))
