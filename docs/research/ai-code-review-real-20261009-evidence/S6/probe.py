import json
from api import submit
rows=[]
for ops in [[('a',1)],[('a',0)],[('a',4)],[('a',3)],[('a',1),('a',1)],[('a',1),('a',2)],[('a',2),('b',2)]]:
    state={'stock':3,'events':[],'done':{}}
    results=[submit(state,k,n) for k,n in ops]
    rows.append({'ops':ops,'results':results,'state':state})
print(json.dumps(rows,sort_keys=True))
