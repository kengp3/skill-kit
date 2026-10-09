from pathlib import Path
import shutil,json,subprocess,sys,os,datetime
R=Path('/private/tmp/ai-review-real-20261009')
original=json.loads((R/'oracle-execution.json').read_text())['logs']
changes={
 'S3':('paging.py','[:limit + 1]','[:limit]'),
 'S4':('policy.py','now <= expires','now < expires'),
 'S6':('service.py',"    state['stock'] -= count\n","    state['stock'] -= count\n    state['events'].append({'key': key, 'count': count})\n")}
results={}
for case,(file,old,new) in changes.items():
 root=R/'solution-poc'/case
 shutil.copytree(R/case/'head',root)
 source=root/file;text=source.read_text();assert text.count(old)==1
 source.write_text(text.replace(old,new))
 argv=original[case]['head']['argv']
 env=dict(os.environ,PYTHONPATH=str(root),PYTHONDONTWRITEBYTECODE='1')
 p=subprocess.run(argv,cwd=R,env=env,text=True,capture_output=True,timeout=10)
 assert p.returncode==0,p.stderr
 rows=json.loads(p.stdout); failures=[r for r in rows if r[1]!=r[2]]
 assert not failures,(case,failures)
 assert original[case]['head']['mismatches']>0
 results[case]={'scope':'fixture-only proposed fix; no skill or reviewed-source mutation','changed_file':str(source),'replacement':{'old':old,'new':new},'argv':argv,'cwd':str(R),'PYTHONPATH':str(root),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'checks':len(rows),'before_failures':original[case]['head']['mismatches'],'after_failures':len(failures)}
(R/'solution-poc.json').write_text(json.dumps({'executed_at':datetime.datetime.now().astimezone().isoformat(),'results':results},ensure_ascii=False,indent=2))
print(json.dumps({c:{k:v[k] for k in ['checks','before_failures','after_failures']} for c,v in results.items()},indent=2))
