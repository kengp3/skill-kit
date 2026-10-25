"""Archive selected prior actual trials without credentials or installed skill copies."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent
CANDIDATE=Path('/private/tmp/unified-t07-integrated-0.3.0')
CASES={'A-standalone':'/private/tmp/unified-t02-A-retry','BD-nohelpers':'/private/tmp/unified-t02-B','C-migration':'/private/tmp/unified-t03-positive','C-conflict':'/private/tmp/unified-t03-conflict','E-resume':'/private/tmp/unified-E','F-prelaunch-failure':'/private/tmp/unified-F','F-independent':'/private/tmp/unified-F-persistent','G-disabled':'/private/tmp/unified-G-disabled','FG-timeout':'/private/tmp/unified-t06-G'}
summary=[]
for name,source in CASES.items():
 src=Path(source);dst=HERE/'staged'/name;dst.mkdir(parents=True,exist_ok=False)
 for filename in ('run.json','stdout.jsonl','stderr.log','session-model-contexts.json','fixture-before.json'):
  if (src/filename).is_file():shutil.copyfile(src/filename,dst/filename)
 if (src/'project').is_dir():
  shutil.copytree(src/'project',dst/'artifacts',ignore=shutil.ignore_patterns('.agents','.git'))
 run=json.loads((src/'run.json').read_text())
 differences=[]
 for path,oldhash in run.get('source_files',{}).items():
  rel=path.removeprefix('.agents/')
  current=CANDIDATE/rel
  if not current.is_file()or hashlib.sha256(current.read_bytes()).hexdigest()!=oldhash:differences.append(rel)
 files={str(f.relative_to(dst)):hashlib.sha256(f.read_bytes()).hexdigest()for f in dst.rglob('*')if f.is_file()}
 (dst/'archive-manifest.json').write_text(json.dumps(files,ensure_ascii=False,sort_keys=True,indent=2))
 summary.append({'case':name,'original_path':str(src),'exit_code':run.get('exit_code'),'source':run.get('source'),'source_differences_from_2fbb_candidate':differences,'global_auth_unchanged':run.get('global_auth_unchanged'),'raw_files':len(files)})
(HERE/'staged-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
