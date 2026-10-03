"""Run with python3 -B evidence/verify_integration.py from the project root."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from prices import total_cents
from labels import receipt_label
from receipt import receipt

assert total_cents([]) == 0
assert total_cents(iter([0, 100, 205])) == 305
assert total_cents([10**30, 1]) == 10**30 + 1
for value, error in ((-1, ValueError), (1.5, TypeError), (1.0, TypeError),
                     (True, TypeError), (False, TypeError), ('100', TypeError),
                     (None, TypeError)):
    for operation in (lambda: total_cents([0, value]),
                      lambda: receipt('Alice', [0, value])):
        try:
            operation()
        except error:
            pass
        else:
            raise AssertionError(f'accepted invalid price {value!r}')
assert receipt_label('  Alice  ') == 'Alice'
assert receipt_label('\t\n  ') == 'Guest'
assert receipt_label('') == 'Guest'
assert receipt_label('  Alice Smith  ') == 'Alice Smith'
assert receipt('  Alice  ', [100, 205]) == 'Alice: 305 cents'
assert receipt('\t\n ', []) == 'Guest: 0 cents'
baseline = json.loads((root / 'evidence/baseline.json').read_text())
for path, digest in baseline.items():
    if path not in {'prices.py', 'labels.py', 'receipt.py'}:
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, path
print('extended integration and preserved-file checks passed')
