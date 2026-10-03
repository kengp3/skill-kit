from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from labels import label


cases = [
    ("  Alice  ", "Alice"),
    ("", "Guest"),
    ("   ", "Guest"),
    ("\t\n", "Guest"),
    ("\tAlice\n", "Alice"),
    ("  Alice  Bob  ", "Alice  Bob"),
]
for name, expected in cases:
    actual = label(name)
    assert actual == expected, (name, expected, actual)

print(f"PASS: {len(cases)} label cases")
