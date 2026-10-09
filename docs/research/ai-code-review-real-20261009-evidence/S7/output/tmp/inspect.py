import subprocess,json,pathlib
r=pathlib.Path('/private/tmp/ai-review-real-20261009/S7'); out=r/'output'
(out/'start.json').write_text(json.dumps({'tool':'clock__curr_time','raw_output':{'current_time':'2026-10-09 11:31:17 UTC'}}))
commands=[]
for side in ['base','head']:
 repo=r/('repo-'+side)
 for args in [['rev-parse','HEAD'],['symbolic-ref','--short','HEAD'],['status','--porcelain=v1','--untracked-files=all'],['ls-tree','-r','HEAD']]:commands.append(['git','-C',str(repo),*args])
commands += [['git','diff','--no-index','--no-renames','--name-status',str(r/'base'),str(r/'head')],['git','diff','--no-index','--no-renames',str(r/'base'),str(r/'head')]]
commands += [['cat',str(r/p)] for p in ['base/legacy.py','base/api.py','head/service.py','head/api.py','probe.py']]
logs=[]
for c in commands:
 p=subprocess.run(c,text=True,capture_output=True); entry={'command':c,'stdout':p.stdout,'stderr':p.stderr,'exit_code':p.returncode};logs.append(entry);print(json.dumps(entry))
(out/'inspection.json').write_text(json.dumps(logs,indent=2))
