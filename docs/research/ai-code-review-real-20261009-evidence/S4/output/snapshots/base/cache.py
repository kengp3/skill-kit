def lookup(store, key, now):
    item = store.get(key)
    if item is None:
        return None
    expires, value = item
    return value if now < expires else None
