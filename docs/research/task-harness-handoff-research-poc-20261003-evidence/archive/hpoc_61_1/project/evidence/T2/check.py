import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from labels import label

assert label("  Alice  ") == "Alice"
assert label("") == "Guest"
assert label("   ") == "Guest"
assert label("\t\n Alice \n\t") == "Alice"
assert label("\t\n") == "Guest"
assert label("  Alice  Smith  ") == "Alice  Smith"
assert label("  Alice\tSmith  ") == "Alice\tSmith"

print("T2 assertions passed")
