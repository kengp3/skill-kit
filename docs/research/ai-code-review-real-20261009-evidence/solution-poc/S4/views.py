from cache import lookup
def preview(store, key, now):
    return lookup(store, key, now)
def export_values(store, keys, now):
    return [v for key in keys if (v := lookup(store, key, now)) is not None]
