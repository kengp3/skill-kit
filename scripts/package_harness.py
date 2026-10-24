"""Build a self-contained Codex runtime. Never install or overwrite a release."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('define-task', 'project-setting', 'task-harness', 'ai-code-review')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(package):
    if package.is_symlink():
        raise ValueError('package root must not be a symlink')
    manifest_path = package / 'runtime-manifest.json'
    if manifest_path.is_symlink():
        raise ValueError('manifest must not be a symlink')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema_version') != 1 or not isinstance(manifest.get('files'), dict):
        raise ValueError('unsupported manifest')
    actual = {}
    for path in package.rglob('*'):
        if path.is_symlink():
            raise ValueError(f'symlinks are not permitted: {path}')
        if path.is_file() and path != manifest_path:
            actual[path.relative_to(package).as_posix()] = digest(path)
    if not actual or actual != manifest['files']:
        raise ValueError('runtime content differs from manifest')
    return digest(manifest_path)


def build(destination):
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination exists; use a new release directory')
    sources = [(ROOT / 'packaging/codex/.codex-plugin/plugin.json',
                Path('.codex-plugin/plugin.json')),
               (ROOT / 'packaging/codex/hooks/hooks.json', Path('hooks/hooks.json')),
               (ROOT / 'packaging/codex/hooks/task_harness.py', Path('hooks/task_harness.py'))]
    for source in [*(source for source, _ in sources),
                   *(ROOT / 'skills' / s / 'SKILL.md' for s in SKILLS)]:
        if any(parent.is_symlink() for parent in [source, *source.parents]
               if parent != ROOT and ROOT in parent.parents):
            raise ValueError(f'symlink in runtime source path: {source}')
        if not source.is_file():
            raise ValueError(f'missing required runtime input: {source}')
    for skill in SKILLS:
        directory = ROOT / 'skills' / skill
        for path in sorted(directory.rglob('*')):
            if path.is_symlink():
                raise ValueError(f'symlinks are not runtime inputs: {path}')
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                sources.append((path, path.relative_to(ROOT)))
    resolved_destination = destination.resolve()
    if any(resolved_destination == source or source in resolved_destination.parents
           for source in [ROOT / 'skills', ROOT / 'packaging']):
        raise ValueError('destination must be outside runtime sources')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        stage = Path(temp) / 'package'
        stage.mkdir()
        files = {}
        for source, relative in sources:
            if source.is_symlink() or not source.is_file():
                raise ValueError(f'invalid runtime input: {source}')
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            files[relative.as_posix()] = digest(target)
        version = json.loads((stage / '.codex-plugin/plugin.json').read_text())['version']
        manifest = {'schema_version': 1, 'version': version, 'files': files}
        (stage / 'runtime-manifest.json').write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
        verify(stage)
        stage.rename(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='check installed contents; no writes')
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        if args.verify:
            print(verify(args.destination.absolute()))
        else:
            build(args.destination.absolute())
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'{error}\n')
    print(args.destination.absolute())


if __name__ == '__main__':
    main()
