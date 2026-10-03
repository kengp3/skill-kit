"""One-shot archive after all preregistered runs terminate. No behavioral verdict."""
import hashlib, importlib.util, json, shutil, subprocess, sys
from pathlib import Path
here=Path(__file__).resolve().parent
repo=here.parents[2]
matrix=json.loads((here/'matrix.json').read_text());workspace=Path(matrix['workspace'])
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('trace_export',repo/'docs/research/task-harness-revalidation2-20261003-evidence/export_traces.py')
export=importlib.util.module_from_spec(spec);spec.loader.exec_module(export)
export.PREFIXES=tuple(r['actor'] for r in matrix['runs'])
sessions=Path('/Users/kengp3/.codex/sessions/2026/10/03')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):(here/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
assert not (here/'archive').exists(),'Do not overwrite a completed archive'
(here/'native-traces').mkdir(exist_ok=True)
manifest=[];models=[];lifecycle=[];commands=[];verification=[]
for path in sorted(sessions.glob('*.jsonl')):
 with path.open() as f:
  first=f.readline();meta=json.loads(first).get('payload',{});actor=meta.get('agent_path','')
  if not any(actor==p or actor.startswith(p+'/') for p in export.PREFIXES):continue
  lines=[first,*f.readlines()]
 trace=export.select(lines)
 name=actor.removeprefix('/root/').replace('/','--')+'.json'
 trace['source_file']=str(path)
 # Keep only raw tool/identity/lifecycle rows, excluding internal reasoning and unrelated messages.
 rawname=name.removesuffix('.json')+'.json'
 rawdir=here/'native-raw';rawdir.mkdir(exist_ok=True)
 selected = {}
 for number, raw in enumerate(lines, 1):
  row=json.loads(raw);payload=row.get('payload',{})
  if row['type'] in ('session_meta','turn_context') or (row['type']=='response_item' and payload.get('type') in export.CALLS | export.OUTPUTS) or (row['type']=='event_msg' and payload.get('type') in ('task_started','task_complete','item_started','item_completed','token_count')):
   selected[str(number)]=raw
 (rawdir/rawname).write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
 trace['archived_raw']='native-raw/'+rawname
 for e in trace['events']:
  row=json.loads(lines[e['source_line']-1]);assert hashlib.sha256(lines[e['source_line']-1].encode()).hexdigest()==e['raw_line_sha256']
  assert e['payload']=={k:row['payload'][k] for k in e['payload']}
 save('native-traces/'+name,trace)
 contexts=[];observations=[]
 for n,line in enumerate(lines,1):
  row=json.loads(line);p=row.get('payload',{});provenance={'source_line':n,'raw_line_sha256':hashlib.sha256(line.encode()).hexdigest(),'timestamp':row.get('timestamp')}
  if row['type']=='turn_context':contexts.append(dict(**provenance,model=p.get('model'),effort=p.get('effort'),reasoning=p.get('reasoning_effort')))
  if row['type']=='event_msg' and p.get('type') in ('task_started','task_complete','item_started','item_completed','token_count'):
   observations.append(dict(**provenance,payload=p))
   item=p.get('item',{})
   if p['type']=='item_completed' and item.get('type')=='CommandExecution':commands.append(dict(actor=actor,source_file=str(path),**provenance,item=item))
 expected=next(r['model'] for r in matrix['runs'] if actor==r['actor'] or actor.startswith(r['actor']+'/'))
 terminal=any(o['payload']['type']=='task_complete' for o in observations)
 verification.append(dict(actor=actor,model_matches=bool(contexts) and {c['model'] for c in contexts}=={expected},terminal=terminal))
 manifest.append(dict(actor=actor,file=name,events=len(trace['events'])))
 models.append(dict(actor=actor,contexts=contexts));lifecycle.append(dict(actor=actor,observations=observations))
save('native-traces/manifest.json',manifest);save('model-observation.json',models);save('lifecycle-observation.json',lifecycle);save('commands.json',commands)
save('trace-verification.json',dict(actors=len(manifest),tool_events=sum(x['events'] for x in manifest),raw_hashes_and_retained_projection_match=True,observations=verification))
assert all(v['terminal'] for v in verification),'A running actor cannot be archived as complete'
checks=[];protected=[];receipts=[]
for run in matrix['runs']:
 src=Path(run['project']).parent;dest=here/'archive'/run['id']
 shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__'))
 changed=[f for f in run['protected'] if not (src/f).is_file() or sha(src/f)!=run['baseline'][f]]
 protected.append(dict(run=run['id'],changed=changed))
 argv=[sys.executable,'-B','check.py'];result=subprocess.run(argv,cwd=dest/'project',capture_output=True,text=True,timeout=20)
 checks.append(dict(run=run['id'],argv=argv,cwd=str(dest/'project'),returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
 for p in (dest/'project'/'evidence').rglob('*.json'):
  try:r=json.loads(p.read_text())
  except (ValueError,UnicodeError):continue
  if not isinstance(r,dict) or 'argv' not in r:continue
  versions=[]
  for name,digest in r.get('sources_after',{}).items():
   try:rel=Path(name).relative_to(src);current=sha(dest/rel);valid=current==digest
   except (ValueError,FileNotFoundError):rel=Path(name);valid=False
   versions.append(dict(source=str(rel),matches_current=valid))
  receipts.append(dict(run=run['id'],receipt=str(p.relative_to(here)),data=r,current_sources=versions))
save('artifact-checks.json',checks);save('protected-checks.json',protected);save('receipt-inventory.json',receipts)
print(json.dumps({'actors':len(manifest),'runs':len(checks),'checks_pass':sum(x['returncode']==0 for x in checks),'protected_changes':sum(len(x['changed']) for x in protected),'receipts':len(receipts)}))
