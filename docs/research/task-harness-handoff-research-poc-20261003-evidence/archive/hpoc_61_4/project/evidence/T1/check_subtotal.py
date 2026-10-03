import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from amounts import subtotal

assert subtotal([(125, 2), (50, 3)]) == 400
assert subtotal([]) == 0
assert subtotal([(125, 2)]) == 250
assert subtotal([(10, 3), (25, 4), (5, 2)]) == 140
assert subtotal([(125, 0), (50, 3)]) == 150
assert subtotal(iter([(125, 2), (50, 3)])) == 400
print("PASS subtotal: supplied cases, empty, single/multiple, zero quantity, one-pass iterable")
