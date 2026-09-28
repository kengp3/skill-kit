from api import list_page

def export_ids(rows, limit=2, max_pages=10):
    result = []
    cursor = 0
    for _ in range(max_pages):
        page = list_page(rows, cursor, limit)
        if not page["items"]:
            return result
        result.extend(row["id"] for row in page["items"])
        cursor = page["next_cursor"]
    raise RuntimeError("pagination did not terminate")
