import json
from api import checkout
print(json.dumps([checkout(n) for n in [0,999,1000,1001]]))
