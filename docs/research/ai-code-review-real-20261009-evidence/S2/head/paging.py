def after(ids, cursor, limit):
    return [i for i in ids if i > cursor][:limit]
