from amounts import subtotal
from labels import label
from receipt import receipt
assert subtotal([(125,2),(50,3)]) == 400
assert subtotal([]) == 0
assert label("  Alice  ") == "Alice"
assert label(" ") == "Guest"
assert receipt(" Alice ", [(125,2),(50,3)]) == "Alice: 400 cents"
assert receipt(" ", []) == "Guest: 0 cents"
print("PASS receipt integration")
