#!/usr/bin/env python3
"""Freeze committed inputs and compare explicit observations, never infer equivalence."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f'Invalid JSON number: {value}')
    value = json.loads(Path(path).read_text(encoding='utf-8'),
                       object_pairs_hook=pairs, parse_constant=invalid, parse_float=invalid)
    if not isinstance(value, dict):
        raise ValueError('Evidence documents must be JSON objects')
    return value


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def git(repo, *args):
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(repo), *args],
                                   stderr=subprocess.PIPE, timeout=60)


def safe_path(root, name):
    parts = PurePosixPath(name).parts
    if not parts or '\\' in name or any(p in ('.', '..', '.git') for p in parts):
        raise ValueError(f'Unsafe path: {name}')
    target = root / name
    if PurePosixPath(name).is_absolute() or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes output: {name}')
    if any(p.is_symlink() for p in [target, *target.parents] if p == root or p.is_relative_to(root)):
        raise ValueError(f'Symlink not supported: {name}')
    return target


def prepare(old_repo, old_ref, new_repo, new_ref, out):
    out = Path(out).absolute()
    out = out.parent.resolve() / out.name
    for repo in (old_repo, new_repo):
        repo = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
        if out.resolve().is_relative_to(repo):
            raise ValueError('Output must be outside both source repositories')
    safe_path(out.parent, out.name)
    out.mkdir()  # A failed run remains for inspection; never overwrite it.
    manifest = {'schema': 1, 'mode': 'committed-only', 'tool_sha256': digest(__file__)}
    for side, repo, ref in [('old', old_repo, old_ref), ('new', new_repo, new_ref)]:
        commit = git(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
        root = out / 'snapshots' / side
        root.mkdir(parents=True)
        files, names = {}, set()
        for entry in git(repo, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0'):
            if not entry:
                continue
            metadata, name = entry.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            name = name.decode('utf-8')
            if mode not in ('100644', '100755') or kind != 'blob':
                raise ValueError(f'Unsupported tree entry: {side}/{name} ({mode})')
            if name.casefold() in names:
                raise ValueError(f'Case collision: {name}')
            names.add(name.casefold())
            content = git(repo, 'cat-file', 'blob', oid)
            if content.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
                raise ValueError(f'Unresolved LFS pointer: {name}')
            target = safe_path(root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(content)
            target.chmod(0o755 if mode == '100755' else 0o644)
            files[name] = {'sha256': digest(target), 'mode': mode, 'blob': oid}
        manifest[side] = {'repo': str(Path(repo).resolve()), 'ref': ref, 'commit': commit,
                          'files': files, 'dirty_excluded': bool(git(repo, 'status', '--porcelain'))}
    write_json(out / 'manifest.json', manifest)
    return manifest


def verify(run):
    run = Path(run).resolve()
    manifest = read_json(run / 'manifest.json')
    if manifest['schema'] != 1 or manifest['tool_sha256'] != digest(__file__):
        raise ValueError('Manifest schema or helper version changed; prepare a new run')
    for side in ('old', 'new'):
        root = run / 'snapshots' / side
        actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() or p.is_symlink()}
        if actual != set(manifest[side]['files']):
            raise ValueError(f'Snapshot file set changed: {side}')
        for name, item in manifest[side]['files'].items():
            path = safe_path(root, name)
            if digest(path) != item['sha256'] or bool(path.stat().st_mode & 0o111) != (item['mode'] == '100755'):
                raise ValueError(f'Snapshot changed: {side}/{name}')
    return manifest


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def compare(run, contract_path, old_path, new_path):
    run = Path(run).resolve()
    manifest = verify(run)
    contract = read_json(contract_path)
    cases = contract['cases']
    if not isinstance(contract['scope'], str) or not contract['scope'] or not isinstance(cases, list) or not cases or not isinstance(contract['artifacts'], dict) or not contract['artifacts']:
        raise ValueError('Scope, nonempty cases and runner artifacts are required')
    ids = [c['id'] for c in cases]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Case IDs must be unique nonempty strings')
    for name, expected in contract['artifacts'].items():
        if digest(safe_path(run, name)) != expected:
            raise ValueError(f'Runner/config/input artifact changed: {name}')
    bindings = {'manifest_sha256': digest(run / 'manifest.json'),
                'contract_sha256': digest(contract_path)}
    observations, problems = {}, []
    for side, path in [('old', old_path), ('new', new_path)]:
        evidence = read_json(path)
        if any(evidence.get(k) != v for k, v in bindings.items()) or evidence.get('commit') != manifest[side]['commit'] or evidence.get('side') != side:
            problems.append(f'{side}: stale evidence or incorrect side/commit')
        commands = evidence.get('command')
        if isinstance(commands, list) and all(isinstance(arg, str) for arg in commands):
            commands = [commands]
        valid_commands = isinstance(commands, list) and bool(commands) and all(
            isinstance(cmd, list) and bool(cmd) and isinstance(cmd[0], str) and bool(cmd[0])
            and all(isinstance(arg, str) and '\x00' not in arg for arg in cmd) for cmd in commands)
        if type(evidence.get('exit_code')) is not int or evidence['exit_code'] != 0 or not valid_commands:
            problems.append(f'{side}: execution failed or command missing/invalid')
        records = evidence.get('records', [])
        if not isinstance(records, list) or any(not isinstance(r, dict) or not isinstance(r.get('observed', {}), dict) for r in records):
            raise ValueError(f'{side}: records must contain observation objects')
        keys = [r['id'] for r in records]
        if len(keys) != len(set(keys)) or set(keys) - set(ids):
            raise ValueError(f'{side}: duplicate or unexpected observations')
        observations[side] = {r['id']: r for r in records}
    results = []
    for case in cases:
        required = case['observe']
        if not isinstance(required, list) or not required or any(not isinstance(k, str) or not k for k in required) or len(required) != len(set(required)):
            raise ValueError('Every case needs unique, nonempty observation names')
        missing, differences = [], []
        rows = [observations[s].get(case['id'], {}) for s in ('old', 'new')]
        valid = not problems
        for side, row in zip(('old', 'new'), rows):
            for key in sorted(set(row.get('observed', {})) - set(required)):
                missing.append(f'{side}: undeclared observation: {key}')
            for key in ('input', 'initial_state', 'environment'):
                if key not in row or canonical(row[key]) != canonical(case[key]):
                    missing.append(f'{side}: missing/mismatched {key}')
                    valid = False
        if valid:
            for key in required:
                if any(key not in r.get('observed', {}) for r in rows):
                    missing.append(f'unobserved: {key}')
                elif canonical(rows[0]['observed'][key]) != canonical(rows[1]['observed'][key]):
                    differences.append(key)
        status = 'FAIL' if differences else 'UNKNOWN' if missing or problems else 'PASS'
        results.append({'id': case['id'], 'status': status, 'differences': differences,
                        'unknowns': problems + missing})
    states = {r['status'] for r in results}
    return {'status': 'FAIL' if 'FAIL' in states else 'UNKNOWN' if 'UNKNOWN' in states else 'PASS',
            'scope': contract['scope'], 'meaning': 'Observed cases only; not a business-equivalence verdict',
            'bindings': bindings, 'old_sha256': digest(old_path), 'new_sha256': digest(new_path),
            'cases': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    prep = sub.add_parser('prepare')
    for option in ('old-repo', 'old-ref', 'new-repo', 'new-ref', 'out'):
        prep.add_argument('--' + option, required=True)
    check = sub.add_parser('verify')
    check.add_argument('--run', required=True)
    comp = sub.add_parser('compare')
    for option in ('run', 'contract', 'old', 'new', 'out'):
        comp.add_argument('--' + option, required=True)
    args = parser.parse_args()
    try:
        if args.action == 'prepare':
            prepare(args.old_repo, args.old_ref, args.new_repo, args.new_ref, args.out)
            result = {'status': 'PREPARED', 'out': args.out}
        elif args.action == 'verify':
            verify(args.run)
            result = {'status': 'VERIFIED'}
        else:
            result = compare(args.run, args.contract, args.old, args.new)
            write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False))
        return {'FAIL': 1, 'UNKNOWN': 2}.get(result['status'], 0)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'UNKNOWN', 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
