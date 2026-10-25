"""Maintainer-only local install/upgrade/load probe; does not start a model."""
import hashlib,json,os,selectors,shutil,subprocess,tempfile,time
from pathlib import Path
SOURCE=Path('/private/tmp/simple-skills-unified-t07')
OUT=SOURCE/'docs/research/unified-project-settings-package-evidence'
OUT.mkdir(exist_ok=False)
ROOT=Path(tempfile.mkdtemp(prefix='unified-t07-native-',dir='/private/tmp'))
STATE=ROOT/'state';PROJECT=ROOT/'project';CATALOG=ROOT/'catalog';OLD=ROOT/'old-source';CANDIDATE=ROOT/'candidate-0.3.0'
for d in (STATE,PROJECT,CATALOG,OLD):d.mkdir()
(STATE/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = true\n[analytics]\nenabled = false\n')
ENV=os.environ.copy();ENV['CODEX_HOME']=str(STATE)
for k in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):ENV.pop(k,None)
CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
BASE=Path('/Users/kengp3/.codex')
BEFORE={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ('config.toml','auth.json')}
def command(label,args,cwd=PROJECT,env=ENV):
 r=subprocess.run([str(x)for x in args],cwd=cwd,env=env,capture_output=True,text=True,timeout=45)
 record={'args':[str(x)for x in args],'cwd':str(cwd),'state':str(STATE),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 (OUT/(label+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 assert r.returncode==0,(label,r.stderr)
 return r
# Export the frozen old source without changing its checkout or release.
a=subprocess.run(['git','archive','c7c769b','scripts/package_harness.py','packaging','skills'],cwd=SOURCE,stdout=subprocess.PIPE,check=True)
subprocess.run(['tar','-xf','-','-C',str(OLD)],input=a.stdout,check=True)
command('build-new',['python3','-B',SOURCE/'scripts/package_harness.py',CANDIDATE])
command('verify-new',['python3','-B',SOURCE/'scripts/package_harness.py','--verify',CANDIDATE])
command('build-old',['python3','-B',OLD/'scripts/package_harness.py',ROOT/'candidate-0.2.1'])
(CATALOG/'.agents/plugins').mkdir(parents=True);(CATALOG/'plugins').mkdir()
shutil.copytree(ROOT/'candidate-0.2.1',CATALOG/'plugins/kengp3-harness-0.2.1')
shutil.copytree(CANDIDATE,CATALOG/'plugins/kengp3-harness-0.3.0')
def catalog(version):
 d={'name':'unified-t07-local','plugins':[{'name':'kengp3-harness','source':{'source':'local','path':'./plugins/kengp3-harness-'+version},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Productivity'}]}
 (CATALOG/'.agents/plugins/marketplace.json').write_text(json.dumps(d,indent=2)+'\n')
def rpc_snapshot(label,version):
 records=[];buffer=b'';rid=0
 with (OUT/(label+'-server.stderr')).open('w')as err:
  process=subprocess.Popen([str(CODEX),'app-server','--stdio'],cwd=PROJECT,env=ENV,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
  sel=selectors.DefaultSelector();sel.register(process.stdout,selectors.EVENT_READ)
  def rpc(method,params):
   nonlocal buffer,rid
   rid+=1;req={'id':rid,'method':method,'params':params};process.stdin.write((json.dumps(req)+'\n').encode());process.stdin.flush();deadline=time.monotonic()+20
   while time.monotonic()<deadline:
    while b'\n'in buffer:
     line,buffer=buffer.split(b'\n',1)
     if not line:continue
     msg=json.loads(line)
     if msg.get('id')==rid:
      records.append({'request':req,'response':msg});assert 'error'not in msg,msg;return msg['result']
    for key, _ in sel.select(.1):
     data=os.read(key.fd,65536)
     if not data:raise RuntimeError('server EOF')
     buffer+=data
   raise TimeoutError(method)
  try:
   rpc('initialize',{'clientInfo':{'name':'unified_t07','version':'1.0'},'capabilities':{'experimentalApi':True}})
   process.stdin.write(b'{"method":"initialized","params":{}}\n');process.stdin.flush()
   plugin=rpc('plugin/read',{'marketplacePath':str(CATALOG/'.agents/plugins/marketplace.json'),'pluginName':'kengp3-harness'})['plugin']
   skills=rpc('skills/list',{'cwds':[str(PROJECT)],'forceReload':True})['data']
   hooks=rpc('hooks/list',{'cwds':[str(PROJECT)]})['data']
   loaded_skills=[x for row in skills for x in row['skills']if x.get('pluginId')=='kengp3-harness@unified-t07-local']
   loaded_hooks=[x for row in hooks for x in row['hooks']if x.get('pluginId')=='kengp3-harness@unified-t07-local']
   assert all(not r['errors']for r in skills)
   assert all(not r['errors']and not r['warnings']for r in hooks)
   cache=STATE/'plugins/cache/unified-t07-local/kengp3-harness'/version
   assert len(loaded_skills)==4,(len(loaded_skills),plugin)
   assert len(loaded_hooks)==3,len(loaded_hooks)
   assert all(x['enabled']and Path(x['path']).is_relative_to(cache)for x in loaded_skills)
   assert all(x['enabled']and Path(x['sourcePath']).is_relative_to(cache)for x in loaded_hooks)
   if version=='0.3.0':
    assert not(cache/'hooks/task_harness.py').exists()
    assert all('python'not in x['command']and 'task_harness.py'not in x['command']for x in loaded_hooks)
    command(label+'-verify-installed',['python3','-B',SOURCE/'scripts/package_harness.py','--verify',cache])
   return {'version':version,'cache':str(cache),'skills':[x['name']for x in loaded_skills],'hooks':[{'event':x['eventName'],'command':x['command'],'trust':x['trustStatus']}for x in loaded_hooks]}
  finally:
   (OUT/(label+'-rpc.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');sel.close();process.stdin.close()
   try:process.wait(timeout=5)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
# Native fresh 0.2.1 install then local 0.3.0 replacement through add.
catalog('0.2.1');command('marketplace-add',[CODEX,'plugin','marketplace','add',CATALOG,'--json'])
command('install-old',[CODEX,'plugin','add','kengp3-harness@unified-t07-local','--json'])
old=rpc_snapshot('loaded-old','0.2.1')
catalog('0.3.0');command('upgrade-new',[CODEX,'plugin','add','kengp3-harness@unified-t07-local','--json'])
new=rpc_snapshot('loaded-upgraded','0.3.0')
# A separate fresh state proves the new package does not need an old install.
STATE=ROOT/'fresh-state';STATE.mkdir();(STATE/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = true\n');ENV['CODEX_HOME']=str(STATE)
command('fresh-marketplace-add',[CODEX,'plugin','marketplace','add',CATALOG,'--json'])
command('fresh-install-new',[CODEX,'plugin','add','kengp3-harness@unified-t07-local','--json'])
fresh=rpc_snapshot('loaded-fresh','0.3.0')
summary={'root':str(ROOT),'candidate':str(CANDIDATE),'old':old,'upgraded':new,'fresh':fresh,'global_config_auth_unchanged':all(hashlib.sha256((BASE/n).read_bytes()).hexdigest()==v for n,v in BEFORE.items()),'model_trial_executed':False,'normal_hook_trust_verified':False}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
