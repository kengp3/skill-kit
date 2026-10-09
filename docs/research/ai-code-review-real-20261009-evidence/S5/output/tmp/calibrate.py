import json,pathlib,copy,subprocess,sys,os,platform
out=pathlib.Path(__file__).resolve().parents[1]; run=out/'run'; skill=out.parent.parent/'skill'
old=json.loads((run/'old.json').read_text()); new=json.loads((run/'new.json').read_text())
for name in ['old-old','duplicate-event','event-order','stock','done','response']:
 data=copy.deepcopy(new); data['records']=copy.deepcopy(old['records'])
 if name!='old-old':
  step=next(r['observed']['steps'][-1] for r in data['records'] if len(r['observed']['steps'][-1]['events'])==2)
  if name=='duplicate-event': step['events'].append(copy.deepcopy(step['events'][0]))
  elif name=='event-order': step['events'].reverse()
  elif name=='stock': step['stock']+=1
  elif name=='done': step['done']={}
  else: step['response']='rejected'
 f=run/('calibration-'+name+'.json'); f.write_text(json.dumps(data,indent=2))
 cmd=[sys.executable,str(skill/'scripts/review.py'),'compare','--run',str(run),'--contract',str(run/'contract.json'),'--old',str(run/'old.json'),'--new',str(f),'--out',str(run/('result-'+name+'.json'))]
 r=subprocess.run(cmd,capture_output=True,text=True)
 (out/('calibration-'+name+'-log.json')).write_text(json.dumps({'command':cmd,'stdout':r.stdout,'stderr':r.stderr,'exit_code':r.returncode,'note':'Synthetic observation comparator calibration, not new business execution'},indent=2))
 assert r.returncode==(0 if name=='old-old' else 1),(name,r.stdout,r.stderr)
 print(name,r.returncode)
for side in ['old','new']:
 env=os.environ.copy(); env['PYTHONPATH']=str(run/'snapshots'/side); env['PYTHONDONTWRITEBYTECODE']='1'
 cmd=[sys.executable,str(out.parent/'probe.py')]; r=subprocess.run(cmd,env=env,capture_output=True,text=True)
 (out/('probe-'+side+'.json')).write_text(json.dumps({'command':cmd,'environment':{'PYTHONPATH':env['PYTHONPATH'],'PYTHONDONTWRITEBYTECODE':'1'},'stdout':r.stdout,'stderr':r.stderr,'exit_code':r.returncode},indent=2)); assert r.returncode==0
print(json.dumps({'python':sys.version,'platform':platform.platform()}))
