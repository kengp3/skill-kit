from policy import discounted

def quote(cents, coupon):
    if type(cents) is not int or cents < 0:
        raise ValueError("nonnegative integer cents required")
    return discounted(cents, coupon)
