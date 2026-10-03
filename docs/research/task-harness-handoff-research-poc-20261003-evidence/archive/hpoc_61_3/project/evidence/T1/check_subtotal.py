from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from amounts import subtotal


cases = [
    ([(125, 2), (50, 3)], 400),
    ([], 0),
    ([(99, 1)], 99),
    ([(125, 0), (50, 3)], 150),
    ([(0, 10), (1, 1)], 1),
    ([(10**18 + 1, 10**6)], 10**24 + 10**6),
    ([(-50, 2), (125, 1)], 25),
]

for items, expected in cases:
    actual = subtotal(items)
    assert actual == expected, (items, expected, actual)
    assert isinstance(actual, int), (items, type(actual))

print(f"PASS subtotal: {len(cases)} cases")
