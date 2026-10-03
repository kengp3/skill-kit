import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from amounts import subtotal

assert subtotal([(125, 2), (50, 3)]) == 400
assert subtotal([]) == 0
assert subtotal([(125, 0)]) == 0
assert subtotal([(75, 3)]) == 225
print("T1 acceptance checks passed")
