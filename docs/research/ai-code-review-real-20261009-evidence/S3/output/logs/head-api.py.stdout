from paging import after
def page(ids, cursor, limit):
    if type(limit) is not int or limit < 1:
        raise ValueError("limit")
    return after(ids, cursor, limit)
