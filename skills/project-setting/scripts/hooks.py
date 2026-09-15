"""Project-local Codex and Claude document-routing hooks."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

import conventions as c

MARKER = '<!-- project-setting -->'
GUIDANCE = '''文件規範：產生專案文件前，讀取專案根目錄 project-setting.json，依文件用途選擇 type 與目的地。
缺設定或無匹配／多重匹配時，提出既有類型或新增類型的建議並詢問使用者；不要自行當作已確認。
可選本次位置，不保存新的匹配規則。確認後使用 .project-setting/runtime/conventions.py 的 init/configure/choose 命令，然後繼續原任務。
configure/choose 的 --confirmed 僅能在使用者已明確選擇後使用；重試或 hook 的建議不算同意。
必要名稱不足時詢問，不從無關對話猜 slug/id。hook 回報的實際路徑用於後續讀取、修改、連結與交接。
shell 不透明改寫：執行產生文件的程式前先解析其輸出位置。不要用 shell 繞過待確認分類。
已存在且未納管的文件不自動搬移；README、AGENTS、CLAUDE、SKILL、第三方技能資源不納入一般文件路由。
'''


def feedback(event, message, deny=False, updated=None, platform='codex'):
    specific = {'hookEventName': event, 'additionalContext': message}
    if deny:
        specific.update(permissionDecision='deny', permissionDecisionReason=message)
    elif updated is not None:
        specific['updatedInput'] = updated
        if platform == 'codex':
            specific['permissionDecision'] = 'allow'
    return {'hookSpecificOutput': specific}


def request_message(result):
    if result['reason'] == 'collision':
        return '目的地已有文件；保留原內容，詢問使用者是否使用另一名稱或明確編輯既有文件。不要新增類型來繞過衝突。\n' + json.dumps(result, ensure_ascii=False)
    return ('文件分類需要使用者決定，請詢問使用者：優先建議合適既有 type，或新增 type／初始化設定，也可只指定本次位置。'
            '不要反覆重試或自行確認。使用者選擇後執行 conventions.py --root <專案> choose <source> '
            '--type <type> --slug <name> [--id <id>] --confirmed；本次位置使用 --destination。'
            '新增類型先以 configure <json-file> --confirmed 保存完整設定。\n' + json.dumps(result, ensure_ascii=False))


def handle(root, platform, event):
    try:
        return route_event(root, platform, event)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        name = event.get('hook_event_name', 'PreToolUse')
        return feedback(name, str(exc), deny=name == 'PreToolUse')


def route_event(root, platform, event):
    name = event.get('hook_event_name', 'PreToolUse')
    if name in ('SessionStart', 'SubagentStart'):
        return feedback(name, GUIDANCE)
    if name != 'PreToolUse':
        return {}
    tool = event.get('tool_name', '')
    data = event.get('tool_input', {})
    cwd = Path(event.get('cwd', root)).resolve()
    mappings = []
    writes = []
    targets = []

    def destination(source, operation, create=False):
        # Tool-relative paths are relative to tool cwd, not necessarily project root.
        absolute = str((cwd / source).absolute())
        result = c.resolve(root, absolute, operation)
        if result['status'] == 'need_input':
            raise ValueError(request_message(result))
        if result['status'] == 'route':
            target = str(Path(root) / result['destination'])
            if create and Path(target).exists():
                raise ValueError('新增文件的目的地已存在；請保留原內容，明確使用更新操作或選擇新名稱。')
            targets.append(target)
            if str(Path(absolute).resolve()) != target:
                mappings.append((result['source'], result['destination']))
                if operation == 'write':
                    writes.append((result['source'], result['destination']))
            return target
        return source

    if tool == 'Bash':
        return feedback(name, GUIDANCE)
    if platform == 'claude' and tool in ('Write', 'Read', 'Edit'):
        updated = dict(data)
        updated['file_path'] = destination(data['file_path'], 'write' if tool == 'Write' else 'read')
    elif platform == 'codex' and tool == 'apply_patch':
        patch = data.get('command', '')
        lines = patch.splitlines(keepends=True)
        previous_source = None
        for index, line in enumerate(lines):
            match = re.fullmatch(r'(\*\*\* (Add File|Update File|Delete File|Move to): )([^\r\n]+)(\r?\n)?', line)
            if match:
                prefix, operation, source, ending = match.groups()
                if operation == 'Move to':
                    if previous_source is None:
                        raise ValueError('重新命名補丁缺少來源')
                    for path in (previous_source, source):
                        result = c.resolve(root, str(cwd / path), 'read')
                        if result['status'] != 'ignore':
                            raise ValueError('目前 hook 不處理受管文件重新命名；請先規劃搬移與參照更新。')
                else:
                    previous_source = source if operation == 'Update File' else None
                target = destination(source, 'write' if operation in ('Add File', 'Move to') else 'read', create=operation == 'Add File')
                if target != source:
                    target = Path(target).relative_to(cwd).as_posix() if Path(target).is_relative_to(cwd) else Path(target).as_posix()
                lines[index] = prefix + target + (ending or '')
        updated = {**data, 'command': ''.join(lines)}
    else:
        return {}
    if len(set(targets)) != len(targets):
        raise ValueError('同一工具呼叫有多個來源指向同一目的地，請拆分並確認文件身份')
    if not mappings:
        return {}
    if writes:
        c.remember_many(root, writes)
    message = '文件目的地已依專案設定調整；後續讀取、修改及連結使用以下實際路徑：\n' + json.dumps(dict(mappings), ensure_ascii=False)
    return feedback(name, message, updated=updated, platform=platform)


def install(root, platform):
    root = Path(root).resolve()
    if c.read_config(root) is None:
        raise ValueError('Hook 安裝需要 project-setting.json；請先初始化，尚未修改任何檔案')
    runtime = root / '.project-setting/runtime'
    if (root / '.project-setting').is_symlink() or runtime.is_symlink():
        raise ValueError('執行目錄不可是符號連結')
    folder = root / ('.codex' if platform == 'codex' else '.claude')
    if folder.is_symlink():
        raise ValueError('平台目錄不可是符號連結')
    config_path = folder / ('hooks.json' if platform == 'codex' else 'settings.json')
    if config_path.is_symlink():
        raise ValueError('平台設定不可是符號連結')
    config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    if not isinstance(config, dict) or not isinstance(config.get('hooks', {}), dict):
        raise ValueError('平台設定與 hooks 必須是物件')
    for groups in config.get('hooks', {}).values():
        if not isinstance(groups, list) or any(not isinstance(group, dict) for group in groups):
            raise ValueError('每個 hook 事件必須是物件陣列')
    feature_config = folder / 'config.toml'
    if platform == 'codex' and feature_config.is_symlink():
        raise ValueError('Codex 功能設定不可是符號連結')
    instructions = root / ('AGENTS.md' if platform == 'codex' else 'CLAUDE.md')
    if instructions.is_symlink():
        raise ValueError('指令檔為符號連結，請人工整合')
    text = instructions.read_text(encoding='utf-8') if instructions.exists() else ''
    for filename in ('conventions.py', 'hooks.py'):
        if (runtime / filename).is_symlink():
            raise ValueError('執行檔不可是符號連結')
    runtime.mkdir(parents=True, exist_ok=True)
    for filename in ('conventions.py', 'hooks.py'):
        target = runtime / filename
        if target.is_symlink():
            raise ValueError('執行檔不可是符號連結')
        source = Path(__file__).parent / filename
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
    # Discover the nearest configured project without machine-specific paths.
    bootstrap = (
        "import pathlib,runpy,sys; "
        "cwd=pathlib.Path.cwd().resolve(); "
        "root=next((p for p in (cwd,*cwd.parents) if (p/'project-setting.json').exists()),None); "
        "root is not None or sys.exit('project-setting.json not found'); "
        "script=root/'.project-setting/runtime/hooks.py'; "
        "script.is_file() or sys.exit('project-setting hook runtime not found'); "
        "sys.path.insert(0,str(script.parent)); "
        "sys.argv=[str(script),'hook','--platform','" + platform + "']; "
        "runpy.run_path(str(script),run_name='__main__')"
    )
    command = 'python3 -c "' + bootstrap + '"'
    # Match only registrations emitted by older installers, including Windows.
    legacy_command = 'python3 "$(git rev-parse --show-toplevel)/.project-setting/runtime/hooks.py" hook --platform ' + platform
    legacy_bootstrap = (
        "import pathlib,runpy,subprocess,sys; "
        "root=subprocess.check_output(['git','rev-parse','--show-toplevel']).decode('utf-8').strip(); "
        "script=pathlib.Path(root)/'.project-setting/runtime/hooks.py'; "
        "sys.path.insert(0,str(script.parent)); "
        "sys.argv=[str(script),'hook','--platform','codex']; "
        "runpy.run_path(str(script),run_name='__main__')"
    )
    for event, matcher in (('SessionStart', None), ('SubagentStart', None), ('PreToolUse', '^(apply_patch|Bash)$' if platform == 'codex' else '^(Write|Read|Edit|Bash)$')):
        groups = config.setdefault('hooks', {}).setdefault(event, [])
        handler = {'type': 'command', 'command': command, 'timeout': 10}
        if platform == 'codex':
            handler['commandWindows'] = 'py -3 -X utf8 -c "' + bootstrap + '"'
        group = {'hooks': [handler]}
        legacy_handler = {'type': 'command', 'command': legacy_command, 'timeout': 10}
        legacy = {'hooks': [legacy_handler]}
        legacy_windows = {'hooks': [{**legacy_handler, 'commandWindows': 'py -3 -X utf8 -c "' + legacy_bootstrap + '"'}]}
        if matcher:
            group['matcher'] = legacy['matcher'] = legacy_windows['matcher'] = matcher
        for index, existing in enumerate(groups):
            if existing == legacy or (platform == 'codex' and existing == legacy_windows):
                groups[index] = group
        if group not in groups:
            groups.append(group)
        # Collapse identical registrations when multiple old versions coexisted.
        groups[:] = [entry for index, entry in enumerate(groups) if entry != group or group not in groups[:index]]
    c.atomic_json(config_path, config)
    if platform == 'codex':
        feature_config = folder / 'config.toml'
        if not feature_config.exists():
            feature_config.write_text('[features]\nhooks = true\n', encoding='utf-8')
    if MARKER not in text:
        instructions.write_text(text.rstrip() + '\n\n' + MARKER + '\n' + GUIDANCE, encoding='utf-8')
    ignore = root / '.gitignore'
    if ignore.exists() and not ignore.is_symlink():
        ignore_text = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
        for pattern in ('.project-setting/routes.json', '.project-setting/routes.lock'):
            if pattern not in ignore_text.splitlines():
                ignore_text = ignore_text.rstrip() + '\n' + pattern + '\n'
        ignore.write_text(ignore_text, encoding='utf-8')
    return {'status': 'installed', 'platform': platform, 'root': str(root), 'note': '僅表示整合檔案已安裝，尚未驗證啟用。Codex：既有 config.toml 保持原樣；確認 [features] hooks = true（false 會停用），再到 /hooks 審查並信任定義。啟動新工作階段驗證載入。需要 Python 3.9+，不需要 Git。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'hook'))
    parser.add_argument('--platform', choices=('codex', 'claude'), required=True)
    parser.add_argument('--root')
    args = parser.parse_args()
    event = {}
    try:
        if args.action == 'install':
            result = install(Path(args.root).resolve() if args.root else c.project_root('.'), args.platform)
        else:
            event = json.load(sys.stdin)
            installed_root = Path(__file__).resolve().parents[2]
            root = Path(args.root).resolve() if args.root else (installed_root if (installed_root / '.project-setting/runtime/hooks.py').resolve() == Path(__file__).resolve() else c.project_root(event.get('cwd', '.')))
            result = handle(root, args.platform, event)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        if args.action == 'install':
            print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False))
            raise SystemExit(1)
        result = feedback(event.get('hook_event_name', 'PreToolUse'), str(exc), deny=event.get('hook_event_name', 'PreToolUse') == 'PreToolUse')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
