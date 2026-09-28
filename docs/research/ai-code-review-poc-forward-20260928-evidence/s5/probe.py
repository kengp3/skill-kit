import json
from views import preview, export_values
store = {"a": (10, "A"), "empty": (10, "")}
for now in (9, 10, 11):
    print(json.dumps({"now": now, "a": preview(store, "a", now), "empty": preview(store, "empty", now), "missing": preview(store, "missing", now), "export": export_values(store, ["missing", "a", "empty"], now)}))
