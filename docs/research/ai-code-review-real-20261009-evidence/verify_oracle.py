from pathlib import Path
import json,subprocess,os,sys,hashlib,datetime
R=Path('/private/tmp/ai-review-real-20261009'); logs={}
programs={
'S1':'''import json
from api import checkout
rows=[]
for n in [0,1,999,1000,1001,100000]:
 rows.append([n,checkout(n),{'payable_cents':n-100 if n>=1000 else n}])
for n in [-1,True,1.0,'1000',None]:
 try: checkout(n); result='accepted'
 except Exception as e: result=[type(e).__name__,str(e)]
 rows.append([repr(n),result,['ValueError','amount']])
print(json.dumps(rows))
''',
'S2':'''import json
from api import page
rows=[]
for ids in [[],[1],[1,2,3],[2,4,6]]:
 for cursor in [-1,0,1,2,3,6,7]:
  for limit in [1,2,4]: rows.append([[ids,cursor,limit],page(ids,cursor,limit),[i for i in ids if i>cursor][:limit]])
for limit in [0,-1,True,1.5]:
 try: page([1],0,limit);result='accepted'
 except Exception as e: result=[type(e).__name__,str(e)]
 rows.append([repr(limit),result,['ValueError','limit']])
print(json.dumps(rows))
''',
'S4':'''import json
from views import preview,export_values
rows=[]
s={'a':(5,'value'),'b':(5,'')}
for t in [4,5,6]:
 rows.append([['preview',t],preview(s,'a',t),'value' if t<5 else None])
 rows.append([['export',t],export_values(s,['a','missing','b'],t),['value',''] if t<5 else []])
 rows.append([['missing',t],preview(s,'missing',t),None])
print(json.dumps(rows))
''',
'S5':'''import json,itertools
from api import submit
rows=[]
items=list(itertools.product(['a','b'],range(5)))
for length in [1,2]:
 for seq in itertools.product(items,repeat=length):
  state={'stock':3,'events':[],'done':{}};expected={'stock':3,'events':[],'done':{}}
  actual=[];want=[]
  for key,count in seq:
   actual.append(submit(state,key,count))
   if key in expected['done']: want.append(expected['done'][key])
   elif count<1 or count>expected['stock']:want.append('rejected')
   else:
    want.append('accepted');expected['stock']-=count;expected['events'].append({'key':key,'count':count});expected['done'][key]='accepted'
  rows.append([seq,{'return':actual,'state':state},{'return':want,'state':expected}])
print(json.dumps(rows))
'''}
programs['S3']=programs['S2'];programs['S6']=programs['S5'];programs['S7']=programs['S5']
for case,program in programs.items():
 logs[case]={}
 for side in ['base','head']:
  command=[sys.executable,'-B','-c',program]
  env=dict(os.environ,PYTHONPATH=str(R/case/side),PYTHONDONTWRITEBYTECODE='1')
  p=subprocess.run(command,cwd=R,env=env,text=True,capture_output=True,timeout=10)
  assert p.returncode==0,(case,side,p.stderr)
  rows=json.loads(p.stdout);fail=[r for r in rows if r[1]!=r[2]]
  logs[case][side]={'argv':command,'cwd':str(R),'PYTHONPATH':env['PYTHONPATH'],'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'count':len(rows),'mismatches':len(fail),'first_mismatch':fail[:1]}
expected={'S1':(1,0),'S2':(33,0),'S3':(33,None),'S4':(0,2),'S5':(0,0),'S6':(0,None),'S7':(0,0)}
for c,(b,h) in expected.items():
 if c in ['S2','S3']: assert logs[c]['base']['mismatches']>0
 else: assert logs[c]['base']['mismatches']==b,(c,logs[c]['base']['mismatches'])
 if h is None: assert logs[c]['head']['mismatches']>0
 else: assert logs[c]['head']['mismatches']==h,(c,logs[c]['head']['mismatches'])
result={'executed_at':datetime.datetime.now().astimezone().isoformat(),'logs':logs,'notes':'S7 local equality is insufficient; required real DB/broker evidence absent.'}
(R/'oracle-execution.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({c:{s:{k:v[k] for k in ['count','mismatches','first_mismatch']} for s,v in sides.items()} for c,sides in logs.items()},ensure_ascii=False,indent=2))
