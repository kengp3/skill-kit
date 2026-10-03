from receipt import receipt

assert receipt("", []) == "Guest: 0 cents"
assert receipt("\t\n ", [(900, 0)]) == "Guest: 0 cents"
assert receipt("  Alice  Smith  ", [(125, 2), (50, 3), (100, 0)]) == "Alice  Smith: 400 cents"
print("PASS receipt whitespace, empty and zero-quantity boundaries")
