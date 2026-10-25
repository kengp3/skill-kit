"""Maintainer-only native interrupt/recovery canary, not a product dependency."""
import hashlib,json,os,re,selectors,shlex,shutil,subprocess,tempfile,time,uuid
from pathlib import Path

OUT=Path(__file__).resolve().parent
CANDIDATE=Path('/private/tmp/unified-review-final-0.3.0')
CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
BASE=Path('/Users/kengp3/.codex')
TOKEN='UNIFIED_NATIVE_STOP_'+uuid.uuid4().hex
CANARY=f"printf '{TOKEN}\\n'; /bin/sleep 20; :"
EXPECTED=['/bin/sh','-c',CANARY]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def contract(path):return json.loads(re.search(r'```json\s*(.*?)```',path.read_text(),re.S)[1])
def canary_event(msg,tid,turn):
 p=msg.get('params',{});i=p.get('item',{})
 if msg.get('method')!='item/started' or p.get('threadId')!=tid or p.get('turnId')!=turn:return False
 if i.get('type')!='commandExecution' or i.get('status')!='inProgress':return False
 try:
  args=shlex.split(i.get('command',''))
  if len(args)==3 and args[0]in('/bin/zsh','/bin/bash','/bin/sh')and args[1]in('-lc','-c'):
   inner=shlex.split(args[2])
   if inner==EXPECTED:return True
  return args==EXPECTED
 except ValueError:return False

def self_check():
 base={'method':'item/started','params':{'threadId':'t','turnId':'u','item':{'type':'commandExecution','status':'inProgress','command':shlex.join(EXPECTED)}}}
 assert canary_event(base,'t','u')
 wrapped=json.loads(json.dumps(base));wrapped['params']['item']['command']=shlex.join(['/bin/zsh','-lc',shlex.join(EXPECTED)])
 assert canary_event(wrapped,'t','u')
 for method,tid,turn in [('item/completed','t','u'),('item/started','other','u'),('item/started','t','other')]:
  bad=json.loads(json.dumps(base));bad['method']=method
  assert not canary_event(bad,tid,turn)
 bad=json.loads(json.dumps(base));bad['params']['item']['command']='echo '+TOKEN
 assert not canary_event(bad,'t','u')


def processes(prior=()):
 r=subprocess.run(['/bin/ps','-axo','pid=,ppid=,args='],capture_output=True,text=True,check=True,timeout=2)
 items=[]
 for line in r.stdout.splitlines():
  parts=line.strip().split(None,2)
  if len(parts)==3:
   items.append({'pid':int(parts[0]),'ppid':int(parts[1]),'command':parts[2]})
 parents=[x for x in items if TOKEN in x['command'] and ('/bin/sh -c' in x['command'] or '/bin/zsh -lc' in x['command'])]
 ids={x['pid']for x in parents}
 known={x['pid']:x['command']for x in prior}
 selected=parents+[x for x in items if (x['ppid']in ids and re.search(r'(?:^|/)sleep 20$',x['command']))or known.get(x['pid'])==x['command']]
 return list({x['pid']:x for x in selected}.values())

class Server:
 def __init__(self,project,env,label):
  self.label=label;self.project=project;self.buffer=b'';self.rid=0;self.replies={};self.events=[];self.closed=False
  self.log=(OUT/f'{label}-rpc.jsonl').open('x');self.stderr=(OUT/f'{label}-server.stderr').open('x')
  self.process=subprocess.Popen([str(CODEX),'app-server','--stdio'],cwd=project,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,start_new_session=True)
  self.sel=selectors.DefaultSelector();self.sel.register(self.process.stdout,selectors.EVENT_READ)
 def emit(self,kind,msg):self.log.write(json.dumps({'at':time.time(),kind:msg},ensure_ascii=False)+'\n');self.log.flush()
 def send(self,method,params):
  self.rid+=1;msg={'id':self.rid,'method':method,'params':params};self.emit('request',msg)
  self.process.stdin.write((json.dumps(msg)+'\n').encode());self.process.stdin.flush();return self.rid
 def pump(self,wait=.15):
  if b'\n'not in self.buffer:
   if not self.sel.select(wait):return
   chunk=os.read(self.process.stdout.fileno(),65536)
   if not chunk:raise RuntimeError('owned server EOF')
   self.buffer+=chunk
  while b'\n'in self.buffer:
   line,self.buffer=self.buffer.split(b'\n',1)
   if not line:continue
   msg=json.loads(line)
   if 'id'in msg and ('result'in msg or 'error'in msg):self.replies[msg['id']]=msg;self.emit('response',msg)
   elif 'id'in msg:
    self.emit('server_request',msg);params=msg.get('params',{});method=msg.get('method','')
    # Only this owned project can receive approvals; unknown app/network requests fail closed.
    if method=='item/commandExecution/requestApproval':
     command=params.get('command','');cwd=params.get('cwd')
     allowed=cwd==str(self.project)and not any(x in command for x in ('auth.json','/Users/','curl ','wget ','brew ','npm ','pip ','rm -rf'))
     reply={'id':msg['id'],'result':{'decision':'accept'if allowed else'decline'}}
    elif method=='item/fileChange/requestApproval':
     root=params.get('grantRoot');allowed=root is None or Path(root).resolve().is_relative_to(self.project.resolve())
     reply={'id':msg['id'],'result':{'decision':'accept'if allowed else'decline'}}
    else:reply={'id':msg['id'],'error':{'code':-32601,'message':'No unrelated interactive tools authorized in this canary'}}
    self.process.stdin.write((json.dumps(reply)+'\n').encode());self.process.stdin.flush();self.emit('client_response',reply)
   else:self.events.append(msg);self.emit('event',msg)
 def call(self,method,params,timeout=30):
  rid=self.send(method,params);deadline=time.monotonic()+timeout
  while rid not in self.replies and time.monotonic()<deadline:self.pump()
  if rid not in self.replies:raise TimeoutError(method+' result unknown; no retry')
  msg=self.replies.pop(rid)
  if 'error'in msg:raise RuntimeError(method+': '+json.dumps(msg['error']))
  return msg['result']
 def initialize(self):
  self.call('initialize',{'clientInfo':{'name':'unified_native_stop','version':'1.0'},'capabilities':{'experimentalApi':True}})
  self.process.stdin.write(b'{"method":"initialized","params":{}}\n');self.process.stdin.flush()
 def start_thread(self):
  return self.call('thread/start',{'cwd':str(self.project),'runtimeWorkspaceRoots':[str(self.project)],'sandbox':'workspace-write','approvalPolicy':'on-request','ephemeral':False,'model':'gpt-6.1-sol','config':{'model_reasoning_effort':'low','web_search':'disabled'}})
 def turn(self,tid,prompt):
  return self.call('turn/start',{'threadId':tid,'input':[{'type':'text','text':prompt},{'type':'skill','name':'task-harness','path':str(self.project/'.agents/skills/task-harness/SKILL.md')} ]})['turn']['id']
 def terminal(self,tid,turn):
  for e in self.events:
   p=e.get('params',{})
   if e.get('method')=='turn/completed'and p.get('threadId')==tid and p.get('turn',{}).get('id')==turn:return p['turn']
 def close(self):
  if self.closed:return {}
  self.closed=True;pid=self.process.pid
  self.process.stdin.close()
  try:self.process.wait(timeout=10)
  except subprocess.TimeoutExpired:self.process.terminate();self.process.wait(timeout=5)
  self.sel.close();self.log.close();self.stderr.close()
  try:os.kill(pid,0);absent=False
  except ProcessLookupError:absent=True
  return {'pid':pid,'exit_code':self.process.returncode,'absent':absent}

self_check()
assert digest(CANDIDATE/'runtime-manifest.json')=='7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'
before={n:digest(BASE/n)for n in ('config.toml','auth.json')}
summary={'candidate_manifest_sha256':digest(CANDIDATE/'runtime-manifest.json'),'token':TOKEN,'self_check':'passed','status':'preparing'}
servers=[]
with tempfile.TemporaryDirectory(prefix='unified-native-stop-',dir='/private/tmp')as tmp:
 root=Path(tmp);state=root/'state';project=root/'project';state.mkdir(mode=0o700);project.mkdir()
 shutil.copyfile(BASE/'auth.json',state/'auth.json');(state/'auth.json').chmod(0o600)
 (state/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = false\napps = false\nplugins = false\n[projects.'+json.dumps(str(project))+']\ntrust_level = "trusted"\n')
 env=os.environ.copy();env['CODEX_HOME']=str(state)
 for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):env.pop(key,None)
 for name in ('project-setting','define-task','task-harness','ai-code-review'):
  shutil.copytree(CANDIDATE/'skills'/name,project/'.agents/skills'/name,ignore=shutil.ignore_patterns('scripts','__pycache__'))
 (project/'docs/plans').mkdir(parents=True);(project/'docs/research').mkdir()
 (project/'ledger.txt').write_text('EXISTING_ONCE\n');(project/'preserve.txt').write_text('KEEP_EXISTING_CONTENT\n')
 (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| research | 證據 | docs/research/{slug}.research.md |\n| task-contract | 合約 | docs/plans/{slug}.task-contract.md |\n| hook-receipt | 收據 | docs/research/{slug}.hook-receipt.md |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n')
 cp=project/'docs/plans/native-stop.task-contract.md'
 data={'schema_version':1,'task_id':'native-stop','project_root':str(project),'owner_session_id':None,'status':'in_progress','objective':'保留一次ledger成果並產出STOP_RESUMED_OK','scope':['保留ledger與preserve','使用同一任務合約','本次canary前景命令僅供原生停止驗證'],'requirements':[{'id':'T1','outcome':'ledger.txt精確EXISTING_ONCE一行','status':'done','depends_on':[],'evidence':['既有fixture成果，續作先核對實際檔案']},{'id':'T2','outcome':'docs/research/stop-result.research.md精確STOP_RESUMED_OK一行','status':'pending','depends_on':['T1'],'evidence':[]}],'authorization':{'user_turn_id':None,'mode':'wait','basis':'預置部分完成狀態；須本回合實際授權'},'recovery':{'next_action':'核對既有成果、保存授權，再進行canary與T2','blockers':[],'unknown_operations':[],'cancellation_reason':''}}
 cp.write_text('# 任務合約：原生停止\n\n<!-- task-harness-contract:v1 -->\n```json\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n```\n<!-- /task-harness-contract -->\n')
 shutil.copytree(project,OUT/'initial',ignore=shutil.ignore_patterns('.agents'))
 try:
  s=Server(project,env,'original');servers.append(s);s.initialize();info=s.start_thread();tid=info['thread']['id'];summary['original_thread']=tid
  prompt=f'''使用 task-harness 接續同一份 docs/plans/native-stop.task-contract.md；這個 cwd 是已確認專案根目錄。本回合明確授權執行：先核對 ledger.txt 的既有一次成果與 preserve.txt，將目前授權／進度成功保存並讀回原合約。然後用原生命令工具執行下面這一個獨立前景命令，勿與任何其他命令或寫入批次合併：\n{shlex.join(EXPECTED)}\n此命令只是測試控制器的停止時窗，不是產品成果。只有它正常結束後才能產出 T2 的 stop-result.research.md 精確一行 STOP_RESUMED_OK。勿提前產出 T2。保留既有 ledger 一次寫入與 preserve，不另建合約、不派子 agent、不改全域或 hooks 設定、不安裝 runtime。此環境 hooks 刻意停用，使用模型主動檢查；使用者 Stop 必須立即服從，不為補寫合約繼續。可觀測 thread ID 為 {tid}；其他宿主 ID 不可取得就留 null 並說明，不虛構。'''
  (OUT/'prompt-original.txt').write_text(prompt);turn=s.turn(tid,prompt);summary['original_turn']=turn;deadline=time.monotonic()+600;interrupt=False;marker=None
  while time.monotonic()<deadline:
   s.pump()
   if marker is None:
    marker=next((e for e in s.events if canary_event(e,tid,turn)),None)
   if marker is not None and not interrupt:
    ended=any(e.get('method')=='item/completed'and e.get('params',{}).get('item',{}).get('id')==marker['params']['item']['id']for e in s.events)
    if ended:raise RuntimeError('canary completed before interruption; window missed')
    members=processes()
    if any(re.search(r'(?:^|/)sleep 20$',x['command'])for x in members):
     c=contract(cp);assert c['task_id']=='native-stop'and c['status']=='in_progress';assert(project/'ledger.txt').read_bytes()==b'EXISTING_ONCE\n';assert not(project/'docs/research/stop-result.research.md').exists()
     summary['command_started_event']=marker;summary['owned_canary_processes_before_interrupt']=members;summary['contract_before_interrupt']=c
     summary['interrupt_response']=s.call('turn/interrupt',{'threadId':tid,'turnId':turn});interrupt=True;summary['interrupt_request_count']=1
   terminal=s.terminal(tid,turn)
   if terminal:
    summary['original_terminal']=terminal
    assert interrupt and terminal['status']=='interrupted',terminal
    break
  else:raise TimeoutError('original turn deadline; do not replay')
  summary['original_readback']=s.call('thread/read',{'threadId':tid,'includeTurns':True})
  time.sleep(.5);summary['owned_canary_processes_initially_after_interrupt']=processes(summary['owned_canary_processes_before_interrupt'])
  stop_deadline=time.monotonic()+25
  while processes(summary['owned_canary_processes_before_interrupt'])and time.monotonic()<stop_deadline:time.sleep(.2)
  summary['owned_canary_processes_after_interrupt']=processes(summary['owned_canary_processes_before_interrupt'])
  assert not summary['owned_canary_processes_after_interrupt']
  assert not(project/'docs/research/stop-result.research.md').exists();assert(project/'ledger.txt').read_bytes()==b'EXISTING_ONCE\n'
  summary['original_server']=s.close();assert summary['original_server']['absent']
  shutil.copytree(project,OUT/'after-stop',ignore=shutil.ignore_patterns('.agents'))
  stop={'original_thread_id':tid,'original_turn_id':turn,'native_turn_status':'interrupted','interrupt_request_count':1,'original_server':summary['original_server'],'owned_canary_processes_after_interrupt':summary['owned_canary_processes_after_interrupt'],'product_after_stop_absent':True,'ledger_sha256':digest(project/'ledger.txt'),'contract_sha256':digest(cp),'command_completion':'No exit 0 inferred for interrupted item'}
  (OUT/'stop-confirmation.json').write_text(json.dumps(stop,ensure_ascii=False,indent=2));(project/'case-control').mkdir();(project/'case-control/stop-confirmation.json').write_text(json.dumps(stop,ensure_ascii=False,indent=2))
  resumed=Server(project,env,'resume');servers.append(resumed);resumed.initialize();newinfo=resumed.start_thread();newtid=newinfo['thread']['id'];summary['resume_thread']=newtid
  prompt2=f'''明確授權使用 task-harness 接續同一任務 docs/plans/native-stop.task-contract.md。cwd 是相同且已確認的專案根目錄。前回合已收到真正原生 turn/interrupt 並為 interrupted；原 server 已結束且受控前景命令不再存在，證據在 case-control/stop-confirmation.json，這是控制器的觀測，不是新授權來源。請先核對實際 ledger、preserve、合約與未知操作／先前執行者，成功保存接手及本次授權後才完成 T2。canary 只是停止測試時窗，本回合不再執行它，不把中斷命令視為成功；必要產品成果仍為 STOP_RESUMED_OK 一行，ledger 必須保持 EXISTING_ONCE 一行，不另建合約、不重做既有寫入。不派子 agent、不更改全域或 hooks 設定，不安裝工具。可觀測的新 thread ID 為 {newtid}，其餘 ID 無法觀測時誠實留 null。完成後讀回核對合約與成果。'''
  (OUT/'prompt-resume.txt').write_text(prompt2);newturn=resumed.turn(newtid,prompt2);summary['resume_turn']=newturn;deadline=time.monotonic()+600
  while time.monotonic()<deadline:
   resumed.pump();terminal=resumed.terminal(newtid,newturn)
   if terminal:summary['resume_terminal']=terminal;assert terminal['status']=='completed',terminal;break
  else:raise TimeoutError('resume turn deadline; no blind retry')
  summary['resume_readback']=resumed.call('thread/read',{'threadId':newtid,'includeTurns':True});summary['resume_server']=resumed.close()
  final=contract(cp)
  assert final['task_id']=='native-stop'and final['status']=='done'
  assert len(list((project/'docs/plans').glob('*.task-contract.md')))==1
  assert(project/'docs/research/stop-result.research.md').read_bytes()==b'STOP_RESUMED_OK\n'
  assert(project/'ledger.txt').read_bytes()==b'EXISTING_ONCE\n'
  assert(project/'preserve.txt').read_bytes()==b'KEEP_EXISTING_CONTENT\n'
  assert not final['recovery']['unknown_operations']
  summary['final_contract']=final;summary['status']='passed';summary['assertions']={'actual_started_and_os_process_observed':True,'native_interrupted':True,'owned_original_server_reaped':True,'no_product_after_stop':True,'same_contract_task_id':True,'explicit_resume_completed':True,'ledger_once':True,'preserve_unchanged':True,'unknown_operations_reconciled':True}
 except Exception as exc:
  summary['status']='incomplete';summary['error']=repr(exc)
  # Stop only an identified active turn on this owned server; never launch a replacement.
  if servers and servers[-1].process.poll()is None:
   try:
    active_tid=summary.get('resume_thread',summary.get('original_thread'));active_turn=summary.get('resume_turn',summary.get('original_turn'))
    if active_tid and active_turn and not servers[-1].terminal(active_tid,active_turn):summary['cleanup_interrupt']=servers[-1].call('turn/interrupt',{'threadId':active_tid,'turnId':active_turn},10)
   except Exception as cleanup:summary['cleanup_error']=repr(cleanup)
 finally:
  summary['servers']=[s.close()for s in servers]
  shutil.copytree(project,OUT/'final',ignore=shutil.ignore_patterns('.agents'))
  summary['global_config_auth_unchanged']=all(digest(BASE/n)==v for n,v in before.items())
  summary['temporary_credentials_deleted_on_exit']=True
  contexts=[]
  for fp in (state/'sessions').rglob('*.jsonl'):
   for line in fp.read_text().splitlines():
    try:e=json.loads(line)
    except ValueError:continue
    if e.get('type')=='turn_context':
     d=e.get('payload',{});contexts.append({'session_log':str(fp.relative_to(state)),'timestamp':e.get('timestamp'),'model':d.get('model'),'effort':d.get('effort'),'turn_id':d.get('turn_id')})
  (OUT/'session-contexts.json').write_text(json.dumps(contexts,ensure_ascii=False,indent=2))
  (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({'status':summary['status'],'error':summary.get('error'),'global_unchanged':summary['global_config_auth_unchanged']}),flush=True)
