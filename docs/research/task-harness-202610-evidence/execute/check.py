from prices import total_cents
from labels import receipt_label
from receipt import receipt
assert total_cents([100, 205, 0]) == 305
assert total_cents([]) == 0
for value in (-1, 1.5, True, "100"):
    try:
        total_cents([value])
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError(f"accepted invalid price {value!r}")
assert receipt_label("  Alice  ") == "Alice"
assert receipt_label("  ") == "Guest"
assert receipt("  Alice  ", [100, 205]) == "Alice: 305 cents"
print("receipt checks passed")
