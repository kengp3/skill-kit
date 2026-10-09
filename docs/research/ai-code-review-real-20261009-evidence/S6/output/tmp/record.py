import subprocess,json,sys,pathlib,datetime
root=pathlib.Path('/private/tmp/ai-review-real-20261009/S6/output')
name=sys.argv[1]; cmd=sys.argv[2:]
p=subprocess.run(cmd,capture_output=True,text=True)
(root/'logs'/f'{name}.json').write_text(json.dumps({'command':cmd,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stdout':p.stdout,'stderr':p.stderr,'exit_code':p.returncode},ensure_ascii=False,indent=2))
print(p.stdout,end='');print(p.stderr,end='',file=sys.stderr);print('EXIT',p.returncode)
