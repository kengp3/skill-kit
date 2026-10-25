"""Maintainer-only native lifecycle acceptance; never a product runtime dependency."""
import argparse, hashlib, json, os, selectors, shutil, subprocess, tempfile, time
from pathlib import Path

CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
CANDIDATE=Path('/private/tmp/unified-review-final-0.3.0')
BASE=Path('/Users/kengp3/.codex')
EVIDENCE=Path(__file__).resolve().parent
SKILLS=('define-task','project-setting','task-harness','ai-code-review')

class Native:
 def __init__(self,project,state,out):
  self.project=project;self.out=out;self.records=[];self.buffer=b'';self.counter=0
  self.stderr=(out/'server.stderr.log').open('w');self.raw=(out/'rpc.jsonl').open('w')
  env=os.environ.copy();env['CODEX_HOME']=str(state)
  for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):env.pop(key,None)
  self.proc=subprocess.Popen([str(CODEX),'app-server','--stdio'],cwd=project,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr)
  self.sel=selectors.DefaultSelector();self.sel.register(self.proc.stdout,selectors.EVENT_READ)
  self.rpc('initialize',{'clientInfo':{'name':'unified_model_lifecycle','version':'1.0'},'capabilities':{'experimentalApi':True}})
  self.send({'method':'initialized','params':{}})
 def log(self,direction,message):
  rec={'direction':direction,'message':message};self.records.append(rec);self.raw.write(json.dumps(rec,ensure_ascii=False)+'\n');self.raw.flush()
 def send(self,message):
  self.log('client',message);self.proc.stdin.write((json.dumps(message)+'\n').encode());self.proc.stdin.flush()
 def read(self,timeout):
  deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   if b'\n' in self.buffer:
    line,self.buffer=self.buffer.split(b'\n',1)
    if not line:continue
    msg=json.loads(line);self.log('server',msg)
    if 'id' in msg and 'method' in msg:
     self.send({'id':msg['id'],'error':{'code':-32601,'message':'Lifecycle probe does not provide interactive user authorization'}})
    return msg
   for key,_ in self.sel.select(min(.2,max(0,deadline-time.monotonic()))):
    data=os.read(key.fd,65536)
    if not data:raise RuntimeError('native server EOF')
    self.buffer+=data
  raise TimeoutError('native event wait')
 def rpc(self,method,params,timeout=60):
  self.counter+=1;rid=self.counter;self.send({'id':rid,'method':method,'params':params});deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   msg=self.read(max(.1,deadline-time.monotonic()))
   if msg.get('id')==rid:
    if 'error' in msg:raise RuntimeError(json.dumps(msg,ensure_ascii=False))
    return msg.get('result')
  raise TimeoutError(method)
 def thread(self,model='gpt-6.1-sol',effort='low'):
  return self.rpc('thread/start',{'cwd':str(self.project),'model':model,'ephemeral':False,'sandbox':'workspace-write','approvalPolicy':'on-request','approvalsReviewer':'auto_review','config':{'model_reasoning_effort':effort}})
 def turn(self,thread,prompt,model=None,effort=None,timeout=900):
  params={'threadId':thread,'input':[{'type':'text','text':prompt}]}
  if model:params['model']=model
  if effort:params['effort']=effort
  result=self.rpc('turn/start',params);turn=result['turn']['id'];deadline=time.monotonic()+timeout
  (self.out/'live.json').write_text(json.dumps({'pid':self.proc.pid,'thread':thread,'turn':turn,'model_override':model,'effort_override':effort}))
  while time.monotonic()<deadline:
   msg=self.read(max(.1,deadline-time.monotonic()))
   if msg.get('method')=='turn/completed' and msg.get('params',{}).get('threadId')==thread and msg['params'].get('turn',{}).get('id')==turn:
    return msg['params']['turn']
  raise TimeoutError('turn did not reach terminal state')
 def close(self):
  self.proc.stdin.close()
  try:self.proc.wait(timeout=10)
  except subprocess.TimeoutExpired:self.proc.terminate();self.proc.wait(timeout=10)
  self.sel.close();self.raw.close();self.stderr.close()
  return self.proc.returncode

def settings(default=True):
 return '# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| research | 證據 | docs/research/{slug}.research.md |\n| task-contract | 合約 | docs/plans/{slug}.task-contract.md |\n| hook-receipt | 收據 | docs/research/{slug}.hook-receipt.md |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n'+('| model.default | [gpt-6.1-sol;low] |\n' if default else '')

def contexts(state):
 result=[]
 for fp in (state/'sessions').rglob('*.jsonl'):
  for line in fp.read_text().splitlines():
   try:event=json.loads(line)
   except ValueError:continue
   data=event.get('payload',{})
   if event.get('type')=='session_meta':result.append({'type':'session_meta','file':str(fp.relative_to(state)),'id':data.get('id'),'source':data.get('source'),'timestamp':event.get('timestamp')})
   elif event.get('type')=='turn_context':result.append({'type':'turn_context','file':str(fp.relative_to(state)),'turn_id':data.get('turn_id'),'model':data.get('model'),'effort':data.get('effort'),'timestamp':event.get('timestamp')})
 return result

def run(case):
 out=EVIDENCE/case;out.mkdir(exist_ok=False)
 before={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ('auth.json','config.toml')}
 manifest=json.loads((CANDIDATE/'runtime-manifest.json').read_text())
 assert all(hashlib.sha256((CANDIDATE/p).read_bytes()).hexdigest()==v for p,v in manifest['files'].items())
 summary={'case':case,'candidate_manifest_sha256':hashlib.sha256((CANDIDATE/'runtime-manifest.json').read_bytes()).hexdigest(),'turns':[]}
 with tempfile.TemporaryDirectory(prefix='unified-model-lifecycle-',dir='/private/tmp') as temp:
  root=Path(temp);state=root/'state';project=root/'project';state.mkdir(mode=0o700);project.mkdir(mode=0o700)
  shutil.copyfile(BASE/'auth.json',state/'auth.json');(state/'auth.json').chmod(0o600)
  (state/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = false\n[projects.'+json.dumps(str(project))+']\ntrust_level = "trusted"\n')
  for name in SKILLS:shutil.copytree(CANDIDATE/'skills'/name,project/'.agents/skills'/name,ignore=shutil.ignore_patterns('scripts','__pycache__'))
  (project/'preserve.txt').write_text('KEEP_EXISTING_CONTENT\n')
  (project/'project-setting.md').write_text(settings(case!='switch'))
  if case=='exhausted':
   names={'qa_bad_primary':'not-a-real-model-unified-primary','qa_bad_default':'not-a-real-model-unified-default'}
   (project/'.codex/agents').mkdir(parents=True)
   for name,model in names.items():(project/f'.codex/agents/{name}.toml').write_text(f'name = "{name}"\ndescription = "Isolated unavailable-model acceptance role"\nmodel = "{model}"\nmodel_reasoning_effort = "low"\ndeveloper_instructions = "Only read preserve.txt and report its exact content; do not change files or create agents."\n')
   (project/'project-setting.md').write_text(settings(False)+'| model.role.qa_bad_primary | [not-a-real-model-unified-primary;low, not-a-real-model-unified-primary;high] |\n| model.default | [not-a-real-model-unified-default;low, default] |\n')
  initial=(project/'project-setting.md').read_bytes();native=None
  try:
   native=Native(project,state,out);start=native.thread();tid=start['thread']['id'];summary['thread_start']=start
   common='這是已確認的專案根目錄。使用已複製的 task-harness 與其模型規則，允許保存合約及指定產物。hooks 在此隔離測試停用且不可更改；請用模型接手，不安裝工具或服務，不執行 helper scripts。保留 preserve.txt 與專案長期設定。原生 worker 用 fork_turns=none 與自足輸入。worker 工作是唯讀核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加換行，回報結果；主責保存可查證的 handle 與選擇依據，不杜撰後端模型。'
   if case=='override':
    prompts=[common+' 本次任務ID為 scoped-model，唯一合約 docs/plans/scoped-model.task-contract.md。有T1與T2兩個必要成果，各由不同獨立 worker 核對後分別產出 docs/research/override-1.research.md 與 override-2.research.md。本次任務的 worker 模型單次指定 gpt-6-sol / low，僅此任務有效，請寫入合約而不修改專案預設。本回合只授權完成T1，保存T2 pending與等待狀態後結束本回合，不提前派T2。',common+' 明確續作同一份 docs/plans/scoped-model.task-contract.md，這是同一任務；請從合約恢復並完成T2，沿用仍有效單次覆寫，保留T1，不另建合約。本回合沒有新的模型指定。',common+' 這是獨立的新任務，不是 scoped-model 續作。使用新的唯一合約 docs/plans/new-model-task.task-contract.md，只需派出一個獨立 worker 完成核對，產出 docs/research/new-model-task.research.md。沒有單次模型指定，依目前專案設定選擇。不得從舊任務承接覆寫。']
    for index,prompt in enumerate(prompts):
     if index==2:tid=native.thread()['thread']['id']
     turn=native.turn(tid,prompt);summary['turns'].append({'phase':index+1,'thread':tid,'turn':turn});shutil.copytree(project,out/f'artifacts-phase{index+1}',ignore=shutil.ignore_patterns('.agents','.git'))
     print(json.dumps({'case':case,'phase':index+1,'status':turn.get('status')}),flush=True)
   elif case=='switch':
    phase1=common+' 任務ID為 manual-switch，唯一合約 docs/plans/manual-switch.task-contract.md。專案沒有模型預設，這次也不指定任何 worker 模型或強度。先建立一個名稱 old_worker 的原生 worker，讓它先報告已開始，然後在本專案內等待 gate-old.txt 出現後才完成 preserve.txt 核對；等待須有600秒上限，不建立背景服務。請保存原 worker 的真實 handle與running狀態，保留T1 in_progress。這個回合不要等待它完成，也不要建立 gate-old.txt，只保存合約並等待下一個明確續作回合。'
    turn=native.turn(tid,phase1);summary['turns'].append({'phase':1,'thread':tid,'turn':turn});shutil.copytree(project,out/'artifacts-phase1',ignore=shutil.ignore_patterns('.agents','.git'))
    print(json.dumps({'case':case,'phase':1,'status':turn.get('status')}),flush=True)
    phase2=common+' 明確續作同一份 docs/plans/manual-switch.task-contract.md。測試控制器已經透過原生 turn/start 的 model 與 effort 參數，把目前主責對話選擇切換成 gpt-6-sol / medium；這是主責選擇變更，不是所有 agent 的模型覆寫。請保留原 old_worker handle與設定，不重啟或重派；先核對其存活，建立 gate-old.txt 釋放它。再建立另一個名稱 new_worker 的獨立 worker，沒有任務／角色／階段／專案模型指定，使用宿主原生繼承目前主責。兩個 worker 都完成後保存原合約並產出 docs/research/manual-switch.research.md，記錄實際可觀測結果與限制。'
    turn=native.turn(tid,phase2,model='gpt-6-sol',effort='medium');summary['turns'].append({'phase':2,'thread':tid,'turn':turn});shutil.copytree(project,out/'artifacts-phase2',ignore=shutil.ignore_patterns('.agents','.git'))
    print(json.dumps({'case':case,'phase':2,'status':turn.get('status')}),flush=True)
   else:
    prompt=common+' 本任務有互不相依的T1與T2。T1必須由獨立 worker 核對 preserve.txt，角色 qa_bad_primary 候選及專案預設如設定檔；兩個模型故意不可用，請實際用相應已註冊 qa_bad_primary 與 qa_bad_default 原生角色取得真實失敗，確認原 handle 終態後才前進，不將 fixed role 模型強行覆寫。同模型重複列不可重試，default不可遞迴或在專案預設失敗後擅加主責作候選。T1所有候選不可用時保留未完成並詢問；不要用主責自我檢查滿足T1。T2不要求 worker 或特定模型，由主責直接產出 docs/research/independent-ready.research.md 精確一行 READY_WORK_DONE，完成後讀回。保存唯一合約 docs/plans/exhausted.task-contract.md、真實失敗與嘗試次數。T2不依賴T1，不可一起暫停。'
    turn=native.turn(tid,prompt);summary['turns'].append({'phase':1,'thread':tid,'turn':turn});shutil.copytree(project,out/'artifacts',ignore=shutil.ignore_patterns('.agents','.git'))
    print(json.dumps({'case':case,'phase':1,'status':turn.get('status')}),flush=True)
  except Exception as exc:
   summary['error']=str(exc);shutil.copytree(project,out/'artifacts-error',ignore=shutil.ignore_patterns('.agents','.git'),dirs_exist_ok=True)
   print(json.dumps({'case':case,'error':str(exc)}),flush=True)
  finally:
   if native:summary['owned_server_exit']=native.close()
   (out/'session-contexts.json').write_text(json.dumps(contexts(state),ensure_ascii=False,indent=2))
   summary['settings_unchanged']=(project/'project-setting.md').read_bytes()==initial
   summary['preserve_unchanged']=(project/'preserve.txt').read_bytes()==b'KEEP_EXISTING_CONTENT\n'
   summary['global_unchanged']=all(hashlib.sha256((BASE/n).read_bytes()).hexdigest()==v for n,v in before.items())
   (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 summary['temporary_credentials_deleted_on_exit']=not root.exists()
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 return summary

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('case',choices=['override','switch','exhausted']);args=parser.parse_args();run(args.case)
