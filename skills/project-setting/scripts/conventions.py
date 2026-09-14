"""Project document destinations. Python standard library only."""
import argparse
from contextlib import contextmanager
import fcntl
import fnmatch
import json
import os
from pathlib import Path
import re
import tempfile

CONFIG = 'project-setting.json'
STATE = '.project-setting/routes.json'
DESCRIPTIONS = {'prd': '產品目標、使用者問題與成功指標', 'spec': '系統行為、需求與驗收', 'plan': '實作步驟與驗證安排', 'adr': '架構決策、理由與影響', 'research': '研究證據、比較與調查'}
PROTECTED = {'.git', '.codex', '.claude', '.agents', '.project-setting', 'skills', 'node_modules', '.venv', 'vendor'}
ENTRIES = {'README.md', 'AGENTS.md', 'CLAUDE.md', 'SKILL.md', 'CONTRIBUTING.md', 'LICENSE.md', 'CHANGELOG.md', 'CONSTRAINTS.md'}


def defaults():
    return {'version': 1, 'documents': {
        kind: {'description': description,
               'path': f'docs/{kind if kind in ("adr", "research") else kind + "s"}/' + ('{id}-' if kind == 'adr' else '') + '{slug}.' + kind + '.md',
               'match': [f'*.{kind}.md', f'*-{kind}.md', f'{kind}.md']}
        for kind, description in DESCRIPTIONS.items()}}


def project_root(start):
    start = Path(start).resolve()
    for folder in (start, *start.parents):
        if (folder / CONFIG).exists() or (folder / '.git').exists():
            return folder
    return start


def relative(root, value):
    root = Path(root).resolve()
    path = Path(value)
    target = (root / path).resolve()
    try:
        rel = target.relative_to(root)
    except ValueError:
        raise ValueError('路徑必須位於專案內') from None
    if '..' in path.parts or not rel.parts or any(p in PROTECTED for p in rel.parts):
        raise ValueError('路徑含受保護目錄或無效片段')
    return rel.as_posix()


def atomic_json(path, value):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('設定或狀態檔不可是符號連結')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def validate(root, cfg):
    if not isinstance(cfg, dict) or cfg.get('version') != 1 or not isinstance(cfg.get('documents'), dict):
        raise ValueError('需要 version=1 與 documents 物件')
    for kind, rule in cfg['documents'].items():
        if not re.fullmatch(r'[a-z][a-z0-9-]*', kind) or not isinstance(rule, dict):
            raise ValueError('文件類型必須是小寫識別碼，規則必須是物件')
        path = rule.get('path')
        if not isinstance(path, str) or Path(path).is_absolute() or not path.endswith('.md'):
            raise ValueError('path 必須是專案相對 Markdown 路徑')
        fields = re.findall(r'\{([^{}]+)\}', path)
        if any(f not in ('slug', 'id') for f in fields) or len(fields) != len(set(fields)):
            raise ValueError('僅支援不重複的 {slug}、{id}')
        sample = path.replace('{slug}', 'example').replace('{id}', '0001')
        if '{' in sample or '}' in sample:
            raise ValueError('無效佔位符')
        relative(root, sample)
        patterns = rule.get('match', [])
        if not isinstance(patterns, list) or any(not isinstance(p, str) or not p or '/' in p or '\\' in p for p in patterns):
            raise ValueError('match 必須是檔名模式陣列')
        if not isinstance(rule.get('description', ''), str):
            raise ValueError('description 必須是文字')
    return cfg


def read_config(root):
    path = Path(root) / CONFIG
    if not path.exists():
        return None
    if path.is_symlink():
        raise ValueError('設定檔不可是符號連結')
    return validate(root, json.loads(path.read_text(encoding='utf-8')))


def save_config(root, cfg):
    atomic_json(Path(root) / CONFIG, validate(root, cfg))


def initialize(root, cfg=None):
    current = read_config(root)
    if current is None:
        save_config(root, defaults() if cfg is None else cfg)
    return read_config(root)


def routes(root):
    folder = Path(root) / '.project-setting'
    if folder.is_symlink() or (folder / 'routes.json').is_symlink():
        raise ValueError('路由狀態不可是符號連結')
    path = Path(root) / STATE
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if not isinstance(data, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in data.items()):
        raise ValueError('無效路由狀態，請保留狀態檔供診斷')
    return data


def remember(root, source, destination):
    remember_many(root, [(source, destination)])


def remember_many(root, mappings):
    mappings = [(relative(root, s), relative(root, d)) for s, d in mappings]
    with route_lock(root):
        state = routes(root)
        for source, destination in mappings:
            if source != destination and (
                any(d == source and s != source for s, d in state.items())
                or (destination in state and state[destination] != destination)
            ):
                raise ValueError('別名不可串接其他別名；請使用單一實際目的地')
            owners = [s for s, d in state.items() if d == destination and s != source]
            if owners:
                raise ValueError('目的地已由另一份來源文件保留：' + ', '.join(owners))
            state[source] = destination
        atomic_json(Path(root) / STATE, state)


@contextmanager
def route_lock(root):
    folder = Path(root) / '.project-setting'
    if folder.is_symlink():
        raise ValueError('狀態目錄不可是符號連結')
    folder.mkdir(exist_ok=True)
    lock = folder / 'routes.lock'
    if lock.is_symlink():
        raise ValueError('狀態鎖不可是符號連結')
    with lock.open('a') as stream:
        # ponytail: one lock per project; split only if measured contention warrants it.
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def render(root, rule, slug=None, identifier=None):
    values = {'slug': slug, 'id': identifier}
    for key in re.findall(r'\{([^{}]+)\}', rule['path']):
        if not values[key]:
            raise ValueError('缺少 ' + key)
        if not re.fullmatch(r'[\w-]+', values[key]) or values[key] in ('.', '..'):
            raise ValueError('名稱或編號只能使用字母、數字、底線、連字號')
    return relative(root, rule['path'].format(**values))


def choose(root, source, kind=None, slug=None, identifier=None, destination=None):
    source = relative(root, source)
    if destination is None:
        cfg = read_config(root)
        if cfg is None or kind not in cfg['documents']:
            raise ValueError('請先建立設定或新增文件類型')
        destination = render(root, cfg['documents'][kind], slug, identifier)
    destination = relative(root, destination)
    if not destination.endswith('.md'):
        raise ValueError('目的地必須是 Markdown 文件')
    if source != destination and ((Path(root) / destination).exists() or (Path(root) / source).exists()):
        raise ValueError('來源或目的地已存在，請明確處理既有文件，不自動搬移或覆寫')
    remember(root, source, destination)
    return {'status': 'route', 'source': source, 'destination': destination}


def resolve(root, source, operation='write'):
    raw = Path(source)
    if raw.name in ENTRIES or raw.suffix.lower() != '.md':
        return {'status': 'ignore'}
    if raw.is_absolute():
        try:
            raw = raw.relative_to(Path(root).resolve())
        except ValueError:
            raise ValueError('路徑必須位於專案內') from None
    if any(p in PROTECTED for p in raw.parts):
        return {'status': 'ignore'}
    source = relative(root, source)
    state = routes(root)
    if source in state:
        return {'status': 'route', 'source': source, 'destination': relative(root, state[source])}
    if source in state.values():
        return {'status': 'route', 'source': source, 'destination': source}
    cfg = read_config(root)
    def need(reason, candidates=None):
        return {'status': 'need_input', 'reason': reason, 'source': source,
                'candidates': candidates or [], 'types': {} if cfg is None else cfg['documents']}
    if cfg is None:
        return need('missing_config') if operation == 'write' else {'status': 'ignore'}
    matches = []
    for kind, rule in cfg['documents'].items():
        pattern = re.escape(rule['path']).replace(re.escape('{slug}'), r'(?P<slug>[\w-]+)').replace(re.escape('{id}'), r'(?P<id>[\w-]+)')
        if re.fullmatch(pattern, source):
            matches.append((kind, source))
        elif any(fnmatch.fnmatchcase(raw.name, p) for p in rule.get('match', [])):
            name = re.sub(r'\.md$', '', raw.name)
            name = re.sub(r'[.-]' + re.escape(kind) + '$', '', name)
            slug, identifier = (None if name == kind else name), None
            if kind == 'adr' and slug and re.match(r'^\d+-', slug):
                identifier, slug = slug.split('-', 1)
            try:
                dest = render(root, rule, slug, identifier)
            except ValueError:
                dest = None
            matches.append((kind, dest))
    # Existing files outside configured destinations are not adopted by filename matching.
    if (Path(root) / source).exists() and not any(dest == source for _, dest in matches):
        return {'status': 'ignore', 'reason': 'existing_source'}
    if not matches:
        if operation != 'write':
            return {'status': 'ignore'}
        return need('unmatched')
    if len(matches) > 1:
        return need('ambiguous', [m[0] for m in matches])
    kind, destination = matches[0]
    if destination is None:
        return need('missing_metadata', [kind])
    if source != destination and (Path(root) / destination).exists():
        return need('collision', [kind])
    return {'status': 'route', 'source': source, 'destination': destination, 'type': kind}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    sub = parser.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init')
    init.add_argument('--config')
    sub.add_parser('show')
    update = sub.add_parser('configure')
    update.add_argument('file')
    update.add_argument('--confirmed', action='store_true', required=True)
    query = sub.add_parser('resolve')
    query.add_argument('source')
    choice = sub.add_parser('choose')
    choice.add_argument('source')
    choice.add_argument('--type', dest='kind')
    choice.add_argument('--slug')
    choice.add_argument('--id', dest='identifier')
    choice.add_argument('--destination')
    choice.add_argument('--confirmed', action='store_true', required=True)
    args = parser.parse_args()
    root = project_root(args.root)
    try:
        if args.action == 'init':
            result = initialize(root, json.loads(Path(args.config).read_text()) if args.config else None)
        elif args.action == 'show':
            result = read_config(root)
        elif args.action == 'configure':
            save_config(root, json.loads(Path(args.file).read_text(encoding='utf-8')))
            result = read_config(root)
        elif args.action == 'choose':
            result = choose(root, args.source, args.kind, args.slug, args.identifier, args.destination)
        else:
            result = resolve(root, args.source)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
