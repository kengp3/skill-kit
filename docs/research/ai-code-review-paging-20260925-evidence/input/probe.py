from api import list_page
from export import export_ids

rows = [{"id": 1}, {"id": 2}, {"id": 3}]
assert [row["id"] for row in list_page(rows, cursor=1, limit=1)["items"]] == [2]
print("page boundary passed")
assert export_ids(rows, limit=1, max_pages=5) == [1, 2, 3]
print("export traversal passed")
