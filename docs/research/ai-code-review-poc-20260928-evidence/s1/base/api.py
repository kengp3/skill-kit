from paging import page_after

def list_page(rows, cursor=0, limit=2):
    batch = page_after(rows, cursor, limit)
    return {"items": batch, "next_cursor": batch[-1]["id"] if batch else None}
