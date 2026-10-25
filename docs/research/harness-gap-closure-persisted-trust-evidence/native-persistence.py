"""G03 maintainer transport only; core task work is performed by the model.
Reuse G01's native stdio seam. Run once; --check reads artifacts without sampling.
"""
import argparse, hashlib, importlib.util, json, os, shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
CASE = Path('/private/tmp/g03-persisted-trust-case')
STATE = Path('/private/tmp/g03-persisted-trust-state')
PRIVATE = Path('/private/tmp/g03-persistence-private')
CANDIDATE = Path('/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0')
MANIFEST = '7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'
G01 = OUT.parent/'harness-gap-closure-demo-setup-evidence/native-demo.py'
spec = importlib.util.spec_from_file_location('g01_native_transport', G01)
native_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(native_module)
native_module.DEMO = CASE
save = native_module.save
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def products(index):
    slug = f'g03-invocation-{index}'
    product = CASE/f'docs/research/{slug}.research.md'
    contract = CASE/f'docs/plans/{slug}.task-contract.md'
    assert product.read_bytes() == f'G03_INVOCATION_{index}_OK\n'.encode(), 'literal product mismatch'
    text = contract.read_text()
    assert text.count('<!-- task-harness-contract:v1 -->') == 1
    assert text.count('<!-- /task-harness-contract -->') == 1
    data = json.loads(text.split('```json', 1)[1].split('```', 1)[0])
    assert data['task_id'] == slug and data['project_root'] == str(CASE)
    assert data['status'] == 'done' and data['authorization']['mode'] == 'execute'
    assert len(data['requirements']) == 1 and data['requirements'][0]['status'] == 'done'
    assert not data['recovery']['unknown_operations']
    assert list((CASE/'docs/plans').glob(slug+'*.task-contract.md')) == [contract]
    return {'product': str(product), 'sha256': sha(product), 'contract': str(contract), 'contract_sha256': sha(contract), 'contract_state': data}


def check():
    assert (CASE/'.codex/hooks.json').read_bytes() == (OUT/'exact-hooks.json').read_bytes()
    expected = json.loads((OUT/'hooks-before.json').read_text())['data'][0]['hooks']
    summaries = []
    for index in (1, 2):
        folder = OUT/f'invocation-{index}'
        terminal = json.loads((folder/'task-terminal.json').read_text())
        assert terminal['status'] == 'completed'
        for name in ('hooks-before.json', 'hooks-after.json'):
            hooks = json.loads((folder/name).read_text())['data'][0]['hooks']
            assert [(x['key'], x['currentHash']) for x in hooks] == [(x['key'], x['currentHash']) for x in expected]
            assert all(x['trustStatus'] == 'trusted' and x['enabled'] for x in hooks)
        summaries.append(products(index))
    runs = [json.loads((OUT/f'invocation-{i}/invocation.json').read_text()) for i in (1, 2)]
    assert runs[0]['server_pid'] != runs[1]['server_pid'] and runs[0]['thread_id'] != runs[1]['thread_id']
    assert all(x['owned_server_exit'] == 0 for x in runs)
    return {'products': summaries, 'two_distinct_invocations': runs}


def export_session(source, folder):
    raw = source.read_bytes(); lines = raw.splitlines(keepends=True)
    target = folder/(source.stem+'.excerpt.jsonl')
    omitted = []; kept = []
    with target.open('wb') as output:
        for number, line in enumerate(lines, 1):
            event = json.loads(line)
            if event.get('type') == 'session_meta':
                omitted.append({'line': number, 'sha256': hashlib.sha256(line).hexdigest(), 'reason': 'complete session_meta omitted; may include account identity'})
            else:
                output.write(line); kept.append(number)
    assert not any(token in target.read_text() for token in ('"access_token"', '"refresh_token"', '"creator_account_id"', '"account_id"', 'sk-proj-'))
    save(folder/'session-excerpt-index.json', {'private_original': str(source), 'original_sha256': hashlib.sha256(raw).hexdigest(), 'original_line_count': len(lines), 'public_excerpt': target.name, 'excerpt_sha256': sha(target), 'exact_retained_source_lines': kept, 'omitted': omitted})


def run():
    assert not PRIVATE.exists(), 'run already exists; recover original handles instead of replay'
    assert sha(CANDIDATE/'runtime-manifest.json') == MANIFEST
    assert (CASE/'.codex/hooks.json').read_bytes() == (OUT/'exact-hooks.json').read_bytes()
    assert json.loads((OUT/'human-approval.json').read_text())['approval_text'] == '已審閱，同意正常信任這五項精確定義'
    assert STATE.stat().st_mode & 0o777 == 0o700 and (STATE/'auth.json').stat().st_mode & 0o777 == 0o600
    PRIVATE.mkdir(mode=0o700)
    baseline = {str(p.relative_to(CASE)): sha(p) for p in CASE.rglob('*') if p.is_file() and '.git' not in p.parts}
    global_before = {n: sha(Path('/Users/kengp3/.codex')/n) for n in ('auth.json', 'config.toml')}
    save(OUT/'run-preconditions.json', {'case': str(CASE), 'state': str(STATE), 'private_raw': str(PRIVATE), 'global_before': global_before, 'case_baseline': baseline, 'transport_source': str(G01), 'transport_sha256': sha(G01), 'hook_trust_bypass': False})
    for index in (1, 2):
        private = PRIVATE/f'invocation-{index}'; private.mkdir(mode=0o700)
        public = OUT/f'invocation-{index}'; public.mkdir()
        n = native_module.Native(STATE, private)
        hooks = n.rpc('hooks/list', {'cwds': [str(CASE)]}); save(public/'hooks-before.json', hooks)
        assert len(hooks['data'][0]['hooks']) == 5 and all(h['trustStatus'] == 'trusted' for h in hooks['data'][0]['hooks'])
        skills = n.rpc('skills/list', {'cwds': [str(CASE)], 'forceReload': True}); save(public/'skills-list.json', skills)
        assert not [s for s in skills['data'][0]['skills'] if s['scope'] == 'user' and s['enabled']]
        for name in native_module.SKILLS:
            assert any(s['path'] == str(CASE/'.agents/skills'/name/'SKILL.md') and s['enabled'] for s in skills['data'][0]['skills'])
        start = n.thread(); save(public/'thread-start.json', start); tid = start['thread']['id']
        assert start['runtimeWorkspaceRoots'] == [str(CASE)] and start['instructionSources'] == [str(CASE/'AGENTS.md')]
        slug = f'g03-invocation-{index}'
        prompt = f'明確使用本專案候選複製的 $task-harness 完成新的無破壞性小任務。唯一已確認根目錄 {CASE}。先讀現行 AGENTS.md、project-setting.md、技能及 provider 規格；不讀或復活 .planning。唯一 task_id={slug}、唯一合約 docs/plans/{slug}.task-contract.md；先成功保存並完整讀回合約，再建立唯一必要成果 T1：docs/research/{slug}.research.md 精確 bytes 一行 G03_INVOCATION_{index}_OK 加一個 LF，不加標題/其他文字。驗證併入 T1，讀回成果精確 bytes 後保存 done 合約並完整讀回。只允許新增這兩個檔案，其餘既有合約/成果/設定/技能全部保留；不建立假 hook 收據或第二份 tracker。不派子代理，不跑 Python/Node/helper/Java/Maven，不安裝或改全域。只用原生工具與 shell 完成核心工作。宿主模型 gpt-6.1-sol/low，requested 與可觀察 host 分開；session/turn ID 只有可觀察值才填，未知 null 並說明。五個正常信任 hooks 的提醒是否實際可見，依真實開發者訊息與工具觀察回報；不得修改信任資料庫、bypass 或重新執行信任操作。若 shell 的 sandbox-exec 在命令開始前失敗，保存真錯誤後可用 scoped require_escalated 只重試本case必要原生命令，不改安全設定。'
        save(public/'invocation.json', {'server_pid': n.proc.pid, 'thread_id': tid, 'state': str(STATE), 'phase': 'running'})
        terminal = n.turn(tid, 'task', prompt, ('task-harness',))
        save(public/'task-terminal.json', terminal)
        assert terminal['status'] == 'completed', 'real turn did not complete; keep state and credentials'
        save(public/'product-check.json', products(index))
        save(public/'hooks-after.json', n.rpc('hooks/list', {'cwds': [str(CASE)]}))
        exit_code = n.close()
        save(public/'invocation.json', {'server_pid': n.proc.pid, 'thread_id': tid, 'turn_id': terminal['id'], 'state': str(STATE), 'phase': 'terminal', 'owned_server_exit': exit_code})
        for name in ('rpc.jsonl', 'server.stderr.log', 'task-prompt.txt'):
            content = (private/name).read_text()
            assert not any(token in content for token in ('"access_token"', '"refresh_token"', '"creator_account_id"', '"account_id"', 'sk-proj-'))
            shutil.copyfile(private/name, public/name)
        export_session(Path(start['thread']['path']), public)
    after = {name: sha(CASE/name) for name in baseline}
    assert after == baseline, 'pre-existing case files changed'
    global_after = {n: sha(Path('/Users/kengp3/.codex')/n) for n in global_before}
    assert global_after == global_before
    save(OUT/'run-result.json', {'check': check(), 'case_baseline_unchanged': True, 'global_before': global_before, 'global_after': global_after, 'global_unchanged': True, 'credentials_still_retained_pending_final_evidence_checks': True})
    print(json.dumps({'run_result': str(OUT/'run-result.json')}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    if args.check: print(json.dumps(check(), ensure_ascii=False))
    else: run()
