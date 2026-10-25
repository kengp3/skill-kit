"""Verify the exact final candidate through isolated native plugin loading; no model."""
import argparse,hashlib,json,os,selectors,shutil,subprocess,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--old-candidate');options=p.parse_args();OUT=HERE/('final-upgrade'if options.old_candidate else 'final-loader');OUT.mkdir(exist_ok=False)
CANDIDATE=Path('/private/tmp/unified-review-final-0.3.0');EXPECTED='7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'
CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
assert hashlib.sha256((CANDIDATE/'runtime-manifest.json').read_bytes()).hexdigest()==EXPECTED
before={n:hashlib.sha256((Path('/Users/kengp3/.codex')/n).read_bytes()).hexdigest()for n in ('config.toml','auth.json')}
with tempfile.TemporaryDirectory(prefix='unified-t08-final-load-',dir='/private/tmp')as tmp:
 root=Path(tmp);state=root/'state';project=root/'project';catalog=root/'catalog'
 for d in (state,project,catalog):d.mkdir()
 (state/'config.toml').write_text('[features]\nhooks = true\n')
 (catalog/'.agents/plugins').mkdir(parents=True);(catalog/'plugins').mkdir();shutil.copytree(CANDIDATE,catalog/'plugins/kengp3-harness')
 def write_catalog(path):
  (catalog/'.agents/plugins/marketplace.json').write_text(json.dumps({'name':'unified-t08-final','plugins':[{'name':'kengp3-harness','source':{'source':'local','path':path},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Productivity'}]}))
 write_catalog('./plugins/kengp3-harness')
 if options.old_candidate:
  shutil.copytree(options.old_candidate,catalog/'plugins/old-harness');write_catalog('./plugins/old-harness')
 env=os.environ.copy();env['CODEX_HOME']=str(state)
 for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):env.pop(key,None)
 for label,args in [('marketplace',['plugin','marketplace','add',str(catalog),'--json']),('install',['plugin','add','kengp3-harness@unified-t08-final','--json'])]:
  r=subprocess.run([str(CODEX),*args],cwd=project,env=env,capture_output=True,text=True,timeout=45)
  (OUT/(label+'.json')).write_text(json.dumps({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2));assert r.returncode==0
 if options.old_candidate:
  old_cache=state/'plugins/cache/unified-t08-final/kengp3-harness/0.2.1'
  assert json.loads((old_cache/'.codex-plugin/plugin.json').read_text())['version']=='0.2.1'
  write_catalog('./plugins/kengp3-harness')
  r=subprocess.run([str(CODEX),'plugin','add','kengp3-harness@unified-t08-final','--json'],cwd=project,env=env,capture_output=True,text=True,timeout=45)
  (OUT/'upgrade.json').write_text(json.dumps({'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2));assert r.returncode==0
 records=[];buf=b'';rid=0
 with (OUT/'server.stderr').open('w')as stderr:
  proc=subprocess.Popen([str(CODEX),'app-server','--stdio'],cwd=project,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
  sel=selectors.DefaultSelector();sel.register(proc.stdout,selectors.EVENT_READ)
  def rpc(method,params):
   global rid,buf
   rid+=1;request={'id':rid,'method':method,'params':params};proc.stdin.write((json.dumps(request)+'\n').encode());proc.stdin.flush();deadline=time.monotonic()+20
   while time.monotonic()<deadline:
    while b'\n'in buf:
     raw,buf=buf.split(b'\n',1)
     if not raw:continue
     response=json.loads(raw)
     if response.get('id')==rid:
      records.append({'request':request,'response':response});assert 'error'not in response,response;return response['result']
    for key,_ in sel.select(.1):
     data=os.read(key.fd,65536)
     if not data:raise RuntimeError('server EOF')
     buf+=data
   raise TimeoutError(method)
  try:
   rpc('initialize',{'clientInfo':{'name':'unified_t08_final','version':'1.0'},'capabilities':{'experimentalApi':True}});proc.stdin.write(b'{"method":"initialized","params":{}}\n');proc.stdin.flush()
   skills=rpc('skills/list',{'cwds':[str(project)],'forceReload':True})['data'];hooks=rpc('hooks/list',{'cwds':[str(project)]})['data']
  finally:
   (OUT/'rpc.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));sel.close();proc.stdin.close()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
 cache=state/'plugins/cache/unified-t08-final/kengp3-harness/0.3.0'
 manifest=json.loads((cache/'runtime-manifest.json').read_text());assert hashlib.sha256((cache/'runtime-manifest.json').read_bytes()).hexdigest()==EXPECTED
 assert all(hashlib.sha256((cache/p).read_bytes()).hexdigest()==h for p,h in manifest['files'].items())
 ss=[s for row in skills for s in row['skills']if s.get('pluginId')=='kengp3-harness@unified-t08-final'];hh=[h for row in hooks for h in row['hooks']if h.get('pluginId')=='kengp3-harness@unified-t08-final']
 assert len(ss)==4 and len(hh)==3
 assert (cache/'skills/task-harness/assets/codex-hooks.json').read_bytes()==(cache/'hooks/hooks.json').read_bytes()
 assert not(cache/'hooks/task_harness.py').exists()
 result={'upgraded_from': '0.2.1'if options.old_candidate else None,'candidate_manifest_sha256':EXPECTED,'installed_manifest_matches':True,'skills':[s['name']for s in ss],'hooks':[{'event':h['eventName'],'command':h['command'],'trust':h['trustStatus']}for h in hh],'canonical_asset_matches_plugin_hooks':True,'global_config_auth_unchanged':all(hashlib.sha256((Path('/Users/kengp3/.codex')/n).read_bytes()).hexdigest()==v for n,v in before.items()),'model_trial':False}
 (OUT/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
