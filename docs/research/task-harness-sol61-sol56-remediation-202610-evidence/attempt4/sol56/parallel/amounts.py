def subtotal(items):
    return sum(cents * quantity for cents, quantity in items)
