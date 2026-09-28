def discounted(cents, coupon):
    return cents - (100 if coupon and cents >= 1000 else 0)
