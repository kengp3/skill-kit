import datetime
import json
import os
import pathlib
import subprocess
import sys

root = pathlib.Path('/private/tmp/ai-review-real-20261009/S3')
out = root / 'output'
records = []
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

def run(label, argv, extra_env=None):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(argv, cwd=root, env={**env, **(extra_env or {})}, capture_output=True)
    (out/'logs'/f'{label}.stdout').write_bytes(proc.stdout)
    (out/'logs'/f'{label}.stderr').write_bytes(proc.stderr)
    record = dict(label=label, argv=argv, cwd=str(root), env={'PYTHONDONTWRITEBYTECODE':'1', **(extra_env or {})}, started=started, exit_code=proc.returncode, stdout=f'logs/{label}.stdout', stderr=f'logs/{label}.stderr')
    records.append(record)
    print(json.dumps(record))
    return proc

(out/'start-clock.json').write_text('{"current_time":"2026-10-09 11:30:38 UTC","source":"clock__curr_time first call, before business sources"}\n')
git = ['git', '-C', str(root/'repo')]
run('status', git+['status', '--porcelain=v1', '--untracked-files=all'])
run('refs', git+['rev-parse', 'review-base', 'review-head'])
run('merge-base', git+['merge-base', 'review-base', 'review-head'])
run('files', git+['ls-tree', '-r', '--name-only', 'review-head'])
base = '3159b0975832c88522dfec4d13adf851ec8d6ada'
head = 'f3ea1892ae704f155c2f837bde3e2312032af50f'
run('name-status', git+['diff', '--name-status', f'{base}...{head}'])
run('patch', git+['diff', '--no-ext-diff', f'{base}...{head}'])
for name, commit in [('base',base),('head',head)]:
    target = out/'snapshots'/name
    target.mkdir(parents=True, exist_ok=True)
    for file in ['api.py','paging.py']:
        p = run(f'{name}-{file}', git+['show', f'{commit}:{file}'])
        assert p.returncode == 0
        (target/file).write_bytes(p.stdout)
        assert (root/name/file).read_bytes() == p.stdout, f'{name}/{file} raw snapshot mismatch'
        if name == 'head':
            assert (root/'repo'/file).read_bytes() == p.stdout
run('callers', ['rg','-n','after|page|limit',str(out/'snapshots')])
run('python-version', [sys.executable,'--version'])
run('git-version', ['git','--version'])
for name in ['base','head']:
    run(f'test-{name}', [sys.executable, str(out/'tmp/test_review.py'), str(out/'snapshots'/name)])
    run(f'probe-{name}', [sys.executable,str(root/'probe.py')], {'PYTHONPATH':str(out/'snapshots'/name)})
(out/'commands.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
