from pricing import price
def checkout(cents):
    if type(cents) is not int or cents < 0:
        raise ValueError("amount")
    return {"payable_cents": price(cents)}
