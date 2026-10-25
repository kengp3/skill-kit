"""Maintainer-only real native-agent settings/I/O probes; no product dependency."""
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path

CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
CANDIDATE=Path('/private/tmp/unified-review-final-0.3.0')
BASE=Path('/Users/kengp3/.codex')
OUT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('case',choices=['repair-order','matcher-scope','write-failure','read-failure','delete-failure']);p.add_argument('--attempt',default='');a=p.parse_args()
out=OUT/(a.case+('-'+a.attempt if a.attempt else ''));out.mkdir(exist_ok=False)
manifest=json.loads((CANDIDATE/'runtime-manifest.json').read_text())
assert all(hashlib.sha256((CANDIDATE/n).read_bytes()).hexdigest()==v for n,v in manifest['files'].items())
global_before={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest()for n in ['config.toml','auth.json']}

def snapshot(project):
 return {str(f.relative_to(project)):hashlib.sha256(f.read_bytes()).hexdigest()for f in project.rglob('*')if f.is_file()}
def native(label,prompt,project,env):
 (out/(label+'.prompt.txt')).write_text(prompt)
 with (out/(label+'.stdout.jsonl')).open('w')as stdout,(out/(label+'.stderr.log')).open('w')as stderr:
  proc=subprocess.Popen([str(CODEX),'exec','--skip-git-repo-check','--json','--approve-for-me','-m','gpt-6.1-sol','-c','model_reasoning_effort="low"',prompt],cwd=project,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
  try:code=proc.wait(timeout=600)
  except subprocess.TimeoutExpired:
   proc.terminate()
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
   code=None
 return {'exit_code':code,'owned_process_terminal':proc.poll()is not None}
def setting(project,full):
 s=(CANDIDATE/'skills/project-setting/assets/document-rules.md').read_text()
 if full:
  needle='| research | 研究證據、比較與調查 | docs/research/{slug}.research.md |';assert needle in s
  s=s.replace(needle,needle+'\n| task-contract | 任務合約 | docs/plans/harness/{filename} |\n| hook-receipt | 技術收據 | docs/research/receipts/{filename} |')
  s+='\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n| schema_version | 1 |\n'
 return s

with tempfile.TemporaryDirectory(prefix='unified-settings-fault-',dir='/private/tmp')as tmp:
 root=Path(tmp);state=root/'state';project=root/'project'
 state.mkdir(mode=0o700);project.mkdir(mode=0o700)
 shutil.copyfile(BASE/'auth.json',state/'auth.json');(state/'auth.json').chmod(0o600)
 (state/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = false\n[agents]\nenabled = false\n[projects.'+json.dumps(str(project))+']\ntrust_level = "trusted"\n')
 env=os.environ.copy();env['CODEX_HOME']=str(state)
 for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):env.pop(key,None)
 for name in ['define-task','project-setting','task-harness','ai-code-review']:
  shutil.copytree(CANDIDATE/'skills'/name,project/'.agents/skills'/name,ignore=shutil.ignore_patterns('scripts','__pycache__'))
 (project/'preserve.txt').write_text('KEEP_EXISTING_CONTENT\n')
 (project/'project-setting.md').write_text(setting(project,a.case in ['delete-failure']))
 phases=[];controls=[];protected=[]
 try:
  if a.case=='repair-order':
   (project/'project-setting.md').write_text('# 文件規範\n\n| 類型 | 文件用途 | 目的地與檔名 |\n| --- | --- | --- |\n|   hook-receipt   | 技術收據 | docs/research/{slug}.hook-receipt.md |\n| research | 證據 | docs/research/{slug}.research.md |\n|   task-contract | 任務合約 | docs/plans/{slug}.task-contract.md |\n\n## Other Settings\n\nKEEP_CUSTOM_SECTION\n\n## Task Harness\n\n| 設定項目 | 值 |\n| --- | --- |\n|  model.default   |  [gpt-6.1-sol;low]  |\n')
   prompt='使用 task-harness 完成這個已確認專案根目錄的小任務：先由 project-setting 依技能規格修復必要但缺少的 schema_version，正常讀取列順序與空白已調整的分類表；保留 Other Settings 中 KEEP_CUSTOM_SECTION 與所有既有有效位置及 model.default。修復後產出 docs/research/repair-order.research.md 精確一行 REPAIR_ORDER_OK，讀回驗收並保存唯一合約。本次保持 hooks 停用，不改任何平台設定、不安裝工具、不執行 runtime/helper scripts。保留 preserve.txt。'
  elif a.case=='matcher-scope':
   hooks=json.loads((CANDIDATE/'skills/task-harness/assets/codex-hooks.json').read_text())['hooks'];(project/'.codex').mkdir()
   (project/'.codex/hooks.json').write_text(json.dumps({'hooks':{'SessionStart':[{'matcher':'startup','hooks':hooks['SessionStart'][0]['hooks']}] }},indent=2))
   prompt='使用 project-setting 並參照 task-harness 自帶設定規格，唯讀診斷這個已確認專案根目錄的 Codex 標準 hooks 覆蓋範圍。既有 SessionStart 的 command 與 canonical 相同，但群組是 matcher=startup。這是使用者自訂的受限範圍，未授權擴大、刪除或新增任何 handler；所有檔案保持不變，只回覆是否等效涵蓋 canonical 所需來源，哪些範圍仍缺少。不能只因命令相同就認定完整接入，也不得靠新增重疊副本或寫信任旗標消除缺口。本次不啟動產品開發任務。'
  else:
   (project/'docs/plans/harness').mkdir(parents=True);(project/'docs/research/receipts').mkdir(parents=True)
   (project/'docs/plans/harness/legacy.md').write_text('# Historical contract artifact\nKEEP_CONTRACT_BYTES\n')
   (project/'docs/research/receipts/old.jsonl').write_text('{"kind":"legacy"}\n')
   (project/'harness-project.json').write_text(json.dumps({'schema_version':1,'project_root':str(project),'contract_dir':'docs/plans/harness','receipt_dir':'docs/research/receipts','host':{'session_identity':True,'user_turn_identity':False,'stop_continuation':True}},indent=2))
   common='使用 task-harness 的設定移轉流程處理這個已確認的專案根目錄，由 project-setting 依規格操作。這次只做設定移轉，不開始產品開發任務。保留 preserve.txt、歷史合約 legacy.md 與 old.jsonl 的位元組及位置。不執行 runtime/helper scripts，不安裝工具或服務。不得更改目標檔案的權限、檔案旗標或目錄名稱。若宿主的 sandbox-exec 本身無法啟動，允許對已授權且限於此專案的普通讀寫操作提出原生 scoped 工具批准請求；這不授權 chmod、chflags 或修改任何檔案安全屬性。若目標檔案的普通操作仍失敗，保留原始檔並回報實際錯誤和阻礙，不建立替代設定或備份。'
   if a.case=='write-failure':
    target=project/'project-setting.md';r=subprocess.run(['/usr/bin/chflags','uchg',str(target)],capture_output=True,text=True);assert r.returncode==0,r.stderr;protected.append(target);controls.append({'operation':'set_immutable','target':'project-setting.md','exit_code':r.returncode})
    prompt=common+'請依真實內容先完成無歧義對帳，再以普通寫入操作嘗試一次合併新設定；只有寫入及正常讀回等三個門檻都成立才可以刪舊 JSON。不要藉解除旗標繞過失敗。'
   elif a.case=='delete-failure':
    target=project/'harness-project.json';r=subprocess.run(['/usr/bin/chflags','uchg',str(target)],capture_output=True,text=True);assert r.returncode==0,r.stderr;protected.append(target);controls.append({'operation':'set_immutable','target':'harness-project.json','exit_code':r.returncode})
    prompt=common+'新 Markdown 已預置完成，但仍須按正常流程重新核對三個門檻。三者全部成立後，請以普通刪除操作嘗試一次刪除已移轉的 harness-project.json；若系統拒絕則保留兩檔及具體阻礙，不重跑移轉、不冒稱已刪除。'
   else:
    prompt=common+'本階段只授權完成新設定合併、讀回與對帳；明確禁止在此回合刪除舊 harness-project.json。完成後等待下一回合續作，不提前清理舊檔。'
  initial=snapshot(project);(out/'fixture-before.json').write_text(json.dumps(initial,indent=2))
  phases.append(native('phase1',prompt,project,env))
  if a.case=='read-failure'and phases[-1]['exit_code']==0 and '| schema_version | 1 |' in (project/'project-setting.md').read_text():
   assert (project/'harness-project.json').is_file()
   first=snapshot(project);shutil.copytree(project,out/'artifacts-phase1',ignore=shutil.ignore_patterns('.agents','.git'))
   (project/'project-setting.md').chmod(0);controls.append({'operation':'chmod_000','target':'project-setting.md'})
   try:(project/'project-setting.md').read_bytes();controls.append({'controller_read_denied':False})
   except PermissionError as e:controls.append({'controller_read_denied':True,'errno':e.errno})
   phase2=common+'明確接續上一階段的同一移轉：請重新從磁碟正常讀取 project-setting.md，核對真實狀態後才決定是否可以刪除舊 JSON。本回合沒有更改權限或檔案旗標的授權；讀回若失敗則保留舊檔並回報，不能把前次已讀值當本次讀回。失敗時只在最終回覆說明，不新增或修改診斷文件。'
   phases.append(native('phase2',phase2,project,env))
   (project/'project-setting.md').chmod(0o644);controls.append({'operation':'controller_restore_read_permission_after_terminal'})
   (out/'phase1-files.json').write_text(json.dumps(first,indent=2))
 finally:
  for target in protected:
   r=subprocess.run(['/usr/bin/chflags','nouchg',str(target)],capture_output=True,text=True);controls.append({'operation':'controller_clear_immutable_after_terminal','target':target.name,'exit_code':r.returncode});assert r.returncode==0,r.stderr
  target=project/'project-setting.md'
  if target.exists():target.chmod(0o644)
 final=snapshot(project);shutil.copytree(project,out/'artifacts',ignore=shutil.ignore_patterns('.agents','.git'))
 contexts=[];errors=[]
 for fp in (state/'sessions').rglob('*.jsonl'):
  for line in fp.read_text().splitlines():
   try:event=json.loads(line)
   except ValueError:continue
   if event.get('type')=='turn_context':
    d=event.get('payload',{});contexts.append({'session_log':str(fp.relative_to(state)),'timestamp':event.get('timestamp'),'model':d.get('model'),'effort':d.get('effort'),'turn_id':d.get('turn_id')})
   if any(x in line.lower()for x in ['operation not permitted','permission denied','eperm','eacces','immutable','read-only file system']):errors.append(event)
 (out/'session-contexts.json').write_text(json.dumps(contexts,ensure_ascii=False,indent=2));(out/'permission-events.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2))
 summary={'case':a.case,'candidate_manifest_sha256':hashlib.sha256((CANDIDATE/'runtime-manifest.json').read_bytes()).hexdigest(),'project_root':str(project),'phases':phases,'controls':controls,'initial_files':initial,'final_files':final,'global_config_auth_unchanged':all(hashlib.sha256((BASE/n).read_bytes()).hexdigest()==v for n,v in global_before.items()),'temporary_credentials_deleted_on_exit':True,'hook_trust_bypass':False,'helpers_copied':False}
 (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps({'case':a.case,'phases':phases,'global_unchanged':summary['global_config_auth_unchanged']}))
