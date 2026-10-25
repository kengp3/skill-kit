"""Maintainer-only G06; transport adapted from G01 native-demo.py.
Public preconditions: exact candidate, static hooks, isolated roots/state, no replay.
Run once; observation timeout repolls same live handle. Never a product dependency.
"""
import hashlib, json, os, selectors, shutil, subprocess, tempfile, time
from pathlib import Path
OUT=Path(__file__).resolve().parent
CODEX=Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
BASE=Path('/Users/kengp3/.codex')
CANDIDATE=Path('/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0')
MANIFEST='7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Native:
    def __init__(self, state, out=OUT):
        self.out = out
        self.counter = 0; self.buffer = b''; self.records = []
        self.raw = (self.out/'rpc.jsonl').open('w'); self.err = (self.out/'server.stderr.log').open('w')
        env = os.environ.copy(); env['CODEX_HOME'] = str(state)
        for key in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_ACCESS_TOKEN', 'CHATGPT_AUTH_TOKEN', 'CODEX_REMOTE_TOKEN'):
            env.pop(key, None)
        self.proc = subprocess.Popen([str(CODEX), 'app-server', '--stdio'], cwd=DEMO, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.err)
        self.selector = selectors.DefaultSelector(); self.selector.register(self.proc.stdout, selectors.EVENT_READ)
        self.rpc('initialize', {'clientInfo': {'name': 'g06_hook_sources', 'version': '1.0'}, 'capabilities': {'experimentalApi': True}})
        self.send({'method': 'initialized', 'params': {}})

    def send(self, message):
        self.log('client', message)
        self.proc.stdin.write((json.dumps(message) + '\n').encode()); self.proc.stdin.flush()

    def log(self, direction, message):
        self.records.append({'direction': direction, 'message': message})
        self.raw.write(json.dumps({'at': time.time(), 'direction': direction, 'message': message}, ensure_ascii=False) + '\n'); self.raw.flush()

    def read(self, seconds=30):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                if not line: continue
                msg = json.loads(line); self.log('server', msg)
                if 'id' in msg and 'method' in msg:
                    self.send({'id': msg['id'], 'error': {'code': -32601, 'message': 'No external interactive authorization supplied by G01 controller'}})
                return msg
            for key, _ in self.selector.select(.2):
                data = os.read(key.fd, 65536)
                if not data: raise RuntimeError('owned native server EOF')
                self.buffer += data
        raise TimeoutError('observation window only; original native handle remains live')

    def rpc(self, method, params):
        self.counter += 1; rid = self.counter
        self.send({'id': rid, 'method': method, 'params': params})
        while True:
            msg = self.read(60)
            if msg.get('id') == rid:
                if 'error' in msg: raise RuntimeError(json.dumps(msg))
                return msg['result']

    def thread(self):
        return self.rpc('thread/start', {'cwd': str(DEMO), 'runtimeWorkspaceRoots': [str(DEMO)], 'ephemeral': False, 'model': 'gpt-6.1-sol', 'sandbox': 'workspace-write', 'approvalPolicy': 'on-request', 'approvalsReviewer': 'auto_review', 'config': {'model_reasoning_effort': 'low', 'bypass_hook_trust': True}})

    def turn(self, tid, phase, prompt, skills=()):
        (self.out/(phase+'-prompt.txt')).write_text(prompt)
        inputs = [{'type': 'text', 'text': prompt}] + [{'type': 'skill', 'name': name, 'path': str(DEMO/'.agents/skills'/name/'SKILL.md')} for name in skills]
        result = self.rpc('turn/start', {'threadId': tid, 'input': inputs, 'effort': 'low'})
        turn = result['turn']['id']
        save(self.out/'live.json', {'server_pid': self.proc.pid, 'thread_id': tid, 'turn_id': turn, 'phase': phase, 'state': 'running'})
        print(json.dumps({'phase': phase, 'server_pid': self.proc.pid, 'thread': tid, 'turn': turn}), flush=True)
        while True:
            try: msg = self.read(30)
            except TimeoutError:
                print(json.dumps({'phase': phase, 'observation': 'same handle still pending'}), flush=True)
                continue
            if msg.get('method') == 'turn/completed' and msg.get('params', {}).get('threadId') == tid and msg['params'].get('turn', {}).get('id') == turn:
                save(self.out/(phase+'-terminal.json'), msg['params']['turn'])
                save(self.out/'live.json', {'server_pid': self.proc.pid, 'thread_id': tid, 'turn_id': turn, 'phase': phase, 'state': 'terminal', 'status': msg['params']['turn'].get('status')})
                return msg['params']['turn']

    def close(self):
        self.proc.stdin.close()
        try: self.proc.wait(15)
        except subprocess.TimeoutExpired: self.proc.terminate(); self.proc.wait(10)
        self.selector.close(); self.raw.close(); self.err.close()
        return self.proc.returncode


def archive_catalog(state):
 """Redact only the irrelevant plugin/list reply; hash private original bytes."""
 private=state/'unrelated-catalog-raw';private.mkdir(mode=0o700)
 originals={}
 for name in ('rpc.jsonl','plugins-list.json'):
  source=OUT/name;target=private/name
  shutil.copyfile(source,target)
  originals[name]={'private_original':str(target),'sha256':sha(target),'size':target.stat().st_size}
 output=[]
 for line in (OUT/'rpc.jsonl').read_bytes().splitlines(keepends=True):
  record=json.loads(line)
  if record['direction']=='server' and record['message'].get('id')==4 and 'result' in record['message']:
   record['message']['result']={'redacted_unrelated_remote_catalog':True,'summary_file':'plugins-summary.json'}
   line=(json.dumps(record,ensure_ascii=False)+'\n').encode()
  output.append(line)
 (OUT/'rpc.jsonl').write_bytes(b''.join(output))
 catalog=json.loads((OUT/'plugins-list.json').read_text())
 save(OUT/'plugins-summary.json',{'marketplaces':[{'name':m['name'],'path':m.get('path'),'plugins':[{'id':x['id'],'installed':x.get('installed'),'enabled':x.get('enabled'),'source':x.get('source')} for x in m.get('plugins',[]) if x.get('installed')]} for m in catalog.get('marketplaces',[])],'marketplaceLoadErrors':catalog.get('marketplaceLoadErrors')})
 (OUT/'plugins-list.json').unlink()
 save(OUT/'catalog-redaction.json',{'reason':'Exclude unrelated remote catalog and signed icon URLs; every other RPC line retained byte-for-byte','originals':originals})


def archive_sessions(state):
 """Keep full private originals; public excerpts omit only identity metadata/guardian."""
 index=[]
 for source in (state/'sessions').rglob('*.jsonl'):
  raw=source.read_bytes().splitlines(keepends=True)
  events=[json.loads(line) for line in raw]
  meta=next(x['payload'] for x in events if x.get('type')=='session_meta')
  guardian=isinstance(meta.get('source'),dict) and meta['source'].get('subagent',{}).get('other')=='guardian'
  relative=source.relative_to(state/'sessions')
  target=OUT/'sessions'/relative.with_suffix('.excerpt.jsonl')
  omitted=[n for n,e in enumerate(events,1) if guardian or e.get('type')=='session_meta']
  if not guardian:
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(b''.join(line for n,line in enumerate(raw,1) if n not in omitted))
  index.append({'id':meta['id'],'source':meta.get('source'),'parent_thread_id':meta.get('parent_thread_id'),'private_original':str(source),'full_sha256':sha(source),'full_line_count':len(raw),'public_excerpt':None if guardian else str(target.relative_to(OUT)),'retained_original_lines':[] if guardian else [n for n in range(1,len(raw)+1) if n not in omitted],'omitted_original_lines':omitted,'reason':'unrelated native guardian' if guardian else 'session_meta includes unnecessary creator identity; other lines kept byte-for-byte'})
 save(OUT/'session-index.json',index)


def run():
 global DEMO
 assert not (OUT/'preconditions.json').exists() and not (OUT/'rpc.jsonl').exists(), 'existing case: inspect saved handle, never restart'
 assert sha(CANDIDATE/'runtime-manifest.json')==MANIFEST
 manifest=json.loads((CANDIDATE/'runtime-manifest.json').read_text())
 assert all(sha(CANDIDATE/n)==h for n,h in manifest['files'].items())
 root=Path(tempfile.mkdtemp(prefix='g06-native-',dir='/private/tmp'));root.chmod(0o700)
 DEMO=root/'project';DEMO.mkdir();state=root/'state';state.mkdir(mode=0o700)
 shutil.copyfile(BASE/'auth.json',state/'auth.json');(state/'auth.json').chmod(0o600)
 before={n:sha(BASE/n) for n in ('auth.json','config.toml')}
 source=Path('/Users/kengp3/Workspaces/mine/demo-002')
 for name in ('AGENTS.md','project-setting.md'):shutil.copyfile(source/name,DEMO/name)
 (DEMO/'preserve.txt').write_bytes(b'G06_PRESERVE\n')
 for name in ('define-task','project-setting','task-harness','ai-code-review'):
  shutil.copytree(CANDIDATE/'skills'/name,DEMO/'.agents/skills'/name,ignore=shutil.ignore_patterns('scripts','__pycache__'))
 hooks={'hooks':{}}
 for name in ('project-setting','task-harness'):
  value=json.loads((CANDIDATE/'skills'/name/'assets/codex-hooks.json').read_text())
  for event,groups in value['hooks'].items():
   for group in groups:
    assert set(group)=={'hooks'}, 'canonical group only'
    for h in group['hooks']:
     assert h['type']=='command' and h['timeout']==5
     for key,prefix in [('command','echo '),('commandWindows','cmd /d /c echo ')]:
      assert h[key].startswith(prefix)
      assert not any(x in h[key] for x in (';','&','|','`','$','>','<','\n','\r'))
   hooks['hooks'].setdefault(event,[]).extend(groups)
 (DEMO/'.codex').mkdir();save(DEMO/'.codex/hooks.json',hooks)
 (DEMO/'.codex/config.toml').write_text('[features]\nhooks = true\n')
 cfg='cli_auth_credentials_store = "file"\n[features]\nhooks = true\n[projects.'+json.dumps(str(DEMO))+']\ntrust_level = "trusted"\n'
 for name in ('archify','define-task','project-setting'):
  cfg+='\n[[skills.config]]\npath = "/Users/kengp3/.agents/skills/'+name+'/SKILL.md"\nenabled = false\n'
 (state/'config.toml').write_text(cfg)
 save(OUT/'canonical-hooks.json',hooks);(OUT/'isolated-config.toml').write_text(cfg)
 fixed={name:sha(DEMO/name) for name in ('AGENTS.md','project-setting.md','preserve.txt','.codex/hooks.json','.codex/config.toml')}
 save(OUT/'preconditions.json',{'case_root':str(DEMO),'state':str(state),'manifest':MANIFEST,'global_before':before,'source_instruction_hashes':{n:sha(source/n) for n in ('AGENTS.md','project-setting.md')},'fixed':fixed,'hook_bytes_reviewed':True,'static_metacharacters_absent':True,'thread_config_override':{'bypass_hook_trust':True},'normal_persisted_trust_test':False,'runtimeWorkspaceRoots':[str(DEMO)]})
 native=Native(state);summary={'root':str(root),'state':str(state),'phases':[]}
 save(OUT/'controller-live.json',{'controller_pid':os.getpid(),'server_pid':native.proc.pid,'root':str(root),'phase':'preflight'})
 skills=native.rpc('skills/list',{'cwds':[str(DEMO)],'forceReload':True});save(OUT/'skills-list.json',skills)
 hl=native.rpc('hooks/list',{'cwds':[str(DEMO)]});save(OUT/'hooks-list.json',hl)
 assert all(h['sourcePath']==str(DEMO/'.codex/hooks.json') for d in hl['data'] for h in d['hooks'])
 assert sum(len(d['hooks']) for d in hl['data'])==5
 save(OUT/'plugins-list.json',native.rpc('plugin/list',{'cwds':[str(DEMO)]}))
 print(json.dumps({'phase':'qualified-awaiting-slot','pid':native.proc.pid,'root':str(root)}),flush=True)
 start=native.thread();save(OUT/'thread-start.json',start);tid=start['thread']['id']
 save(OUT/'controller-live.json',{'controller_pid':os.getpid(),'server_pid':native.proc.pid,'root':str(root),'thread':tid,'phase':'thread-qualified-awaiting-slot'})
 while not (root/'start-model').exists():time.sleep(1)
 common='這是已確認專案根目錄 '+str(DEMO)+'。明確使用 $task-harness，先讀 AGENTS.md、project-setting.md 與技能。只用原生工具與模型，不使用 Python/Node/helper、不安裝套件/服務，不改設定、hooks或全域。唯一任務g06-lifecycle，唯一合約docs/plans/g06-lifecycle.task-contract.md。ledger.txt是產品一次寫入canary，精確G06_ONCE加一個LF；保留preserve.txt。正常Stop hook是被動{}且不產生新授權。不要因收到hook重播成果、重驗未改條件或重派worker；未知先查回原handle。無宿主ID留null不造值。'
 p1=common+' 本回合授權：先保存並讀回合約，完成T1一次canary寫入與讀回；T2只由一個原生唯讀worker核對preserve.txt，拿到真實handle與完成結果後保存，同worker不要重啟；worker不寫檔不建立其他agent，沒有模型指定沿用主責。T3是後續生命週期核對，本回合保留pending並等待明確續作。本回合只完成T1/T2，不產出T3。'
 t=native.turn(tid,'startup',p1,('task-harness',));summary['phases'].append({'phase':'startup','thread':tid,'turn':t});assert t['status']=='completed'
 for phase in ('startup',):
  shutil.copytree(DEMO,OUT/(phase+'-artifacts'),ignore=shutil.ignore_patterns('.agents','.codex'))
  r=subprocess.run(['python3',str(OUT/'check.py'),str(DEMO)],capture_output=True,text=True);save(OUT/(phase+'-check.json'),{'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 save(OUT/'before-resume-read.json',native.rpc('thread/read',{'threadId':tid,'includeTurns':True}))
 summary['server1_exit']=native.close()
 native=Native(state,OUT/'resume')
 resumed=native.rpc('thread/resume',{'threadId':tid,'cwd':str(DEMO),'runtimeWorkspaceRoots':[str(DEMO)],'sandbox':'workspace-write','approvalPolicy':'on-request','approvalsReviewer':'auto_review','config':{'bypass_hook_trust':True}});save(OUT/'thread-resume.json',resumed);assert resumed['thread']['id']==tid
 p2=common+' 明確續作同一任務。本回合只核對原合約、原worker與既有canary/副作用；沿用T1/T2證據，不重寫canary、不派任何新worker、不重驗未變條件。保存恢復資訊並保留T3 pending後等待下一次明確續作。不要宣稱同event redelivery。'
 t=native.turn(tid,'resume',p2,('task-harness',));summary['phases'].append({'phase':'resume','thread':tid,'turn':t});assert t['status']=='completed'
 shutil.copytree(DEMO,OUT/'resume-artifacts',ignore=shutil.ignore_patterns('.agents','.codex'))
 save(OUT/'compact-request.json',native.rpc('thread/compact/start',{'threadId':tid}))
 while True:
  try:m=native.read(30)
  except TimeoutError:print('compact pending; same handle',flush=True);continue
  if m.get('method')=='turn/completed' and m.get('params',{}).get('threadId')==tid:
   save(OUT/'compact-terminal.json',m['params']);assert m['params']['turn']['status']=='completed';break
 p3=common+' 明確續作同一任務，剛才由原生thread/compact/start做真正compaction。本回合T3只核對原合約及可觀測worker狀態與一次canary，不重寫T1、不派新agent、不重驗未變條件。保存必要生命週期核對/授權資訊及合約done並讀回；不得把compaction或hook本身當新授權，不建立額外成果/收據。'
 t=native.turn(tid,'after-compact',p3,('task-harness',));summary['phases'].append({'phase':'after-compact','thread':tid,'turn':t});assert t['status']=='completed'
 shutil.copytree(DEMO,OUT/'final-artifacts',ignore=shutil.ignore_patterns('.agents','.codex'))
 r=subprocess.run(['python3',str(OUT/'check.py'),str(DEMO)],capture_output=True,text=True);save(OUT/'green-check.json',{'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 save(OUT/'final-read.json',native.rpc('thread/read',{'threadId':tid,'includeTurns':True}))
 save(OUT/'background-terminals.json',native.rpc('thread/backgroundTerminals/list',{'threadId':tid}))
 summary['server2_exit']=native.close()
 archive_catalog(state)
 archive_sessions(state)
 summary['fixed_unchanged']=all(sha(DEMO/n)==h for n,h in fixed.items())
 summary['global_unchanged']=all(sha(BASE/n)==h for n,h in before.items())
 save(OUT/'summary.json',summary)
 print(json.dumps({'phase':'all-terminal','root':str(root),'summary':str(OUT/'summary.json')}),flush=True)
if __name__=='__main__':
 (OUT/'resume').mkdir(exist_ok=True)
 run()
