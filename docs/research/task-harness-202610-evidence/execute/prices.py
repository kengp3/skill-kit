def total_cents(prices):
    total = 0
    for price in prices:
        if not isinstance(price, int) or isinstance(price, bool):
            raise TypeError("Prices must be integers")
        if price < 0:
            raise ValueError("Prices must be nonnegative")
        total += price
    return total
