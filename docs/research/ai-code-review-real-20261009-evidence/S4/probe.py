import json
from views import preview, export_values
s={"a":(5,"v"),"b":(5,"")}
print(json.dumps([[preview(s,"a",t),export_values(s,["a","b","missing"],t)] for t in [4,5,6]]))
