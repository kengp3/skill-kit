from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from receipt import receipt

cases = [
    (" Alice ", [(125, 2), (50, 3)], "Alice: 400 cents"),
    (" ", [], "Guest: 0 cents"),
    ("", [(50, 0)], "Guest: 0 cents"),
    ("\tAlice  Bob\n", [(0, 10), (99, 1)], "Alice  Bob: 99 cents"),
    ("訪客", [(10**18 + 1, 10**6)], "訪客: 1000000000000000001000000 cents"),
    (" A ", [(-50, 2), (125, 1)], "A: 25 cents"),
]
for name, items, expected in cases:
    original = items.copy()
    assert receipt(name, items) == expected, (name, items, expected)
    assert items == original
print(f"PASS receipt boundaries: {len(cases)} cases")
