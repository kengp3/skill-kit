import sys,json,itertools,copy
sys.path.insert(0,sys.argv[1])
from api import submit
ops=list(itertools.product(['a','b'],range(5)));rows=[]
for length in [1,2]:
 for seq in itertools.product(ops,repeat=length):
  state={'stock':3,'events':[],'done':{}};steps=[]
  for key,count in seq:
   try: result=submit(state,key,count);error=None
   except Exception as exc:result=None;error={'type':type(exc).__name__,'message':str(exc)}
   steps.append({'result':result,'error':error,'state':copy.deepcopy(state)})
  rows.append({'operations':seq,'initial_state':{'stock':3,'events':[],'done':{}},'steps':steps})
print(json.dumps(rows,sort_keys=True))
