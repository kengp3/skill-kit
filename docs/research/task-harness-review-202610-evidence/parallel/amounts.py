def subtotal(items):
    return sum(price * quantity for price, quantity in items)
