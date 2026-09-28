from cache import lookup

def preview(store, key, now):
    return lookup(store, key, now)

def export_values(store, keys, now):
    return [value for key in keys if (value := lookup(store, key, now)) is not None]
