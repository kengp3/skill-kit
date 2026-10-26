"""Maintainer-only ZIP preparation/checks; never launches Codex or a trial."""
import argparse
import copy
import datetime
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
PRODUCT = Path('/Users/kengp3/Workspaces/mine/simple-skills')
DEMO = Path('/Users/kengp3/Workspaces/mine/demo-002')
CANDIDATE = PRODUCT / 'dist/candidates/kengp3-harness-0.3.0'
CANDIDATE_HASH = '7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e'
KIT = 'manual-kit-20261026-4a9d7f20'
CASES = {
    'stop': {'case_id': 'G07-STOP-20261026-4a9d7f20', 'token': 'G07_STOP_4a9d7f20_6e37c1a8',
             'proposed_root': '/Users/g07stop/Workspaces/harness-g07-stop'},
    'model': {'case_id': 'G07-MODEL-20261026-7b3e2d91', 'token': 'G07_MODEL_7b3e2d91_a64c802f',
              'proposed_root': '/Users/g07model/Workspaces/harness-g07-model'},
}
BASE_FILES = ('AGENTS.md', 'project-setting.md', '.codex/config.toml', '.codex/hooks.json')
SECRET_PATTERN = re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?im:^\s*["\']?(?:access_token|refresh_token|client_secret|api_key|trusted_hash)["\']?\s*[:=])')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_entry(name):
    p = PurePosixPath(name)
    if not name or '\\' in name or ':' in name or p.is_absolute() or any(x in ('', '.', '..') for x in name.split('/')):
        raise ValueError('unsafe ZIP entry: ' + name)


def source_bytes(path):
    if path.is_symlink() or path.resolve() != path or not path.is_file():
        raise ValueError('source must be a real file: ' + str(path))
    data = path.read_bytes()
    if SECRET_PATTERN.search(data):
        raise ValueError('credential/trust material pattern in source: ' + str(path))
    return data


def collect_sources():
    manifest_path = CANDIDATE / 'runtime-manifest.json'
    manifest_bytes = source_bytes(manifest_path)
    if digest(manifest_bytes) != CANDIDATE_HASH:
        raise ValueError('candidate manifest hash mismatch')
    manifest = json.loads(manifest_bytes)
    selected = {p: h for p, h in manifest['files'].items()
                if p.startswith('skills/') and 'scripts' not in PurePosixPath(p).parts}
    if len(selected) != 21 or {PurePosixPath(p).parts[1] for p in selected} != {'define-task', 'project-setting', 'task-harness', 'ai-code-review'}:
        raise ValueError('unexpected runtime inventory')
    sources = {}
    for rel, expected in sorted(selected.items()):
        data = source_bytes(CANDIDATE / rel)
        if digest(data) != expected:
            raise ValueError('candidate entry hash mismatch: ' + rel)
        sources['.agents/' + rel] = (data, {'kind': 'candidate', 'path': str(CANDIDATE / rel), 'sha256': expected})
    for rel in BASE_FILES:
        data = source_bytes(DEMO / rel)
        sources[rel] = (data, {'kind': 'demo-current-base', 'path': str(DEMO / rel), 'sha256': digest(data)})
    # Only the known project wiring is portable, never a user config/trust DB.
    if sources['.codex/config.toml'][0] != b'[features]\nhooks = true\n':
        raise ValueError('project config changed; review before packaging')
    hooks = json.loads(sources['.codex/hooks.json'][0])['hooks']
    expected_hooks = {}
    for skill in ('project-setting', 'task-harness'):
        for event, definitions in json.loads(sources[f'.agents/skills/{skill}/assets/codex-hooks.json'][0])['hooks'].items():
            expected_hooks.setdefault(event, []).extend(definitions)
    if hooks != expected_hooks:
        raise ValueError('project hooks differ from candidate merged definitions')
    return sources, manifest_bytes


def archive_bytes(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, (data, _) in sorted(entries.items()):
            safe_entry(name)
            info = zipfile.ZipInfo(name, (2026, 10, 26, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return output.getvalue()


def verify_archive(data, record, expected):
    if digest(data) != record['sha256']:
        raise ValueError('ZIP hash mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        for info in archive.infolist():
            safe_entry(info.filename)
            if stat.S_IFMT(info.external_attr >> 16) != stat.S_IFREG:
                raise ValueError('non-regular ZIP entry')
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError('ZIP inventory mismatch')
        if {e['path'] for e in record['entries']} != set(expected) or len(record['entries']) != len(names):
            raise ValueError('manifest inventory mismatch')
        for entry in record['entries']:
            actual = archive.read(entry['path'])
            original, source = expected[entry['path']]
            if actual != original or digest(actual) != entry['sha256'] or entry['source'] != source or digest(original) != source['sha256']:
                raise ValueError('entry/source hash or bytes mismatch')


def write_new(path, data):
    with path.open('xb') as stream:
        stream.write(data)


def case_entries(sources, kind, case):
    folder = Path(case['proposed_root']).name
    entries = {folder + '/' + rel: value for rel, value in sources.items()}
    literals = {'preserve.txt': b'G07_PRESERVE_ONCE\n'}
    if kind == 'stop':
        literals['ledger.txt'] = b'G07_LEDGER_ONCE\n'
    for rel, data in literals.items():
        entries[folder + '/' + rel] = (data, {'kind': 'literal-canary', 'utf8': data.decode(), 'sha256': digest(data)})
    return entries


def verify_prepared(output):
    manifest = json.loads((output / 'manifest.json').read_text())
    if manifest['candidate_manifest_sha256'] != CANDIDATE_HASH or set(manifest['archives']) != set(CASES):
        raise ValueError('prepared manifest candidate/cases mismatch')
    sources, _ = collect_sources()
    counts = {}
    for kind, case in CASES.items():
        record = manifest['archives'][kind]
        if any(record[key] != value for key, value in case.items()) or record['file'] != kind + '-input.zip':
            raise ValueError('reserved case identity mismatch')
        expected = case_entries(sources, kind, case)
        verify_archive((output / record['file']).read_bytes(), record, expected)
        counts[kind] = len(expected)
    for item in manifest['prompts']:
        if digest(source_bytes(output / item['file'])) != item['sha256'] or digest(source_bytes(Path(item['template']))) != item['template_sha256']:
            raise ValueError('prepared prompt/template changed')
    return {'kind': 'maintainer preparation/source readback only; no native trial', 'result': 'passed',
            'archive_entries': counts, 'source_files_unchanged': len(sources), 'candidate_manifest_matches': True,
            'prompt_template_hashes_match': True, 'credential_pattern_scan': 'passed on allowlisted source bytes',
            'accounts_created': False, 'ui_trials_executed': False}


def build(output):
    if output.exists() or output.is_symlink():
        raise FileExistsError('refusing existing output: ' + str(output))
    sources, candidate_bytes = collect_sources()
    records, files, prompt_sources = {}, {}, []
    for kind, case in CASES.items():
        assert all(re.fullmatch(r'[A-Za-z0-9_-]+', case[key]) for key in ('case_id', 'token'))
        entries = case_entries(sources, kind, case)
        data = archive_bytes(entries)
        record = {'file': kind + '-input.zip', **case, 'environment_status': 'proposed/not observed; OS account not created; name availability unproved',
                  'observed_root': None, 'observed_uid': None, 'observed_state': None, 'sha256': digest(data),
                  'entries': [{'path': name, 'sha256': digest(value[0]), 'bytes': len(value[0]), 'source': value[1]} for name, value in sorted(entries.items())]}
        verify_archive(data, record, entries)
        records[kind] = record
        files[record['file']] = data
        for name in (('stop-start', 'stop-resume') if kind == 'stop' else ('model-start', 'model-continue')):
            template = source_bytes(HERE / (name + '.prompt.txt'))
            body = template.decode().split('\n\n', 1)[1]
            for key, value in {'CASE_ROOT': case['proposed_root'], 'CASE_ID': case['case_id'], 'TOKEN': case['token']}.items():
                body = body.replace('{' + key + '}', value)
            header = f'候選輸入，尚未執行。case={case["case_id"]}；reserved token={case["token"]}。root 是建議值，帳號未建且名稱可用性未證；先實測 UID/HOME/state/同 chat 原生紀錄/來源/可寫範圍與觀測資格，實際 root 不符先重新確認，資格成立後使用者才可送出。STOP_PROOF/UI_PROOF 仍待真實證據，不能預填。\n\n'
            rendered = (header + body).encode()
            files[name + '.prompt.txt'] = rendered
            prompt_sources.append({'file': name + '.prompt.txt', 'sha256': digest(rendered), 'template': str(HERE / (name + '.prompt.txt')), 'template_sha256': digest(template)})
    for path, (_, source) in sources.items():
        if digest(source_bytes(Path(source['path']))) != source['sha256']:
            raise ValueError('source changed during preparation: ' + path)
    if source_bytes(CANDIDATE / 'runtime-manifest.json') != candidate_bytes:
        raise ValueError('candidate manifest changed during preparation')
    manifest = {'kind': 'portable input preparation only; no trial/qualification result',
                'prepared_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'candidate_root': str(CANDIDATE), 'candidate_manifest_sha256': CANDIDATE_HASH,
                'demo_base_root': str(DEMO), 'source_preservation': '25 allowlisted source files and candidate manifest unchanged across preparation',
                'archives': records, 'prompts': prompt_sources,
                'credential_scope': 'exact allowlist plus credential/private-key/trust-assignment pattern scan; no auth/keychain/session files read',
                'runtime_requirements': 'Finder extraction; no Python/Node/helper required by operator or core harness'}
    files['manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    output.mkdir()
    for name, data in files.items():
        write_new(output / name, data)
    return manifest


def self_check():
    expected = {'sample/preserve.txt': (b'KNOWN\n', {'kind': 'literal-canary', 'utf8': 'KNOWN\n', 'sha256': digest(b'KNOWN\n')})}
    data = archive_bytes(expected)
    record = {'sha256': digest(data), 'entries': [{'path': name, 'sha256': digest(value[0]), 'source': value[1]} for name, value in expected.items()]}
    verify_archive(data, record, expected)
    checks = ['known ZIP inventory/bytes/source hashes accepted']
    def rejects(label, fn):
        try:
            fn()
        except (ValueError, FileExistsError):
            checks.append(label)
        else:
            raise AssertionError('did not reject: ' + label)
    bad = copy.deepcopy(record); bad['sha256'] = '0' * 64
    rejects('wrong ZIP hash rejected', lambda: verify_archive(data, bad, expected))
    bad_entry = copy.deepcopy(record); bad_entry['entries'][0]['sha256'] = '0' * 64
    rejects('wrong entry hash rejected', lambda: verify_archive(data, bad_entry, expected))
    bad_source = copy.deepcopy(record); bad_source['entries'][0]['source']['sha256'] = '0' * 64
    rejects('wrong source hash rejected', lambda: verify_archive(data, bad_source, expected))
    rejects('unexpected inventory rejected', lambda: verify_archive(data, record, {}))
    for name in ('../escape', '/absolute', 'safe/../escape', 'safe\\escape', 'C:/escape'):
        rejects('dangerous entry rejected: ' + name, lambda name=name: archive_bytes({name: next(iter(expected.values()))}))
    unsafe = io.BytesIO()
    with zipfile.ZipFile(unsafe, 'w') as archive:
        archive.writestr('../escape', b'BAD\n')
    unsafe_bytes = unsafe.getvalue()
    rejects('reader rejects malicious ZIP before inventory check', lambda: verify_archive(unsafe_bytes, {'sha256': digest(unsafe_bytes)}, {}))
    with tempfile.TemporaryDirectory(prefix='g07-kit-selfcheck-') as temp:
        path = Path(temp)
        rejects('existing output directory rejected', lambda: build(path))
        write_new(path / 'preserve', b'KEEP\n')
        rejects('existing output file overwrite rejected', lambda: write_new(path / 'preserve', b'BAD\n'))
        assert (path / 'preserve').read_bytes() == b'KEEP\n'
    return {'kind': 'maintainer archive self-check only; no native trial', 'checks': checks, 'result': 'passed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-check', action='store_true')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        print(json.dumps(self_check(), ensure_ascii=False, indent=2))
    if args.build:
        result = build(HERE / KIT)
        print(json.dumps({'prepared': KIT, 'archive_sha256': {k: v['sha256'] for k, v in result['archives'].items()}}, indent=2))
    if args.verify:
        print(json.dumps(verify_prepared(HERE / KIT), ensure_ascii=False, indent=2))
