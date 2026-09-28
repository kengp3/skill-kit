def page_after(rows, cursor, limit):
    return [row for row in rows if row["id"] >= cursor][:limit]
