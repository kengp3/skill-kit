from receipt import receipt


assert receipt("", []) == "Guest: 0 cents"
assert receipt(" \t\n ", [(99, 0)]) == "Guest: 0 cents"
assert receipt("  Alice  Bob  ", [(25, 4), (10, 3)]) == "Alice  Bob: 130 cents"
assert receipt("\t客戶\n", iter([(125, 2), (50, 3)])) == "客戶: 400 cents"
print("PASS receipt boundaries: empty, whitespace, zero quantity, internal spaces, Unicode and one-pass iterable")
