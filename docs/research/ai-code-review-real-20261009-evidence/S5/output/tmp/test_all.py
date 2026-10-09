import sys,subprocess,pathlib,json,hashlib,copy
p=pathlib.Path(__file__).resolve().parents[1]; run=p/'run'; root=p.parent
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records={}
for side in ['old','old-again','new']:
 actual='old' if side=='old-again' else side
 argv=[sys.executable,str(run/'runner.py'),actual]
 r=subprocess.run(argv,capture_output=True,text=True)
 (p/(side+'-execution.json')).write_text(json.dumps({'command':argv,'stdout':r.stdout,'stderr':r.stderr,'exit_code':r.returncode},indent=2))
 assert r.returncode==0
 records[side]=json.loads(r.stdout)
assert len(records['old'])==110
assert records['old']==records['old-again']
# Calibration uses copies of captured observations; no source is changed.
mutations={}
for name in ['response','stock','done','duplicate-event','event-order']:
 bad=copy.deepcopy(records['old'])
 idx=next(i for i,row in enumerate(bad) if len(row['observed']['steps'][-1]['events'])==2)
 step=bad[idx]['observed']['steps'][-1]
 if name=='response': step['response']='rejected'
 elif name=='stock': step['stock']+=1
 elif name=='done': step['done']={}
 elif name=='duplicate-event': step['events'].append(copy.deepcopy(step['events'][0]))
 else: step['events'].reverse()
 assert bad!=records['old'],name
 mutations[name]='detected'
contract={'scope':json.loads((root/'contract.json').read_text())['requirements'],'artifacts':{'runner.py':h(run/'runner.py')},'cases':[{k:v for k,v in r.items() if k!='observed'}|{'observe':['steps']} for r in records['old']]}
(run/'contract.json').write_text(json.dumps(contract,indent=2))
targets=json.loads((root/'targets.json').read_text())
for side in ['old','new']:
 payload={'side':side,'commit':targets['base' if side=='old' else 'head']['commit'],'manifest_sha256':h(run/'manifest.json'),'contract_sha256':h(run/'contract.json'),'command':[sys.executable,str(run/'runner.py'),side],'exit_code':0,'records':records[side]}
 (run/(side+'.json')).write_text(json.dumps(payload,indent=2))
for side in ['base','head']:
 repo=root/('repo-'+side)
 for f in (root/side).glob('*.py'):
  r=subprocess.run(['git','-C',str(repo),'show',targets[side]['commit']+':'+f.name],capture_output=True)
  assert r.returncode==0 and r.stdout==f.read_bytes()
print(json.dumps({'cases':110,'step_observations':210,'old_old':'PASS','mutations':mutations,'old_new':'PASS' if records['old']==records['new'] else 'FAIL','snapshot_dirs_match_commits':True},indent=2))
assert records['old']==records['new']
