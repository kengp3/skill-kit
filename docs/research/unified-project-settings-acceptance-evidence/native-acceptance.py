"""Maintainer-only installed-candidate trials; never part of the daily skill path."""
import argparse,hashlib,json,os,selectors,shutil,subprocess,tempfile,time
from pathlib import Path

CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
CANDIDATE=Path('/private/tmp/unified-t07-integrated-0.3.0')
EVIDENCE=Path(__file__).resolve().parent
BASE=Path('/Users/kengp3/.codex')
SKILLS=['define-task','project-setting','task-harness','ai-code-review']
p=argparse.ArgumentParser();p.add_argument('case',choices=['packaged-hooks','readonly-invalid','model-policy','standalone-copy','fallback-dispatch','hook-recovery','effort-preflight','migration-resume']);p.add_argument('--candidate',default=str(CANDIDATE));a=p.parse_args();CANDIDATE=Path(a.candidate)
out=EVIDENCE/a.case;out.mkdir(exist_ok=False)
before={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ('config.toml','auth.json')}
manifest=json.loads((CANDIDATE/'runtime-manifest.json').read_text())
for name,digest in manifest['files'].items():
 assert hashlib.sha256((CANDIDATE/name).read_bytes()).hexdigest()==digest,name
hooks=json.loads((CANDIDATE/'hooks/hooks.json').read_text())['hooks']
for groups in hooks.values():
 for group in groups:
  for h in group['hooks']:
   assert h['command'].startswith('echo ')
   assert not any(c in h['command'] for c in (';','&','|','`','$','>','<','\n'))

def native(label,args,project,env,timeout=600):
 suffix='.stdout.jsonl'if label.startswith('model')else'.stdout.json'
 with (out/(label+suffix)).open('w')as stdout,(out/(label+'.stderr.log')).open('w')as stderr:
  process=subprocess.Popen([str(CODEX),*args],cwd=project,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
  try:code=process.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   process.terminate()
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
   code=None
 return {'exit_code':code,'args':args,'owned_process_terminal':process.poll() is not None}

def model_metadata(project,env):
 records=[];buffer=b'';rid=0
 with (out/'metadata-server.stderr').open('w')as stderr:
  process=subprocess.Popen([str(CODEX),'app-server','--stdio'],cwd=project,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr)
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
    for key,_ in sel.select(.1):
     data=os.read(key.fd,65536)
     if not data:raise RuntimeError('server EOF')
     buffer+=data
   raise TimeoutError(method)
  try:
   rpc('initialize',{'clientInfo':{'name':'unified_t08_effort','version':'1.0'},'capabilities':{'experimentalApi':True}});process.stdin.write(b'{"method":"initialized","params":{}}\n');process.stdin.flush();metadata=rpc('model/list',{})
  finally:
   (out/'metadata-rpc.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));sel.close();process.stdin.close()
   try:process.wait(timeout=5)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
 return metadata

with tempfile.TemporaryDirectory(prefix='unified-t08-',dir='/private/tmp')as tmp:
 root=Path(tmp);state=root/'state';project=root/'project';catalog=root/'catalog'
 for d in (state,project,catalog):d.mkdir(mode=0o700)
 shutil.copyfile(BASE/'auth.json',state/'auth.json');(state/'auth.json').chmod(0o600)
 (state/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = true\n[projects.'+json.dumps(str(project))+']\ntrust_level = "trusted"\n')
 env=os.environ.copy();env['CODEX_HOME']=str(state)
 for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):env.pop(key,None)
 (catalog/'.agents/plugins').mkdir(parents=True);(catalog/'plugins').mkdir()
 shutil.copytree(CANDIDATE,catalog/'plugins/kengp3-harness')
 (catalog/'.agents/plugins/marketplace.json').write_text(json.dumps({'name':'unified-t08-local','plugins':[{'name':'kengp3-harness','source':{'source':'local','path':'./plugins/kengp3-harness'},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Productivity'}]},indent=2))
 installs=[]
 for label,args in [('marketplace-add',['plugin','marketplace','add',str(catalog),'--json']),('install',['plugin','add','kengp3-harness@unified-t08-local','--json'])]:
  if a.case in ('standalone-copy','hook-recovery'):continue
  result=native(label,args,project,env,45);installs.append(result);assert result['exit_code']==0,result
 (project/'preserve.txt').write_text('KEEP_EXISTING_CONTENT\n')
 if a.case in ('standalone-copy','hook-recovery'):
  for name in SKILLS:
   shutil.copytree(CANDIDATE/'skills'/name,project/'.agents/skills'/name,ignore=shutil.ignore_patterns('scripts','__pycache__'))
 if a.case=='effort-preflight':
  metadata=model_metadata(project,env)
  selected=next(m for m in metadata['data']if m['model']=='gpt-6-sol')
  assert selected['defaultReasoningEffort']=='medium'and'none'not in [x['reasoningEffort']for x in selected['supportedReasoningEfforts']]
  (project/'host-model-metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
  (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| research | 證據 | docs/research/{slug}.research.md |\n| task-contract | 合約 | docs/plans/{slug}.task-contract.md |\n| hook-receipt | 收據 | docs/research/{slug}.hook-receipt.md |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n| model.stage.驗證 | [gpt-6-sol;none, gpt-6.1-sol;low] |\n')
  prompt='使用 task-harness 完成驗證階段的原生派工：依 project-setting.md 候選清單建立獨立 worker，唯讀核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加換行。host-model-metadata.json 是測試控制器剛由本次宿主 model/list 取得的原始結果；可讀取它判斷模型與強度支援，不能編造 provider 錯誤。沒有禁止強度調整的限制。依技能處理，保存原始要求、選擇理由、真實 handle、宿主可觀測結果及產物檢查到唯一合約及 docs/research/effort.research.md；不要更改長期設定、原生主責模型或安裝工具服務。worker 用新上下文與自足輸入，不得改寫 preserve.txt。'
 elif a.case=='migration-resume':
  (project/'docs/plans/harness').mkdir(parents=True);(project/'docs/research/receipts').mkdir(parents=True)
  (project/'docs/plans/harness/legacy.md').write_text('# Historical artifact\nKEEP_CONTRACT_BYTES\n')
  (project/'docs/research/receipts/old.jsonl').write_text('{"kind":"legacy"}\n')
  (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| research | 證據 | docs/research/{slug}.research.md |\n| task-contract | 合約 | docs/plans/harness/{filename} |\n| hook-receipt | 收據 | docs/research/receipts/{filename} |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n')
  (project/'harness-project.json').write_text(json.dumps({'schema_version':1,'project_root':str(project),'contract_dir':'docs/plans/harness','receipt_dir':'docs/research/receipts','host':{'session_identity':True,'user_turn_identity':True,'stop_continuation':True}},indent=2))
  prompt='使用 task-harness 接續這個已確認根目錄的設定移轉。這是預置的部分完成狀態：新 Markdown 已寫入，但舊 harness-project.json 尚在；這不是已證明發生過的 OS 中斷。請依移轉／修復流程讀回實際狀態，只補未通過的三項門檻，不重複新增規則。確認全部成立後才刪除舊檔、不留備份。明確授權在本專案由 project-setting 操作設定；docs/plans/harness/legacy.md 與 docs/research/receipts/old.jsonl 是必須逐位元組保留的歷史產物，不得搬移、改寫或當作本次可執行合約。preserve.txt 也須保留。保存真實對帳與讀回依據；不能直接沿用 host=true，不安裝 runtime 或服務。'
 elif a.case=='hook-recovery':
  (project/'.codex').mkdir()
  (project/'.codex/hooks.json').write_text(json.dumps({'hooks':{'SessionStart':[{'hooks':[{'type':'command','command':'exit 17','timeout':5},{'type':'command','command':'echo UNRELATED_SENTINEL','timeout':5}]}],'UserPromptSubmit':[{'hooks':[{'type':'command','command':'exit 17','timeout':5}]}],'Stop':[{'hooks':[{'type':'command','command':'echo {}','timeout':5}]}]}},indent=2))
  prompt='使用純複製安裝的 task-harness，這是已確認專案根目錄。任務有 T1：ledger.txt 精確一行 T1_ONCE；T2：docs/research/recovery-result.research.md 精確一行 RECOVERED_OK。唯一合約固定為 docs/plans/hook-recovery.task-contract.md。本回合只授權完成 T1 與設定／hook 修復，T2 必須等下一個明確續作回合，請保存後等待。此測試擁有 .codex/hooks.json 兩個 command=exit 17 的壞 handler，明確授權由 project-setting 移除／替換這兩項為 task-harness 自帶的標準 hooks；command=echo UNRELATED_SENTINEL 是無關 handler，必須原樣保留。保留 preserve.txt，不安裝 runtime 或服務。診斷並依規格修復，讀回設定、合約與 T1；不要重做已有寫入，不宣稱尚未觀測的信任／觸發已通過。'
 elif a.case=='standalone-copy':
  prompt='使用純複製安裝的 project-setting，指定包含 task-harness，依 task-harness 自帶的 Markdown 設定規格初始化這個已確認根目錄的專案設定與 Codex 標準 hooks。這裡沒有 plugin 安裝；只使用已複製的 skills 與各自 assets，不可依賴來源 repo 的 packaging 或任何 runtime/helper。請保留 preserve.txt，完成設定後讀回核對並報告實際來源與能力限制。這次是設定初始化，不另啟動產品開發任務。'
 elif a.case=='fallback-dispatch':
  (project/'.codex/agents').mkdir(parents=True)
  (project/'.codex/agents/unavailable_worker.toml').write_text('name = "unavailable_worker"\ndescription = "A worker role whose first model is intentionally unavailable for an isolated fallback acceptance test"\nmodel = "not-a-real-model-for-unified-test"\nmodel_reasoning_effort = "low"\ndeveloper_instructions = "Read preserve.txt and report whether it exactly equals KEEP_EXISTING_CONTENT plus one newline. Do not change files, create agents, or install tools."\n')
  (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| research | 證據 | docs/research/{slug}.research.md |\n| task-contract | 合約 | docs/plans/{slug}.task-contract.md |\n| hook-receipt | 收據 | docs/research/{slug}.hook-receipt.md |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n| model.role.unavailable_worker | [not-a-real-model-for-unified-test;low, gpt-6.1-sol;low] |\n')
  prompt='使用 task-harness 完成實際模型回退驗收：這是已確認的專案根目錄，允許保存唯一任務合約與結果。依 unavailable_worker 角色候選清單，實際用原生角色建立新上下文 worker，工作是唯讀檢查 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加換行。首選模型故意為不可用名稱；請保留宿主真實拒絕或失敗，確認沒有工作執行後才依規則改派下一候選 gpt-6.1-sol/low。固定 unavailable_worker 角色不可直接覆寫其模型；可用宿主支援的通用原生 agent，保留相同工作範圍與指示，fork_turns=none、自足上下文。不要修改長期設定、安裝服務或假造失敗。若取得 handle 必須先查明狀態，不盲目重派。把真實失敗、回退原因、成功 handle、宿主可觀測模型與檢查結果寫入 docs/research/fallback.research.md，完成驗收並讀回合約。此案例不要求改變主責模型。'
 elif a.case=='readonly-invalid':
  (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| task-contract | 合約 | docs/plans/{slug}.md |\n| task-contract | 衝突合約 | other/{slug}.md |\n| hook-receipt | 收據 | docs/research/{slug}.jsonl |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 9 |\n| schema_version | 1 |\n')
  (project/'harness-project.json').write_text(json.dumps({'schema_version':1,'project_root':str(project),'contract_dir':'docs/plans','receipt_dir':'docs/research','host':{'session_identity':True,'user_turn_identity':True,'stop_continuation':True}}))
  prompt='使用已安裝的 task-harness 檢視這個已確認根目錄的設定與舊設定移轉可行性。這次只討論、唯讀，不得新增、修改或刪除任何檔案，也不得初始化合約。指出缺漏、重複、衝突及版本問題，說明是否能通過三項刪除門檻。不要將先前 host=true 當成新資格，不要自行選一份重複值。'
 elif a.case=='model-policy':
  (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n| research | 證據 | docs/research/{slug}.research.md |\n| task-contract | 合約 | docs/plans/{slug}.task-contract.md |\n| hook-receipt | 收據 | docs/research/{slug}.hook-receipt.md |\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n| model.default | [gpt-6.1-sol;low] |\n| model.stage.研究 | [gpt-6-sol;medium] |\n| model.role.analyst | [gpt-6.1-sol;high] |\n')
  cases=[{'id':'user','current':'[gpt-6-sol;low]','task':'[gpt-6.1-sol;medium]','role':'analyst','stage':'研究'}, {'id':'task','current':None,'task':'[gpt-6-sol;low]','role':'analyst','stage':'研究'}, {'id':'role','current':None,'task':None,'role':'analyst','stage':'研究'}, {'id':'stage','current':None,'task':None,'role':None,'stage':'研究'}, {'id':'project','current':None,'task':None,'role':None,'stage':'未設定'}, {'id':'fallback','candidates':'[not-an-available-model;high, gpt-6-sol;none]','observed_unavailable':['not-an-available-model'],'observed_effort_unsupported':['gpt-6-sol;none'],'host_default_effort':{'gpt-6-sol':'medium'}}, {'id':'default','candidates':'[not-an-available-model]','observed_unavailable':['not-an-available-model']}, {'id':'dedup','candidates':'[gpt-6-sol;low, gpt-6-sol;high, default]','observed_unavailable':['gpt-6-sol']}, {'id':'strict','candidates':'[gpt-6-sol;none]','observed_effort_unsupported':['gpt-6-sol;none'],'user_restriction':'這個模型的強度不可變更'}, {'id':'inherit','project_defaults_present':False,'current':None,'task':None,'role':None,'stage':None}, {'id':'new-task','previous_task_override':'[gpt-6-sol;high]','new_task':True}]
  (project/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
  prompt='使用已安裝 task-harness 的模型規則，完成一個設定判讀任務：讀取 cases.json 與 project-setting.md，把每個 case 的首選來源、模型、強度、依序回退結果和理由寫入 docs/research/model-policy.research.md，並保存唯一任務合約。cases 的 observed_* 是明列的測試輸入，不是你實際查到的 provider 事件；請明確標示這點。這個任務只驗證模型實際判讀規則，不做派工或推定 provider 可用性。不要修改專案長期設定；不需要執行解析／判斷 helper。沒有指定主責資訊時使用原生繼承並標不可觀測值。'
 else:
  prompt='使用已安裝的 task-harness 完成小任務：這是已確認的專案根目錄，允許透過 project-setting 初始化設定與唯一任務合約。產出 docs/research/packaged-result.research.md，精確一行 PACKAGED_OK，讀回驗收並保留 preserve.txt。不安裝 runtime、服務或執行 helper scripts。依你實際收到的 hook 提醒與技能規則核對開始及收尾，不要把提醒當作機械驗收或假造收據。回報實際成果與限制。'
 initial={str(f.relative_to(project)):hashlib.sha256(f.read_bytes()).hexdigest() for f in project.rglob('*')if f.is_file()}
 (out/'prompt.txt').write_text(prompt)
 result=native('model',['exec','--skip-git-repo-check','--json','--approve-for-me','--dangerously-bypass-hook-trust','-m','gpt-6.1-sol','-c','model_reasoning_effort="low"',prompt],project,env)
 phases=[result]
 if a.case=='hook-recovery' and result['exit_code']==0:
  shutil.copytree(project,out/'artifacts-phase1',ignore=shutil.ignore_patterns('.git','.agents'))
  actual=json.loads((project/'.codex/hooks.json').read_text())['hooks']
  canonical=json.loads((CANDIDATE/'skills/task-harness/assets/codex-hooks.json').read_text())['hooks']
  allowed={'echo UNRELATED_SENTINEL'}
  for definition in (canonical,json.loads((CANDIDATE/'skills/project-setting/assets/codex-hooks.json').read_text())['hooks']):
   for groups in definition.values():
    for group in groups:
     for handler in group['hooks']:allowed.add(handler['command'])
  observed=[handler for groups in actual.values()for group in groups for handler in group['hooks']]
  assert all(h['command']in allowed for h in observed),observed
  assert sum(h['command']=='echo UNRELATED_SENTINEL'for h in observed)==1
  assert all(sum(h==wanted for g in actual.get(event,[])for h in g['hooks'])==1 for event,groups in canonical.items()for g in groups for wanted in g['hooks'])
  phase2='使用 task-harness 明確接續同一份 docs/plans/hook-recovery.task-contract.md。這是已確認的相同專案根目錄；本回合授權完成 T2。先核對 T1 與 hooks 實際現況，保留 ledger.txt 的一次 T1_ONCE，不重做寫入或另建合約。產出 docs/research/recovery-result.research.md 精確一行 RECOVERED_OK，核對全部成果並保存讀回合約。保留無關 sentinel handler、preserve.txt，不安裝工具或服務。'
  (out/'prompt-phase2.txt').write_text(phase2)
  result=native('model-phase2',['exec','--skip-git-repo-check','--json','--approve-for-me','--dangerously-bypass-hook-trust','-m','gpt-6.1-sol','-c','model_reasoning_effort="low"',phase2],project,env)
  phases.append(result)
 final={str(f.relative_to(project)):hashlib.sha256(f.read_bytes()).hexdigest() for f in project.rglob('*')if f.is_file()}
 shutil.copytree(project,out/'artifacts',ignore=shutil.ignore_patterns('.git','.agents'))
 context=[];hook_records=[]
 for fp in (state/'sessions').rglob('*.jsonl'):
  for line in fp.read_text().splitlines():
   try:event=json.loads(line)
   except ValueError:continue
   if event.get('type')=='turn_context':
    data=event.get('payload',{});context.append({'session_log':str(fp.relative_to(state)),'timestamp':event.get('timestamp'),'model':data.get('model'),'effort':data.get('effort'),'turn_id':data.get('turn_id')})
   if 'task-harness:'in line or 'hook_'in line or 'hook/'in line:
    hook_records.append(event)
 (out/'session-contexts.json').write_text(json.dumps(context,ensure_ascii=False,indent=2))
 (out/'hook-session-records.json').write_text(json.dumps(hook_records,ensure_ascii=False,indent=2))
 cache=state/'plugins/cache/unified-t08-local/kengp3-harness/0.3.0'
 installed_manifest=hashlib.sha256((cache/'runtime-manifest.json').read_bytes()).hexdigest() if cache.exists() else None
 summary={'case':a.case,'candidate':str(CANDIDATE),'candidate_manifest_sha256':hashlib.sha256((CANDIDATE/'runtime-manifest.json').read_bytes()).hexdigest(),'installed_manifest_sha256':installed_manifest,'plugin_installs':installs,'result':result,'phases':phases,'initial_files':initial,'final_files':final,'global_config_auth_unchanged':all(hashlib.sha256((BASE/n).read_bytes()).hexdigest()==v for n,v in before.items()),'hook_trust_bypass':True,'normal_persisted_trust_verified':False,'temporary_credentials_deleted_on_exit':True,'state_root':str(state),'project_root':str(project)}
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 print(json.dumps({'case':a.case,'exit_code':result['exit_code'],'hook_session_records':len(hook_records),'global_unchanged':summary['global_config_auth_unchanged']}))
