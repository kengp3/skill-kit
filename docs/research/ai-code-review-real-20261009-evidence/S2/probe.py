import json
from api import page
print(json.dumps([page([1,2,3],2,2),page([],0,1),page([1,2,3],0,1)]))
