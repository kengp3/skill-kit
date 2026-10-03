from amounts import subtotal
from labels import label

def receipt(name, items):
    return f"{label(name)}: {subtotal(items)} cents"
