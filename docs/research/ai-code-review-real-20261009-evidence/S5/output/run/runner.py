import sys,json,itertools,copy
from pathlib import Path
side=sys.argv[1]
sys.path.insert(0,str(Path(__file__).parent/'snapshots'/side))
from api import submit
ops=list(itertools.product(['a','b'],range(5)))
rows=[]
for length in (1,2):
 for sequence in itertools.product(ops,repeat=length):
  state={'stock':3,'events':[],'done':{}}; steps=[]
  for key,count in sequence:
   try: result=submit(state,key,count); error=None
   except Exception as e: result=None; error={'type':type(e).__name__,'message':str(e)}
   steps.append({'response':result,'error':error,'stock':state['stock'],'done':copy.deepcopy(state['done']),'events':copy.deepcopy(state['events'])})
  rows.append({'id':str(len(rows)+1),'input':{'operations':[list(x) for x in sequence]},'initial_state':{'stock':3,'events':[],'done':{}},'environment':{},'observed':{'steps':steps}})
print(json.dumps(rows,sort_keys=True))
