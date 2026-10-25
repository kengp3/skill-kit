"""Read-only current-tree audit: save field names and paths, never auth values."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
AUTH = Path('/Users/kengp3/.codex/auth.json')
OUT = Path(__file__).resolve().parent
TARGETS = sorted([*ROOT.glob('docs/research/harness-gap-closure-demo-setup-evidence/**/session-contexts.json'), *ROOT.glob('docs/research/harness-gap-closure-strict-effort-evidence/**/session-contexts.json')])

def leaves(value, path=''):
    if isinstance(value, dict):
        for key, item in value.items(): yield from leaves(item, f'{path}.{key}' if path else key)
    elif isinstance(value, list):
        for item in value: yield from leaves(item, path+'[]')
    else: yield path, value

def audit():
    auth_bytes = AUTH.read_bytes()
    needles = [(key, value.encode()) for key, value in leaves(json.loads(auth_bytes)) if isinstance(value, str) and len(value) >= 20 and any(word in key.lower() for word in ('token', 'api_key', 'account_id'))]
    names = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=ACM', 'f15338e...HEAD'], cwd=ROOT).decode().splitlines()
    files = [ROOT/name for name in names if (ROOT/name).is_file() and not (ROOT/name).is_symlink()]
    matches = []
    for path in files:
        content = path.read_bytes()
        for key, needle in needles:
            if needle in content: matches.append({'file': str(path.relative_to(ROOT)), 'auth_field': key})
    fields = [{'file': str(path.relative_to(ROOT)), 'sensitive_field_paths': sorted({key for key, _ in leaves(json.loads(path.read_text())) if any(word in key.lower() for word in ('account', 'user_id', 'token', 'api_key'))})} for path in TARGETS]
    return {'as_of': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(), 'baseline': 'f15338e', 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(), 'auth_source_sha256': hashlib.sha256(auth_bytes).hexdigest(), 'auth_value_count': len(needles), 'scanned_file_count': len(files), 'auth_literal_matches': matches, 'derived_field_audit': fields, 'result': 'failed' if matches or any(x['sensitive_field_paths'] for x in fields) else 'passed'}

if __name__ == '__main__':
    result = audit(); (OUT/sys.argv[1]).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'scanned_file_count', 'auth_value_count')}))
    sys.exit(0 if result['result'] == 'passed' else 1)
