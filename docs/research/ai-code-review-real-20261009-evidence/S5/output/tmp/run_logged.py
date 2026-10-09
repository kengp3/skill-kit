import subprocess,json,sys,pathlib
out=pathlib.Path(__file__).resolve().parents[1]
name=sys.argv[1]; argv=sys.argv[2:]
r=subprocess.run(argv,capture_output=True,text=True)
(out/(name+'.json')).write_text(json.dumps({'command':argv,'stdout':r.stdout,'stderr':r.stderr,'exit_code':r.returncode},indent=2))
print(r.stdout,end=''); print(r.stderr,end='',file=sys.stderr); sys.exit(r.returncode)
