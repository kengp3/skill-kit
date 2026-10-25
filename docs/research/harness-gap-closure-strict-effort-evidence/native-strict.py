"""G04 maintainer-only native trials. No helper is required by the product model."""
import argparse, hashlib, json, os, selectors, shutil, subprocess, tempfile, time
from pathlib import Path

OUT = Path(__file__).resolve().parent
DEMO = Path('/Users/kengp3/Workspaces/mine/demo-002')
CANDIDATE = Path('/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0')
CODEX = Path('/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
BASE = Path('/Users/kengp3/.codex')
SKILLS = ('define-task', 'project-setting', 'task-harness', 'ai-code-review')
MANIFEST = '7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'


def context_metadata(event):
    """Export only acceptance metadata; never copy unknown session/account fields."""
    fields = {
        'session_meta': ('id', 'session_id', 'timestamp', 'cwd', 'cli_version', 'originator', 'model_provider', 'thread_source', 'parent_thread_id', 'agent_path', 'agent_nickname', 'agent_role'),
        'turn_context': ('turn_id', 'root_turn_id', 'cwd', 'model', 'effort'),
    }
    kind = event.get('type')
    if kind not in fields: return None
    data = event.get('payload', {})
    payload = {key: data[key] for key in fields[kind] if key in data and isinstance(data[key], (str, int, bool, type(None)))}
    roots = data.get('runtime_workspace_roots')
    if isinstance(roots, list) and all(isinstance(p, str) for p in roots): payload['runtime_workspace_roots'] = roots
    source = data.get('source')
    if isinstance(source, str): payload['source'] = source
    elif isinstance(source, dict) and isinstance(source.get('subagent'), dict):
        subagent = source['subagent']; selected = {}
        if isinstance(subagent.get('other'), str): selected['other'] = subagent['other']
        spawn = subagent.get('thread_spawn')
        if isinstance(spawn, dict):
            selected['thread_spawn'] = {key: spawn[key] for key in ('parent_thread_id', 'depth', 'agent_path', 'agent_nickname', 'agent_role') if key in spawn and isinstance(spawn[key], (str, int, type(None)))}
        payload['source'] = {'subagent': selected}
    return {'timestamp': event.get('timestamp'), 'type': kind, 'payload': payload}


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Native:
    def __init__(self, project, state, out):
        self.project = project; self.out = out; self.counter = 0; self.buffer = b''
        self.raw = (out/'rpc.jsonl').open('w'); self.err = (out/'server.stderr.log').open('w')
        env = os.environ.copy(); env['CODEX_HOME'] = str(state)
        for key in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_ACCESS_TOKEN', 'CHATGPT_AUTH_TOKEN', 'CODEX_REMOTE_TOKEN'): env.pop(key, None)
        self.proc = subprocess.Popen([str(CODEX), 'app-server', '--stdio'], cwd=project, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.err)
        self.sel = selectors.DefaultSelector(); self.sel.register(self.proc.stdout, selectors.EVENT_READ)
        self.rpc('initialize', {'clientInfo': {'name': 'g04_native_strict', 'version': '1.0'}, 'capabilities': {'experimentalApi': True}})
        self.send({'method': 'initialized', 'params': {}})

    def send(self, message):
        self.log('client', message); self.proc.stdin.write((json.dumps(message)+'\n').encode()); self.proc.stdin.flush()

    def log(self, direction, message):
        self.raw.write(json.dumps({'at': time.time(), 'direction': direction, 'message': message}, ensure_ascii=False)+'\n'); self.raw.flush()

    def read(self, seconds=30):
        deadline = time.monotonic()+seconds
        while time.monotonic() < deadline:
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                if not line: continue
                msg = json.loads(line); self.log('server', msg)
                if 'id' in msg and 'method' in msg:
                    self.send({'id': msg['id'], 'error': {'code': -32601, 'message': 'G04 controller supplies no interactive user decisions'}})
                return msg
            for key, _ in self.sel.select(.2):
                data = os.read(key.fd, 65536)
                if not data: raise RuntimeError('owned native server EOF')
                self.buffer += data
        raise TimeoutError('observation window; native handle unchanged')

    def rpc(self, method, params):
        self.counter += 1; rid = self.counter; self.send({'id': rid, 'method': method, 'params': params})
        while True:
            try: msg = self.read()
            except TimeoutError: continue
            if msg.get('id') == rid:
                if 'error' in msg: raise RuntimeError(json.dumps(msg, ensure_ascii=False))
                return msg['result']

    def thread(self):
        return self.rpc('thread/start', {'cwd': str(self.project), 'runtimeWorkspaceRoots': [str(self.project)], 'ephemeral': False, 'model': 'gpt-6.1-sol', 'sandbox': 'workspace-write', 'approvalPolicy': 'on-request', 'approvalsReviewer': 'auto_review', 'config': {'model_reasoning_effort': 'low'}})

    def turn(self, tid, prompt, effort='low', skills=True):
        (self.out/'prompt.txt').write_text(prompt)
        inputs = [{'type': 'text', 'text': prompt}]
        if skills: inputs.append({'type': 'skill', 'name': 'task-harness', 'path': str(self.project/'.agents/skills/task-harness/SKILL.md')})
        result = self.rpc('turn/start', {'threadId': tid, 'input': inputs, 'effort': effort}); turn = result['turn']['id']
        live = {'server_pid': self.proc.pid, 'thread_id': tid, 'turn_id': turn, 'project': str(self.project), 'state': 'running'}
        save(self.out/'live.json', live); print(json.dumps(live), flush=True)
        while True:
            try: msg = self.read()
            except TimeoutError:
                print(json.dumps({'turn': turn, 'observation': 'same handle still pending'}), flush=True); continue
            if msg.get('method') == 'turn/completed' and msg.get('params', {}).get('threadId') == tid and msg['params']['turn']['id'] == turn:
                live.update(state='terminal', status=msg['params']['turn']['status']); save(self.out/'live.json', live)
                return msg['params']['turn']

    def close(self):
        self.proc.stdin.close()
        try: self.proc.wait(15)
        except subprocess.TimeoutExpired: self.proc.terminate(); self.proc.wait(10)
        self.sel.close(); self.raw.close(); self.err.close()
        return self.proc.returncode


def run(case):
    out = OUT/case; out.mkdir(exist_ok=False)
    assert subprocess.check_output([str(CODEX), '--version']).decode().strip() == 'codex-cli 0.164.0'
    assert sha(CANDIDATE/'runtime-manifest.json') == MANIFEST
    manifest = json.loads((CANDIDATE/'runtime-manifest.json').read_text())
    assert all(sha(CANDIDATE/p) == digest for p, digest in manifest['files'].items())
    before = {n: sha(BASE/n) for n in ('auth.json', 'config.toml')}
    root = Path(tempfile.mkdtemp(prefix='g04-'+case+'-', dir='/private/tmp')); root.chmod(0o700)
    project = root/'project'; state = root/'state'; project.mkdir(mode=0o700); state.mkdir(mode=0o700)
    shutil.copyfile(BASE/'auth.json', state/'auth.json'); (state/'auth.json').chmod(0o600)
    config = 'cli_auth_credentials_store = "file"\n[features]\nhooks = false\n[projects.'+json.dumps(str(project))+']\ntrust_level = "trusted"\n'
    for name in ('archify', 'define-task', 'project-setting'):
        config += '\n[[skills.config]]\npath = '+json.dumps('/Users/kengp3/.agents/skills/'+name+'/SKILL.md')+'\nenabled = false\n'
    (state/'config.toml').write_text(config); (out/'isolated-config.toml').write_text(config)
    for name in SKILLS: shutil.copytree(CANDIDATE/'skills'/name, project/'.agents/skills'/name, ignore=shutil.ignore_patterns('scripts', '__pycache__'))
    shutil.copyfile(DEMO/'AGENTS.md', project/'AGENTS.md')
    settings = (DEMO/'project-setting.md').read_text()
    settings += ('| model.default | [gpt-6.1-sol;minimal, gpt-6-sol;low] |\n' if case == 'first-only' else '| model.default | [gpt-6.1-sol;minimal, gpt-6-sol;minimal] |\n')
    (project/'project-setting.md').write_text(settings); (project/'preserve.txt').write_bytes(b'KEEP_EXISTING_CONTENT\n')
    initial = (project/'project-setting.md').read_bytes()
    save(out/'preconditions.json', {'candidate_manifest_sha256': MANIFEST, 'candidate': str(CANDIDATE), 'case_root': str(root), 'project': str(project), 'global_before_sha256': before, 'demo_agents_sha256': sha(DEMO/'AGENTS.md'), 'demo_settings_sha256': sha(DEMO/'project-setting.md'), 'controller_fixture': 'Copies current demo AGENTS and document rules; adds case model.default. This is input setup, not observed model behavior.', 'expectations': {'first-only': 'one gpt-6-sol/low child; exact G04_STRICT_WORKER_OK LF; one done contract', 'all-agents': 'T1 blocked; zero child calls; T2 exact G04_INDEPENDENT_READY LF', 'provider-probe': 'one protocol-valid metadata-unsupported native effort request; classify actual rejection layer'}})
    native = None; summary = {'case': case, 'state_root': str(state)}
    try:
        native = Native(project, state, out)
        skills = native.rpc('skills/list', {'cwds': [str(project)], 'forceReload': True}); save(out/'skills-list.json', skills)
        items = skills['data'][0]['skills']
        assert not [x for x in items if x['scope'] == 'user' and x['enabled']]
        assert all(any(x['path'] == str(project/'.agents/skills'/n/'SKILL.md') and x['enabled'] for x in items) for n in SKILLS)
        plugins = native.rpc('plugin/list', {'cwds': [str(project)], 'forceRefetch': False, 'marketplaceKinds': ['local']}); save(out/'plugins-list.json', plugins)
        save(out/'hooks-list.json', native.rpc('hooks/list', {'cwds': [str(project)]}))
        metadata = native.rpc('model/list', {}); save(out/'model-list.json', metadata)
        supported = {x['id']: {e['reasoningEffort'] for e in x['supportedReasoningEfforts']} for x in metadata['data']}
        assert 'minimal' not in supported['gpt-6.1-sol'] and 'minimal' not in supported['gpt-6-sol'] and 'low' in supported['gpt-6-sol']
        save(project/'host-model-metadata.json', metadata)
        start = native.thread(); save(out/'thread-start.json', start); tid = start['thread']['id']
        assert start['runtimeWorkspaceRoots'] == [str(project)] and start['instructionSources'] == [str(project/'AGENTS.md')]
        common = '已確認唯一根目錄 '+str(project)+'。這是隔離自有案例，明確啟用固定候選 $task-harness，先讀 AGENTS.md、project-setting.md 及技能模型規則，再依本案指示建立同一份完整合約並讀回。hooks停用，使用主動檢查，不改hooks或信任。host-model-metadata.json 是本次原生 model/list 的原始輸出，派工前讀它做強度preflight；不得故意發送metadata已判不合格的模型請求。保留所有初始檔案與長期設定。只允許新增指定唯一合約與成果，不安裝服務/套件、不用Python/Node/helper、不碰其他root。普通原生命令若遭sandbox-exec啟動前拒絕，可 scoped require_escalated 僅重試本case命令。任務分工明確授權原生子agent，worker用fork_turns=none及自足輸入。requested與observed分開，實際模型/強度未知就null，請求值不冒稱實際值。'
        if case == 'first-only':
            prompt = common+' 任務ID g04-first-only，唯一合約 docs/plans/g04-first-only.task-contract.md。只有T1：必須由一個獨立worker唯讀核對 preserve.txt 精確內容KEEP_EXISTING_CONTENT加LF，主責驗收該真實worker回報後寫 docs/research/strict-worker.research.md 精確一行G04_STRICT_WORKER_OK加LF。本次指定候選[gpt-6.1-sol;minimal, gpt-6-sol;low]，強度不可變更的strict限制僅適用首選gpt-6.1-sol的minimal；後續gpt-6-sol/low明確合格可用，不能把限制擴大成全候選只能minimal。若首選metadata不支援就略過，不用主責接手滿足獨立worker要求，使用合格後續候選真正派工；保存實際handle、原要求、略過原因、host可觀測結果與證據。完成後讀回成果與同一合約，T1才可done，不建立第二合約。'
        elif case == 'all-agents':
            prompt = common+' 任務ID g04-all-agents，唯一合約 docs/plans/g04-all-agents.task-contract.md。有互不相依T1與T2。T1必須獨立worker唯讀核對preserve.txt後才能產生 docs/research/strict-worker.research.md；候選[gpt-6.1-sol;minimal,gpt-6-sol;minimal]，專案預設也就是同一清單。本次所有子agent的強度只能minimal，嚴格不可變更，限制涵蓋T1所有候選與末段回退；metadata全不合格則T1保持blocked，保存原因與未滿足條件，不發任何違規spawn，不以主責接手滿足T1，不生成依賴T1的成果。T2不依賴T1、不要求worker，由目前主責直接完成 docs/research/independent-ready.research.md 精確一行G04_INDEPENDENT_READY加LF並讀回，可done；這個子agent限制不限制主責T2。完成能做的T2後保存同一合約，指出T1需要的最小使用者決定；本案不授權改強度或設定。'
        else:
            prompt = '這是維護者獨立唯讀native effort probe；只回覆 G04_PROVIDER_PROBE，不執行工具、不派agent、不讀寫檔案。'
        summary['terminal'] = native.turn(tid, prompt, effort='minimal' if case == 'provider-probe' else 'low', skills=case != 'provider-probe')
        save(out/'thread-final.json', native.rpc('thread/read', {'threadId': tid, 'includeTurns': True}))
    except Exception as exc:
        summary['error'] = str(exc)
        print(json.dumps({'case': case, 'error': str(exc)}), flush=True)
    finally:
        if native: summary['owned_server_exit'] = native.close()
        contexts = []; tool_records = []
        for fp in (state/'sessions').rglob('*.jsonl'):
            for line in fp.read_text().splitlines():
                event = json.loads(line)
                if event.get('type') in ('session_meta', 'turn_context'): contexts.append(context_metadata(event))
                if event.get('type') == 'response_item' and event.get('payload', {}).get('type') in ('function_call', 'function_call_output', 'custom_tool_call', 'custom_tool_call_output'): tool_records.append({'file': str(fp.relative_to(state)), **event})
        save(out/'session-contexts.json', contexts)
        save(out/'session-tool-records.json', tool_records)
        shutil.copytree(project, out/'artifacts', ignore=shutil.ignore_patterns('.agents', '.git'))
        summary['settings_unchanged'] = (project/'project-setting.md').read_bytes() == initial
        summary['preserve_unchanged'] = (project/'preserve.txt').read_bytes() == b'KEEP_EXISTING_CONTENT\n'
        summary['global_after_sha256'] = {n: sha(BASE/n) for n in before}; summary['global_unchanged'] = summary['global_after_sha256'] == before
        if native and native.proc.poll() is not None:
            (state/'auth.json').unlink(); summary['credentials_removed'] = not (state/'auth.json').exists()
        else: summary['credentials_removed'] = False
        save(out/'summary.json', summary)
        print(json.dumps({'case': case, 'summary': str(out/'summary.json'), 'terminal': summary.get('terminal', {}).get('status'), 'error': summary.get('error')}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('case', nargs='?', choices=['first-only', 'all-agents', 'provider-probe']); parser.add_argument('--export-contexts', nargs=2, metavar=('INPUT', 'OUTPUT')); args = parser.parse_args()
    if args.export_contexts:
        source, target = map(Path, args.export_contexts)
        save(target, [context_metadata(e) for e in json.loads(source.read_text()) if e.get('type') in ('session_meta', 'turn_context')])
    elif args.case: run(args.case)
    else: parser.error('case or --export-contexts is required')
