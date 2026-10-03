from labels import label

assert label("  Alice  ") == "Alice"
assert label("Alice") == "Alice"
assert label("") == "Guest"
assert label(" \t\n ") == "Guest"
assert label("  Alice  Bob  ") == "Alice  Bob"
print("PASS label boundary cases")
