from prices import total_cents
from labels import receipt_label

def receipt(name, prices):
    return f"{receipt_label(name)}: {total_cents(prices)} cents"
