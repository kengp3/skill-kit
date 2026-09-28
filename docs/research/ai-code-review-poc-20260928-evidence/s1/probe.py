import json
from api import list_page
from export import export_ids
rows = [{"id": 1}, {"id": 2}, {"id": 3}]
print(json.dumps({"page": list_page(rows, cursor=1, limit=1)}))
try:
    print(json.dumps({"export": export_ids(rows, limit=1, max_pages=5)}))
except RuntimeError as error:
    print(json.dumps({"error": str(error)}))
