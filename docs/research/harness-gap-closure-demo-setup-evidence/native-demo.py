"""G01 maintainer acceptance only; model work has no Python/helper dependency."""
import argparse, hashlib, json, os, selectors, shutil, stat, subprocess, tempfile, time
from pathlib import Path

OUT = Path(__file__).resolve().parent
DEMO = Path('/Users/kengp3/Workspaces/mine/demo-002')
CANDIDATE = Path('/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0')
CODEX = Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
BASE = Path('/Users/kengp3/.codex')
SKILLS = ('define-task', 'project-setting', 'task-harness', 'ai-code-review')
MANIFEST = '7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def fingerprint(path):
    if not path.exists() and not path.is_symlink():
        return {'exists': False}
    s = path.lstat()
    value = {'exists': True, 'type': 'symlink' if path.is_symlink() else 'regular', 'size': s.st_size, 'mode': oct(stat.S_IMODE(s.st_mode))}
    if path.is_symlink():
        value['target'] = os.readlink(path)
    else:
        value['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    return value


def preserved():
    baseline = json.loads((OUT.parent/'harness-gap-closure-baseline-evidence/demo-files.json').read_text())
    differences = {name: {'before': value, 'after': fingerprint(DEMO/name)} for name, value in baseline['files'].items() if fingerprint(DEMO/name) != value}
    return {'count': baseline['file_count'], 'differences': differences}


def check_products():
    assert (DEMO/'docs/research/harness-g01-smoke.research.md').read_bytes() == b'G01_NATIVE_DEMO_OK\n', 'exact model-written product missing/mismatched'
    contracts = list((DEMO/'docs/plans').glob('*.task-contract.md'))
    assert len(contracts) == 1, f'unique contract: {contracts}'
    text = contracts[0].read_text()
    assert text.count('<!-- task-harness-contract:v1 -->') == 1
    data = json.loads(text.split('```json', 1)[1].split('```', 1)[0])
    assert data['task_id'] == 'harness-g01-smoke' and data['status'] == 'done'
    assert data['project_root'] == str(DEMO)
    assert data['requirements'] and all(x['status'] == 'done' for x in data['requirements'])
    assert not data['recovery']['unknown_operations']
    assert not preserved()['differences'], 'pre-existing files changed'
    assert not (DEMO/'harness-project.json').exists()
    return {'product': fingerprint(DEMO/'docs/research/harness-g01-smoke.research.md'), 'contract': str(contracts[0]), 'contract_state': data, 'preservation': preserved()}


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
        self.rpc('initialize', {'clientInfo': {'name': 'g01_native_demo', 'version': '1.0'}, 'capabilities': {'experimentalApi': True}})
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
        return self.rpc('thread/start', {'cwd': str(DEMO), 'runtimeWorkspaceRoots': [str(DEMO)], 'ephemeral': False, 'model': 'gpt-6.1-sol', 'sandbox': 'workspace-write', 'approvalPolicy': 'on-request', 'approvalsReviewer': 'auto_review', 'config': {'model_reasoning_effort': 'low'}})

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


def run():
    assert not (OUT/'rpc.jsonl').exists(), 'refuse to overwrite an existing acceptance run; read saved artifacts instead'
    assert not (DEMO/'docs/plans/harness-g01-smoke.task-contract.md').exists(), 'existing task requires explicit readback, not replay'
    assert DEMO.resolve() == DEMO and OUT.resolve() == OUT
    assert not preserved()['differences']
    assert hashlib.sha256((CANDIDATE/'runtime-manifest.json').read_bytes()).hexdigest() == MANIFEST
    manifest = json.loads((CANDIDATE/'runtime-manifest.json').read_text())
    installed = {}
    for name in SKILLS:
        for rel, digest in manifest['files'].items():
            if rel.startswith('skills/'+name+'/') and '/scripts/' not in rel:
                actual = DEMO/'.agents'/rel
                assert actual.is_file() and not actual.is_symlink() and hashlib.sha256(actual.read_bytes()).hexdigest() == digest, str(actual)
                installed[str(actual.relative_to(DEMO))] = digest
    before = {n: fingerprint(BASE/n) for n in ('auth.json', 'config.toml')}
    save(OUT/'preconditions.json', {'candidate': str(CANDIDATE), 'manifest_sha256': MANIFEST, 'installed': installed, 'existing_preservation': preserved(), 'global_before': before, 'requested_model': 'gpt-6.1-sol', 'requested_effort': 'low', 'runtimeWorkspaceRoots': [str(DEMO)], 'ephemeral': False, 'hook_trust_bypass': False})
    state = Path(tempfile.mkdtemp(prefix='g01-native-state-', dir='/private/tmp')); state.chmod(0o700)
    shutil.copyfile(BASE/'auth.json', state/'auth.json'); (state/'auth.json').chmod(0o600)
    (state/'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = true\n[projects.'+json.dumps(str(DEMO))+']\ntrust_level = "trusted"\n')
    summary = {'state_root': str(state), 'turns': []}; native = None
    try:
        native = Native(state)
        save(OUT/'skills-list.json', native.rpc('skills/list', {'cwds': [str(DEMO)], 'forceReload': True}))
        save(OUT/'hooks-before.json', native.rpc('hooks/list', {'cwds': [str(DEMO)]}))
        start = native.thread(); save(OUT/'thread-start.json', start); tid = start['thread']['id']
        probe = native.turn(tid, 'probe', '唯讀工具啟動 probe：已確認唯一專案根為 '+str(DEMO)+'。只用原生 shell 的 pwd 與 head -n 4 AGENTS.md，回報輸出，不修改任何檔案、不派子代理、不使用 Python/Node/helper。若 sandbox-exec 在命令前失敗，先保存錯誤，再可使用 scoped require_escalated 只重試該唯讀命令。')
        assert probe['status'] == 'completed'
        prompt = '明確使用 $project-setting 初始化已確認根目錄 '+str(DEMO)+' 的自身 project-setting.md，這次指定包含 task-harness，依已複製 task-harness/references/project-settings.md provider Markdown 規格合併最小設定及 Codex 標準 hooks。採 project-setting 預設五種文件分類，再加 harness 規格必要兩列與 schema_version=1；模型列省略，保留目前主責模型。先讀現行 AGENTS.md 及目標設定；不得讀取或復活 .planning 舊流程。技能是固定0.3.0完整複製安裝，scripts 選配未安裝。不得借用其他專案規範、不改既有檔案、不安裝 runtime/plugin/服務/全域設定、不執行 Python/Node/helper、不派子代理。允許本次在 .codex 新增 hooks.json/config.toml；受保護目錄可 scoped require_escalated，只操作這些新增設定。不要改安全屬性、信任資料庫或使用 hook trust bypass，新增 hook 未信任可誠實回報。此回合只設定初始化，不建立任務合約或成果。寫入後重讀設定與 hooks 逐項核對；將設定讀回與宿主信任分開。'
        phase = native.turn(tid, 'phase1-init', prompt, ('project-setting',)); summary['turns'].append({'phase': 'init', 'thread': tid, 'status': phase['status']})
        assert phase['status'] == 'completed'
        for name in ('project-setting.md', '.codex/config.toml', '.codex/hooks.json'):
            dest = OUT/'phase1-artifacts'/name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(DEMO/name, dest)
        save(OUT/'hooks-after-init.json', native.rpc('hooks/list', {'cwds': [str(DEMO)]}))
        start2 = native.thread(); save(OUT/'thread-start-task.json', start2); tid2 = start2['thread']['id']
        task = '明確使用 $task-harness 執行一個無破壞性小任務。已確認唯一根目錄 '+str(DEMO)+'，先讀現行 AGENTS.md、project-setting.md 與已安裝技能，依 harness provider 規格重讀檢查設定；不借用其他 repo。唯一 task_id=harness-g01-smoke，唯一合約固定 docs/plans/harness-g01-smoke.task-contract.md，按規範先成功保存且讀回完整合約，再產出 docs/research/harness-g01-smoke.research.md 精確 bytes 一行 G01_NATIVE_DEMO_OK 加一個 LF，不加標題、空白或註解。只有一個必要成果 T1（含驗證），實際讀回驗收後再保存 done 合約並重讀；不要另建第二份 tracker 或假 hook 收據。允許這兩個新增檔案，其他既有檔案與設定保留。不可讀/執行 .planning 舊流程，不跑 Java/Maven、不使用 Python/Node/helper、不安裝服務/套件、不派子代理。模型/強度由原生主責 gpt-6.1-sol/low，記 requested 與可觀測 host 分開，不假裝知道 provider weights。宿主 session/turn 身分僅填可觀測值，沒有就 null並說明，不能造 ID。hook 若未信任，使用同一合約的主動檢查接手，誠實保存缺口與實際讀回證據，不修改信任 db、不 bypass。'
        phase = native.turn(tid2, 'phase2-task', task, ('task-harness',)); summary['turns'].append({'phase': 'task', 'thread': tid2, 'status': phase['status']})
        assert phase['status'] == 'completed'
        summary['acceptance'] = check_products()
        save(OUT/'hooks-final.json', native.rpc('hooks/list', {'cwds': [str(DEMO)]}))
    except Exception as exc:
        summary['error'] = str(exc)
        raise
    finally:
        if native: summary['owned_server_exit'] = native.close()
        contexts = []
        for fp in (state/'sessions').rglob('*.jsonl'):
            for line in fp.read_text().splitlines():
                event = json.loads(line)
                if event.get('type') in ('session_meta', 'turn_context'): contexts.append(event)
        save(OUT/'session-contexts.json', contexts)
        names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=DEMO).decode().split('\0')
        baseline = json.loads((OUT.parent/'harness-gap-closure-baseline-evidence/demo-files.json').read_text())['files']
        added = {n: fingerprint(DEMO/n) for n in names if n and n not in baseline}
        save(OUT/'added-files.json', added)
        for name in added:
            if name.startswith('.agents/'): continue
            source = DEMO/name
            if source.is_file() and not source.is_symlink():
                dest = OUT/'final-artifacts'/name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, dest)
        summary['preservation'] = preserved(); summary['global_after'] = {n: fingerprint(BASE/n) for n in before}
        summary['global_unchanged'] = summary['global_after'] == before
        summary['demo_head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=DEMO).decode().strip()
        summary['demo_status'] = subprocess.check_output(['git', 'status', '--short'], cwd=DEMO).decode()
        shutil.rmtree(state); summary['isolated_state_and_credentials_removed'] = not state.exists()
        save(OUT/'summary.json', summary)
        print(json.dumps({'summary': str(OUT/'summary.json'), 'error': summary.get('error'), 'global_unchanged': summary['global_unchanged']}), flush=True)


def verify_readback():
    """Fresh clean context accepts existing artifacts; never repeats product mutations."""
    out = OUT/'clean-readback'; out.mkdir(exist_ok=False)
    before = {n: fingerprint(BASE/n) for n in ('auth.json', 'config.toml')}
    products_before = check_products()
    state = Path(tempfile.mkdtemp(prefix='g01-readback-state-', dir='/private/tmp')); state.chmod(0o700)
    shutil.copyfile(BASE/'auth.json', state/'auth.json'); (state/'auth.json').chmod(0o600)
    config = 'cli_auth_credentials_store = "file"\n[features]\nhooks = true\n[projects.'+json.dumps(str(DEMO))+']\ntrust_level = "trusted"\n'
    for path in ('archify', 'define-task', 'project-setting'):
        config += '\n[[skills.config]]\npath = '+json.dumps('/Users/kengp3/.agents/skills/'+path+'/SKILL.md')+'\nenabled = false\n'
    (state/'config.toml').write_text(config); (out/'isolated-config.toml').write_text(config)
    native = None; summary = {'state_root': str(state)}
    try:
        native = Native(state, out)
        skills = native.rpc('skills/list', {'cwds': [str(DEMO)], 'forceReload': True}); save(out/'skills-list.json', skills)
        items = skills['data'][0]['skills']
        assert not [x for x in items if x['scope'] == 'user' and x['enabled']], 'user skill remains enabled'
        assert all(any(x['path'] == str(DEMO/'.agents/skills'/name/'SKILL.md') and x['enabled'] for x in items) for name in SKILLS)
        save(out/'plugins-list.json', native.rpc('plugin/list', {'cwds': [str(DEMO)], 'forceRefetch': False, 'marketplaceKinds': ['local']}))
        save(out/'hooks-list.json', native.rpc('hooks/list', {'cwds': [str(DEMO)]}))
        start = native.thread(); save(out/'thread-start.json', start)
        assert start['runtimeWorkspaceRoots'] == [str(DEMO)] and start['instructionSources'] == [str(DEMO/'AGENTS.md')]
        prompt = '明確使用本專案複製的 $task-harness，唯讀驗收既有唯一合約 docs/plans/harness-g01-smoke.task-contract.md 與成果 docs/research/harness-g01-smoke.research.md。這是先前 G01 已 done 任務的獨立驗收，僅授權讀回；不可接手重寫合約、設定或成果，不重做已完成副作用、不建立任何檔案/新tracker、不派子代理、不跑 Python/Node/helper/Java/Maven。根目錄已確認為 '+str(DEMO)+'。讀現行 AGENTS.md 與 project-setting.md（不得使用 .planning），核對 provider 規格的有效設定、唯一合約標記/JSON/required fields、task_id=harness-g01-smoke、全部必要成果 done，以及成果精確為 G01_NATIVE_DEMO_OK 加一個 LF。用系統 shell cmp/od 或等效原生工具讀回 bytes。請檢查 hooks 目前未信任的限制，只回報觀察，不改信任db、不 bypass。只使用本專案 .agents/skills 實際複製來源；其他 user skills 已在隔離state停用。'
        phase = native.turn(start['thread']['id'], 'readback', prompt, ('task-harness',))
        assert phase['status'] == 'completed'; summary['phase'] = phase
        assert check_products() == products_before, 'read-only acceptance changed product/contract'
        summary['acceptance'] = check_products()
    except Exception as exc:
        summary['error'] = str(exc); raise
    finally:
        if native: summary['owned_server_exit'] = native.close()
        contexts = []
        for fp in (state/'sessions').rglob('*.jsonl'):
            for line in fp.read_text().splitlines():
                event = json.loads(line)
                if event.get('type') in ('session_meta', 'turn_context'): contexts.append(event)
        save(out/'session-contexts.json', contexts)
        summary['global_after'] = {n: fingerprint(BASE/n) for n in before}; summary['global_unchanged'] = before == summary['global_after']
        shutil.rmtree(state); summary['isolated_state_and_credentials_removed'] = not state.exists()
        save(out/'summary.json', summary)
        print(json.dumps({'clean_readback': str(out), 'error': summary.get('error')}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check-products', action='store_true'); parser.add_argument('--verify-readback', action='store_true'); args = parser.parse_args()
    if args.check_products: print(json.dumps(check_products(), ensure_ascii=False))
    elif args.verify_readback: verify_readback()
    else: run()
