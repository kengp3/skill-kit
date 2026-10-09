import copy,hashlib,itertools,json,os,pathlib,platform,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; RUN=ROOT/'run'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def cases():
    ops=list(itertools.product(['a','b'],range(5)))
    return [{'id':f'case-{i:03d}','input':{'ops':x},'initial_state':{'stock':3,'events':[],'done':{}},'environment':{'python':platform.python_version()},'observe':['steps']} for i,x in enumerate(list(itertools.product(ops,repeat=1))+list(itertools.product(ops,repeat=2)))]
if len(sys.argv)>1:
    side=sys.argv[1]; sys.path.insert(0,str(RUN/'snapshots'/side))
    from api import submit
    records=[]
    for c in cases():
        state=copy.deepcopy(c['initial_state']); steps=[]
        for key,count in c['input']['ops']:
            result=None; error=None
            try: result=submit(state,key,count)
            except Exception as exc: error={'type':type(exc).__name__,'message':str(exc)}
            steps.append({'return':result,'error':error,'stock':state['stock'],'events':copy.deepcopy(state['events']),'done':copy.deepcopy(state['done'])})
        records.append({k:v for k,v in c.items() if k!='observe'}|{'observed':{'steps':steps}})
    print(json.dumps(records,sort_keys=True));sys.exit(0)
manifest=json.loads((RUN/'manifest.json').read_text())
write(RUN/'contract.json',{'scope':'S6 contract.json 完整 110 組序列；逐步回值、例外、庫存、done、ordered events','artifacts':{'../tmp/harness.py':sha(pathlib.Path(__file__))},'cases':cases()})
# helper artifacts must stay inside run; copy exact harness bytes rather than point outside.
(RUN/'harness-source.py').write_bytes(pathlib.Path(__file__).read_bytes())
contract=json.loads((RUN/'contract.json').read_text());contract['artifacts']={'harness-source.py':sha(RUN/'harness-source.py')};write(RUN/'contract.json',contract)
allrows={}
for label,side in [('old','old'),('old-repeat','old'),('new','new')]:
    cmd=[sys.executable,str(pathlib.Path(__file__)),side]
    p=subprocess.run(cmd,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    write(ROOT/'logs'/f'run-{label}.json',{'command':cmd,'stdout':p.stdout,'stderr':p.stderr,'exit_code':p.returncode})
    assert p.returncode==0,p.stderr
    rows=json.loads(p.stdout);allrows[label]=rows
    if label!='old-repeat': write(RUN/f'{label}.json',{'side':side,'commit':manifest[side]['commit'],'manifest_sha256':sha(RUN/'manifest.json'),'contract_sha256':sha(RUN/'contract.json'),'command':cmd,'exit_code':p.returncode,'records':rows})
assert allrows['old']==allrows['old-repeat']
cal={'old_old_equal':True}
# Mutate actual old observations only for comparator negative controls, not business execution.
for kind in ['missing','duplicate','reorder','count']:
    mutated=copy.deepcopy(allrows['old'])
    row=next(r for r in mutated if r['input']['ops']==[['a',1],['b',1]])
    ev=row['observed']['steps'][-1]['events']
    if kind=='missing': ev.pop()
    elif kind=='duplicate': ev.append(copy.deepcopy(ev[-1]))
    elif kind=='reorder': ev.reverse()
    else: ev[0]['count']=2
    assert mutated!=allrows['old'];cal[kind+'_detected']=True
write(ROOT/'calibration.json',cal)
diffs=[{'id':a['id'],'ops':a['input']['ops'],'old':a['observed'],'new':b['observed']} for a,b in zip(allrows['old'],allrows['new']) if a!=b]
write(ROOT/'counterexamples.json',diffs)
print(json.dumps({'case_count':len(cases()),'different_cases':len(diffs),'calibration':cal,'first_difference':diffs[0]},ensure_ascii=False,indent=2))
