"""G02 maintainer-only native workflow signal trial; not product runtime."""
import argparse, hashlib, json, os, re, selectors, shlex, shutil, signal, subprocess, tempfile, time, uuid
from pathlib import Path

OUT = Path(__file__).resolve().parent
DEMO = Path('/Users/kengp3/Workspaces/mine/demo-002')
CANDIDATE = Path('/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0')
BASE = Path('/Users/kengp3/.codex')
CODEX = Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
MANIFEST = '7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'
SKILLS = ('define-task', 'project-setting', 'task-harness', 'ai-code-review')
PRESERVE = ('AGENTS.md', 'preserve.txt', 'ledger.txt', 'docs/plans/harness/legacy.md', 'docs/research/receipts/old.jsonl')

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
def snapshot(project, label):
    shutil.copytree(project, OUT/label, ignore=shutil.ignore_patterns('.agents', '.git'))
    return {str(p.relative_to(project)): digest(p) for p in project.rglob('*') if p.is_file() and '.agents' not in p.parts}
def processes():
    rows = subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,args='], text=True)
    result = {}
    for line in rows.splitlines():
        values = line.strip().split(None, 2)
        if len(values) == 3: result[int(values[0])] = {'pid': int(values[0]), 'ppid': int(values[1]), 'command': values[2]}
    return result
def descendants(rows, parent):
    selected = {parent}
    while True:
        updated = selected | {p for p, row in rows.items() if row['ppid'] in selected}
        if updated == selected: return [rows[p] for p in sorted(selected) if p in rows]
        selected = updated
def absent(pid): return pid not in processes()

def preflight():
    assert os.getpid() in processes(), 'controller must observe its own OS process before any native trial'
    assert digest(CANDIDATE/'runtime-manifest.json') == MANIFEST
    return {'status': 'passed', 'controller_process_observable': True, 'manifest': MANIFEST}

class Native:
    def __init__(self, state, project, phase):
        self.project = project; self.phase = phase; self.counter = 0; self.buffer = b''; self.events = []; self.responses = {}
        self.raw = (OUT/(phase+'-rpc.jsonl')).open('x'); self.err = (OUT/(phase+'-server.stderr.log')).open('x')
        env = os.environ.copy(); env['CODEX_HOME'] = str(state)
        for key in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_ACCESS_TOKEN', 'CHATGPT_AUTH_TOKEN', 'CODEX_REMOTE_TOKEN'): env.pop(key, None)
        self.proc = subprocess.Popen([str(CODEX), 'app-server', '--stdio'], cwd=project, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.err, start_new_session=True)
        self.selector = selectors.DefaultSelector(); self.selector.register(self.proc.stdout, selectors.EVENT_READ)
        self.rpc('initialize', {'clientInfo': {'name': 'g02_migration_interrupt', 'version': '1.0'}, 'capabilities': {'experimentalApi': True}})
        self.send({'method': 'initialized', 'params': {}})
    def send(self, msg):
        self.log('client', msg); self.proc.stdin.write((json.dumps(msg)+'\n').encode()); self.proc.stdin.flush()
    def log(self, direction, msg):
        self.raw.write(json.dumps({'at': time.time(), 'direction': direction, 'message': msg}, ensure_ascii=False)+'\n'); self.raw.flush()
    def pump(self):
        if b'\n' not in self.buffer:
            if not self.selector.select(.2): return
            data = os.read(self.proc.stdout.fileno(), 65536)
            if not data: raise RuntimeError('owned server EOF; result unknown')
            self.buffer += data
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            if not line: continue
            msg = json.loads(line); self.log('server', msg)
            if 'id' in msg and 'method' in msg:
                self.send({'id': msg['id'], 'error': {'code': -32601, 'message': 'G02 controller grants no external interactive authorization'}})
            elif 'id' in msg: self.responses[msg['id']] = msg
            else: self.events.append(msg)
    def rpc(self, method, params):
        self.counter += 1; rid = self.counter; self.send({'id': rid, 'method': method, 'params': params})
        started = time.monotonic()
        while rid not in self.responses:
            self.pump()
            if time.monotonic()-started > 30:
                print(json.dumps({'pending_rpc': method, 'server_pid': self.proc.pid, 'no_retry': True}), flush=True); started = time.monotonic()
        msg = self.responses.pop(rid)
        if 'error' in msg: raise RuntimeError(json.dumps(msg))
        return msg['result']
    def thread(self):
        info = self.rpc('thread/start', {'cwd': str(self.project), 'runtimeWorkspaceRoots': [str(self.project)], 'ephemeral': False, 'model': 'gpt-6.1-sol', 'sandbox': 'workspace-write', 'approvalPolicy': 'on-request', 'approvalsReviewer': 'auto_review', 'config': {'model_reasoning_effort': 'low'}})
        save(OUT/(self.phase+'-thread.json'), info)
        assert info['runtimeWorkspaceRoots'] == [str(self.project)]
        assert info['instructionSources'] == [str(self.project/'AGENTS.md')]
        return info['thread']['id']
    def turn(self, tid, label, prompt, skills=()):
        (OUT/(label+'-prompt.txt')).write_text(prompt)
        inputs = [{'type': 'text', 'text': prompt}] + [{'type': 'skill', 'name': n, 'path': str(self.project/'.agents/skills'/n/'SKILL.md')} for n in skills]
        turn = self.rpc('turn/start', {'threadId': tid, 'input': inputs, 'effort': 'low'})['turn']['id']
        save(OUT/'live.json', {'server_pid': self.proc.pid, 'thread': tid, 'turn': turn, 'phase': label, 'state': 'running'})
        print(json.dumps({'server_pid': self.proc.pid, 'thread': tid, 'turn': turn, 'phase': label}), flush=True)
        return turn
    def terminal(self, tid, turn):
        return next((e['params']['turn'] for e in self.events if e.get('method') == 'turn/completed' and e['params'].get('threadId') == tid and e['params'].get('turn', {}).get('id') == turn), None)
    def wait(self, tid, turn):
        tick = time.monotonic()
        while not self.terminal(tid, turn):
            self.pump()
            if time.monotonic()-tick > 30:
                print(json.dumps({'observation': 'original handle still pending', 'server_pid': self.proc.pid, 'thread': tid, 'turn': turn}), flush=True); tick = time.monotonic()
        terminal = self.terminal(tid, turn); save(OUT/(self.phase+'-'+turn+'-terminal.json'), terminal)
        save(OUT/'live.json', {'server_pid': self.proc.pid, 'thread': tid, 'turn': turn, 'phase': self.phase, 'state': 'terminal', 'status': terminal['status']})
        return terminal
    def close(self):
        self.proc.stdin.close()
        try: self.proc.wait(15)
        except subprocess.TimeoutExpired: raise RuntimeError('owned native server has not exited; preserve state')
        self.selector.close(); self.raw.close(); self.err.close()
        return {'pid': self.proc.pid, 'exit_code': self.proc.returncode, 'absent': absent(self.proc.pid)}

def check():
    s = json.loads((OUT/'summary.json').read_text())
    assert s['status'] == 'passed', s
    assert s['signal']['count'] == 1 and s['signal']['number'] == signal.SIGTERM
    assert s['original_terminal']['status'] == 'interrupted' and s['resume_terminal']['status'] == 'completed'
    assert s['original_server']['absent'] and s['resume_server']['absent'] and not s['original_descendants_after']
    assert s['global_before'] == s['global_after'] and s['state_removed']
    for name in PRESERVE:
        assert (OUT/'initial'/name).read_bytes() == (OUT/'after-signal'/name).read_bytes() == (OUT/'final'/name).read_bytes(), name
    assert (OUT/'initial/harness-project.json').read_bytes() == (OUT/'after-signal/harness-project.json').read_bytes()
    assert not (OUT/'final/harness-project.json').exists()
    before = (OUT/'initial/project-setting.md').read_text(); partial = (OUT/'after-signal/project-setting.md').read_text(); final = (OUT/'final/project-setting.md').read_text()
    assert before != partial == final, 'real model merge must survive recovery without duplicate writes'
    assert partial.count('| task-contract |') == partial.count('| hook-receipt |') == partial.count('## Task Harness') == 1
    assert 'docs/plans/harness/{filename}' in final and 'docs/research/receipts/{filename}' in final
    assert not list((OUT/'final').rglob('*.task-contract.md')), 'migration-only task must not create a duplicate activity contract'
    records = [json.loads(line) for line in (OUT/'original-rpc.jsonl').read_text().splitlines()]
    start = s['command_started_event']; item = start['params']['item']['id']
    assert start['method'] == 'item/started' and start['params']['item']['status'] == 'inProgress'
    assert s['token'] in start['params']['item']['command']
    assert len([r for r in records if r['direction'] == 'client' and r['message'].get('method') == 'turn/interrupt']) == 1
    assert s['checkpoint_target']['pid'] == s['signal']['pid']
    assert s['checkpoint_target']['command'].endswith('sleep 120')
    readback = s['resume_readback']; assert readback['thread']['id'] == s['resume_thread']
    return {'status': 'passed', 'checks': ['native_started_pid_token_and_actual_merge', 'one_os_signal_and_native_interrupt', 'original_workers_exit_before_new_authorization', 'same_migration_identity', 'three_deletion_gates_raw_review_required', 'legacy_bytes_and_locations_preserved', 'no_duplicate_setting_or_contract', 'global_auth_config_unchanged']}

def run():
    preflight()
    assert not (OUT/'preconditions.json').exists(), 'existing trial evidence must be preserved; choose a new output directory'
    assert OUT.resolve() == OUT and DEMO.resolve() == DEMO
    assert digest(CANDIDATE/'runtime-manifest.json') == MANIFEST
    manifest = json.loads((CANDIDATE/'runtime-manifest.json').read_text())
    assert all(digest(CANDIDATE/n) == h for n, h in manifest['files'].items())
    root = Path(tempfile.mkdtemp(prefix='g02-migration-', dir='/private/tmp')); root.chmod(0o700)
    project = root/'project'; state = root/'state'; project.mkdir(mode=0o700); state.mkdir(mode=0o700)
    shutil.copyfile(BASE/'auth.json', state/'auth.json'); (state/'auth.json').chmod(0o600)
    config = 'cli_auth_credentials_store = "file"\n[features]\nhooks = false\napps = false\nplugins = false\n[projects.'+json.dumps(str(project))+']\ntrust_level = "trusted"\n'
    for n in ('archify', 'define-task', 'project-setting'):
        config += '\n[[skills.config]]\npath = '+json.dumps('/Users/kengp3/.agents/skills/'+n+'/SKILL.md')+'\nenabled = false\n'
    (state/'config.toml').write_text(config); (OUT/'isolated-config.toml').write_text(config)
    for n in SKILLS: shutil.copytree(CANDIDATE/'skills'/n, project/'.agents/skills'/n, ignore=shutil.ignore_patterns('scripts', '__pycache__'))
    installed = {}
    for rel, expected in manifest['files'].items():
        if any(rel.startswith('skills/'+n+'/') for n in SKILLS) and '/scripts/' not in rel:
            actual = project/'.agents'/rel; assert not actual.is_symlink() and digest(actual) == expected; installed[rel] = expected
    for rel in ('AGENTS.md', 'project-setting.md'): shutil.copyfile(DEMO/rel, project/rel)
    settings = (project/'project-setting.md').read_text()
    settings = '\n'.join(line for line in settings.splitlines() if not line.startswith('| task-contract |') and not line.startswith('| hook-receipt |')).split('\n## Task Harness')[0].rstrip()+'\n'
    (project/'project-setting.md').write_text(settings)
    (project/'docs/plans/harness').mkdir(parents=True); (project/'docs/research/receipts').mkdir(parents=True)
    (project/'preserve.txt').write_bytes(b'KEEP_G02_EXISTING_BYTES\n'); (project/'ledger.txt').write_bytes(b'EXISTING_ONCE\n')
    (project/'docs/plans/harness/legacy.md').write_bytes(b'# Historical completed contract\nKEEP_CONTRACT_BYTES\n')
    (project/'docs/research/receipts/old.jsonl').write_bytes(b'{"kind":"legacy","done":true}\n')
    legacy = {'schema_version': 1, 'project_root': str(project), 'contract_dir': 'docs/plans/harness', 'receipt_dir': 'docs/research/receipts', 'host': {'session_identity': True, 'user_turn_identity': False, 'stop_continuation': True}}
    save(project/'harness-project.json', legacy); (project/'case-control').mkdir()
    token = 'G02_MIGRATION_'+uuid.uuid4().hex
    checkpoint = shlex.join(['/bin/sh', '-c', 'printf "%s\\n" "$$" > case-control/checkpoint.pid; printf "'+token+'\\n" > case-control/checkpoint.token; exec /bin/sleep 120'])
    s = {'status': 'preparing', 'root': str(root), 'project': str(project), 'token': token, 'manifest': MANIFEST, 'installed_candidate_files': installed, 'host_version': subprocess.check_output([str(CODEX), '--version'], text=True).strip(), 'isolation_modes': {'state': oct(state.stat().st_mode & 0o777), 'auth': oct((state/'auth.json').stat().st_mode & 0o777)}, 'global_before': {n: digest(BASE/n) for n in ('config.toml', 'auth.json')}, 'demo_inputs': {n: digest(DEMO/n) for n in ('AGENTS.md', 'project-setting.md')}}
    s['initial_files'] = snapshot(project, 'initial'); save(OUT/'preconditions.json', s)
    current = Native(state, project, 'original'); tid = current.thread(); s['original_thread'] = tid
    skills = current.rpc('skills/list', {'cwds': [str(project)], 'forceReload': True}); save(OUT/'skills-list.json', skills)
    items = skills['data'][0]['skills']; assert not [x for x in items if x['scope'] == 'user' and x['enabled']]
    assert all(any(x['path'] == str(project/'.agents/skills'/n/'SKILL.md') and x['enabled'] for x in items) for n in SKILLS)
    save(OUT/'plugins-list.json', current.rpc('plugin/list', {'cwds': [str(project)], 'marketplaceKinds': ['local'], 'forceRefetch': False}))
    probe = current.turn(tid, 'probe', '已確認根目錄 '+str(project)+'。只用普通原生命令讀取 AGENTS.md、project-setting.md 與 preserve.txt；禁止寫入、執行 helper 或開始移轉。回覆讀取結果即可。')
    assert current.wait(tid, probe)['status'] == 'completed'; assert s['initial_files'] == {str(p.relative_to(project)): digest(p) for p in project.rglob('*') if p.is_file() and '.agents' not in p.parts}
    prompt = f'''明確使用本專案固定候選 $task-harness 與 $project-setting 做一次舊 JSON 設定移轉，根目錄已確認為 {project}。本次移轉身分固定 G02-migration；只做設定移轉，不開始產品任務、不建立活動合約。先讀現行 AGENTS.md、project-setting.md、harness-project.json、移轉規則及既有歷史合約／JSONL；以 docs/research/g02-migration.research.md 保存逐欄對帳及階段狀態。以 demo 的文件規範語意為基底，保留其他內容。歷史 ledger.txt 已完成一次，preserve.txt 與歷史產物 bytes/location 全部保留。
本階段授權依規格完成無歧義對帳與由 project-setting 合併新設定，明確保留舊 harness-project.json 等下一階段新授權。為驗收命中寫入後／刪舊前的真實命令窗口，實際寫入 project-setting.md 的那一個 shell 命令必須在成功寫入後，以 && 接上以下 checkpoint 命令（不能先用 apply_patch 寫入，再另跑普通 sleep）：
{checkpoint}
這是驗收專用 workflow 命令 checkpoint，非產品需求。模型需自行依規格組出最小正確新設定內容，控制器不預寫。checkpoint 正常或異常結束後本回合都停止，等待明確新授權，不能自動重試／繼續移轉／刪舊檔；使用者 Stop 立即服從，無須補寫紀錄。若工具異常，不宣稱寫入失敗或回滾，保留未知結果待查。
使用候選技能本身提供規則，hooks 在此案停用由模型接手；不使用 .planning、不派子代理、不改全域／信任資料庫、不執行 Python/Node/helper、不安裝工具。可對本專案普通讀寫提出 scoped 工具請求，但不改安全屬性。'''
    turn = current.turn(tid, 'migration', prompt, ('task-harness', 'project-setting')); s['original_turn'] = turn
    marker = None
    while True:
        current.pump()
        marker = next((e for e in current.events if e.get('method') == 'item/started' and e.get('params', {}).get('threadId') == tid and e['params'].get('turnId') == turn and e['params'].get('item', {}).get('type') == 'commandExecution' and e['params']['item'].get('status') == 'inProgress' and token in e['params']['item'].get('command', '')), marker)
        if marker and (project/'case-control/checkpoint.token').exists() and (project/'case-control/checkpoint.pid').exists():
            assert (project/'case-control/checkpoint.token').read_text() == token+'\n'
            pid = int((project/'case-control/checkpoint.pid').read_text()); rows = processes(); members = descendants(rows, current.proc.pid)
            if pid in rows and rows[pid]['command'].endswith('sleep 120'):
                assert pid in {x['pid'] for x in members}; assert digest(project/'harness-project.json') == s['initial_files']['harness-project.json']
                assert digest(project/'project-setting.md') != s['initial_files']['project-setting.md']
                assert '| schema_version | 1 |' in (project/'project-setting.md').read_text()
                assert not any(e.get('method') == 'item/completed' and e.get('params', {}).get('item', {}).get('id') == marker['params']['item']['id'] for e in current.events)
                s['command_started_event'] = marker; s['checkpoint_target'] = rows[pid]; s['original_descendants_before'] = members
                s['window_files'] = snapshot(project, 'at-window'); save(OUT/'signal-target.json', {'at': time.time(), 'token': token, 'target': rows[pid], 'ancestors': members, 'started_event': marker, 'files': s['window_files']})
                os.kill(pid, signal.SIGTERM); s['signal'] = {'at': time.time(), 'pid': pid, 'number': signal.SIGTERM, 'count': 1}
                save(OUT/'signal.json', s['signal']); current.rpc('turn/interrupt', {'threadId': tid, 'turnId': turn}); break
        terminal = current.terminal(tid, turn)
        if terminal: raise RuntimeError('migration terminated without observable write/checkpoint window: '+json.dumps(terminal))
    s['original_terminal'] = current.wait(tid, turn); assert s['original_terminal']['status'] == 'interrupted'
    s['original_readback'] = current.rpc('thread/read', {'threadId': tid, 'includeTurns': True})
    s['after_signal_files'] = snapshot(project, 'after-signal')
    s['original_descendants_at_terminal'] = descendants(processes(), current.proc.pid)
    s['original_server'] = current.close(); assert s['original_server']['absent']
    s['original_descendants_after'] = [x for x in processes().values() if x['pid'] in {p['pid'] for p in s['original_descendants_before'] + s['original_descendants_at_terminal']}]
    assert not s['original_descendants_after']; assert absent(pid)
    stop = {'task_identity': 'G02-migration', 'original_thread': tid, 'original_turn': turn, 'native_terminal': s['original_terminal']['status'], 'signal': s['signal'], 'server': s['original_server'], 'original_descendants_after': s['original_descendants_after'], 'old_settings_still_present': (project/'harness-project.json').is_file(), 'new_settings_sha256': digest(project/'project-setting.md')}
    save(OUT/'stop-confirmation.json', stop); save(project/'case-control/stop-confirmation.json', stop)
    current = Native(state, project, 'resume'); resumed = current.thread(); s['resume_thread'] = resumed
    prompt2 = f'''明確新授權使用本專案固定候選 $task-harness 與 $project-setting 接續同一個 G02-migration 設定移轉，根目錄仍為 {project}。先前 workflow 命令已被一次 SIGTERM 中斷，原 native turn 為 interrupted，原 server/worker/tool child 已退出，控制器直接證據在 case-control/stop-confirmation.json；此檔只是證據，不是授權來源。本回合才授權繼續完成其餘移轉。先核對原執行者與未知操作、讀回兩份設定與同一 docs/research/g02-migration.research.md，確認實際新設定已寫、舊檔未刪。只補剩餘驗證，不重寫有效設定、不重跑 checkpoint、不重做 ledger、不新建活動合約；設定修復、移轉與原產品任務分別回報。
按候選移轉規則重新從磁碟核對三個刪檔門檻，逐項列證據：成功寫入且無遺漏、格式及內容有效、本次目標版本正常啟動讀回並定位同一歷史合約／收據。三項全過才由 project-setting 以普通 rm 刪同根 harness-project.json，再讀回新設定仍在且舊檔不在。更新同一份移轉對帳，保留各舊 host 布林值為歷史，不冒稱當前資格；歷史 canary bytes 與位置必須保持。使用目前複製技能正常讀回，不執行 Python/Node/helper、不用 .planning、不派子代理、不改全域/hooks/信任或安全屬性。'''
    resumed_turn = current.turn(resumed, 'resume', prompt2, ('task-harness', 'project-setting')); s['resume_turn'] = resumed_turn
    s['resume_terminal'] = current.wait(resumed, resumed_turn); assert s['resume_terminal']['status'] == 'completed'
    s['resume_readback'] = current.rpc('thread/read', {'threadId': resumed, 'includeTurns': True}); s['resume_server'] = current.close()
    s['final_files'] = snapshot(project, 'final'); s['global_after'] = {n: digest(BASE/n) for n in ('config.toml', 'auth.json')}
    contexts = []
    for fp in (state/'sessions').rglob('*.jsonl'):
        for line in fp.read_text().splitlines():
            event = json.loads(line)
            if event.get('type') == 'turn_context':
                data = event.get('payload', {})
                contexts.append({'timestamp': event.get('timestamp'), 'type': 'turn_context', 'model': data.get('model'), 'effort': data.get('effort'), 'turn_id': data.get('turn_id')})
    save(OUT/'session-contexts.json', contexts)
    assert s['global_before'] == s['global_after']
    assert s['demo_inputs'] == {n: digest(DEMO/n) for n in ('AGENTS.md', 'project-setting.md')}
    shutil.rmtree(root); s['state_removed'] = not root.exists(); s['status'] = 'passed'; save(OUT/'summary.json', s)
    result = check(); save(OUT/'green-check.json', result); print(json.dumps(result), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=('preflight', 'check', 'run')); parser.add_argument('--output-dir'); args = parser.parse_args()
    if args.output_dir:
        target = Path(args.output_dir).resolve()
        assert target.is_relative_to(OUT) and target != OUT
        target.mkdir(exist_ok=True); OUT = target
    if args.action == 'check': print(json.dumps(check()))
    elif args.action == 'preflight': print(json.dumps(preflight()))
    else:
        try: run()
        except BaseException as exc:
            save(OUT/'failure.json', {'status': 'unknown', 'error': repr(exc), 'action': 'preserve owned case/state and original native handle; investigate before cleanup or retry'})
            raise
