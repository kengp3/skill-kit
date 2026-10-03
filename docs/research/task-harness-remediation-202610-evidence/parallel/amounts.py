def subtotal(items):
    return sum(unit_cents * quantity for unit_cents, quantity in items)
