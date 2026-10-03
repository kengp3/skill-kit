from amounts import subtotal

assert subtotal([(125, 2), (50, 3)]) == 400
assert subtotal([]) == 0
assert subtotal([(500, 0), (75, 4), (100, 0)]) == 300
assert subtotal([(0, 7)]) == 0
print("PASS subtotal acceptance")
