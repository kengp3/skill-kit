import subprocess,pathlib,json,os,sys,hashlib
root=pathlib.Path('/private/tmp/ai-review-real-20261009/S7');out=root/'output';skill=root.parent/'skill'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');logs=[]
def run(name,args,extra=None):
 e=dict(env);e.update(extra or {});p=subprocess.run(args,capture_output=True,text=True,env=e);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);logs.append({'name':name,'command':args,'environment':{'PYTHONDONTWRITEBYTECODE':'1',**(extra or {})},'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});(out/'execution.json').write_text(json.dumps(logs,indent=2));assert p.returncode==0,(name,p.stderr,p.stdout);return p.stdout
run('prepare',[sys.executable,str(skill/'scripts/review.py'),'prepare','--old-repo',str(root/'repo-base'),'--old-ref','a9fabff50c6d3b2be51e1cc18da2527709eaecb3','--new-repo',str(root/'repo-head'),'--new-ref','aedb2ff70e63fef785d9210eddf30595e8e72386','--out',str(out/'snapshot')])
run('verify',[sys.executable,str(skill/'scripts/review.py'),'verify','--run',str(out/'snapshot')])
for side,kind in [('base','old'),('head','new')]:
 for f in (root/side).glob('*.py'):
  assert f.read_bytes()==(out/'snapshot/snapshots'/kind/f.name).read_bytes(),str(f)
run('environment',[sys.executable,'-c','import sys,platform;print(sys.version);print(platform.platform())'])
for side in ['old','new']:
 run('probe-'+side,[sys.executable,str(root/'probe.py')],{'PYTHONPATH':str(out/'snapshot/snapshots'/side)})
for side in ['old','old','new']:
 name='cases-old-repeat' if side=='old' and (out/'cases-old.stdout').exists() else 'cases-'+side
 run(name,[sys.executable,str(out/'tmp/cases.py'),str(out/'snapshot/snapshots'/side)])
a=json.loads((out/'cases-old.stdout').read_text());b=json.loads((out/'cases-new.stdout').read_text());repeat=json.loads((out/'cases-old-repeat.stdout').read_text())
def equal(x,y):return json.dumps(x,sort_keys=True,separators=(',',':'))==json.dumps(y,sort_keys=True,separators=(',',':'))
assert equal(a,repeat)
mut=json.loads(json.dumps(a));next(row for row in mut if row['steps'][-1]['state']['events'])['steps'][-1]['state']['events'] *= 2
assert not equal(a,mut)
(out/'known-mutation.json').write_text(json.dumps(mut,indent=2))
diffs=[{'old':x,'new':y} for x,y in zip(a,b) if not equal(x,y)]
assert len(a)==len(b)==110
summary={'case_count':len(a),'old_old_equal':equal(a,repeat),'duplicate_event_mutation_detected':not equal(a,mut),'old_new_differences':diffs,'local_equivalence_only':True}
(out/'comparison.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary));assert not diffs
