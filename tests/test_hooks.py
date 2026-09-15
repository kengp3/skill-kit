import json
import os
import shutil
from unittest import mock
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/project-setting/scripts'
sys.path.insert(0, str(SCRIPTS))
import conventions as c
import hooks as h


class HookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        c.initialize(self.root)

    def event(self, tool, data, platform='codex'):
        return h.handle(self.root, platform, {'hook_event_name': 'PreToolUse', 'cwd': str(self.root), 'tool_name': tool, 'tool_input': data})

    def test_patch_rewrites_only_headers_and_preserves_body(self):
        patch = '*** Begin Patch\n*** Add File: login.plan.md\n+# Plan\n+literal login.plan.md\n*** End Patch'
        result = self.event('apply_patch', {'command': patch})['hookSpecificOutput']
        self.assertEqual(result['permissionDecision'], 'allow')
        self.assertIn('*** Add File: docs/plans/login.plan.md', result['updatedInput']['command'])
        self.assertIn('+literal login.plan.md', result['updatedInput']['command'])
        self.assertIn('docs/plans/login.plan.md', result['additionalContext'])

    def test_unknown_blocks_for_user_then_resumes(self):
        patch = '*** Begin Patch\n*** Add File: investigation.md\n+Report\n*** End Patch'
        denied = self.event('apply_patch', {'command': patch})['hookSpecificOutput']
        self.assertEqual(denied['permissionDecision'], 'deny')
        self.assertIn('詢問使用者', denied['permissionDecisionReason'])
        c.choose(self.root, 'investigation.md', kind='research', slug='cache')
        allowed = self.event('apply_patch', {'command': patch})['hookSpecificOutput']
        self.assertIn('docs/research/cache.research.md', allowed['updatedInput']['command'])

    def test_existing_unmanaged_documents_can_be_updated_and_deleted(self):
        for scenario in ('missing_metadata', 'ambiguous'):
            cfg = c.defaults()
            if scenario == 'ambiguous':
                cfg['documents']['spec']['match'].append('plan.md')
            c.save_config(self.root, cfg)
            source = self.root / 'plan.md'
            source.write_text('old\n')
            for operation in ('Update File', 'Delete File'):
                with self.subTest(scenario=scenario, operation=operation):
                    body = '@@\n-old\n+new\n' if operation == 'Update File' else ''
                    patch = f'*** Begin Patch\n*** {operation}: plan.md\n{body}*** End Patch\n'
                    self.assertEqual(self.event('apply_patch', {'command': patch}), {})
                    self.assertEqual(c.routes(self.root), {})
                    self.assertEqual(source.read_text(), 'old\n')
            source.unlink()
            patch = '*** Begin Patch\n*** Add File: plan.md\n+new\n*** End Patch\n'
            self.assertEqual(self.event('apply_patch', {'command': patch})['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_claude_write_read_edit_preserve_fields(self):
        write = self.event('Write', {'file_path': str(self.root / 'login.spec.md'), 'content': '# Spec'}, 'claude')['hookSpecificOutput']
        self.assertNotIn('permissionDecision', write)
        dest = str(self.root / 'docs/specs/login.spec.md')
        self.assertEqual(write['updatedInput'], {'file_path': dest, 'content': '# Spec'})
        for tool, fields in [('Read', {'offset': 2}), ('Edit', {'old_string': 'old', 'new_string': 'new'})]:
            result = self.event(tool, {'file_path': str(self.root / 'login.spec.md'), **fields}, 'claude')['hookSpecificOutput']
            self.assertEqual(result['updatedInput'], {'file_path': dest, **fields})

    def test_install_preserves_settings_and_is_idempotent(self):
        (self.root / 'AGENTS.md').write_text('Existing instructions\n')
        folder = self.root / '.claude'
        folder.mkdir()
        existing = {'env': {'HELLO': 'world'}, 'hooks': {'PreToolUse': [{'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'echo existing'}]}]}}
        (folder / 'settings.json').write_text(json.dumps(existing))
        h.install(self.root, 'claude')
        first = (folder / 'settings.json').read_text()
        h.install(self.root, 'claude')
        self.assertEqual(first, (folder / 'settings.json').read_text())
        self.assertEqual(json.loads(first)['env'], existing['env'])
        self.assertTrue((self.root / 'AGENTS.md').read_text().startswith('Existing instructions'))
        h.install(self.root, 'codex')
        self.assertTrue((self.root / '.codex/hooks.json').exists())

    def test_windows_command_and_upgrade_preserve_other_hooks(self):
        h.install(self.root, 'codex')
        config_path = self.root / '.codex/hooks.json'
        config = json.loads(config_path.read_text())
        handler = config['hooks']['PreToolUse'][0]['hooks'][0]
        self.assertIn('commandWindows', handler)
        command = handler['commandWindows']
        self.assertTrue(command.startswith('python -X utf8 -c "'))
        # Execute the Windows bootstrap as Python on this host; shell/native OS
        # compatibility still requires the same test on Windows.
        code = command.split(' -c "', 1)[1][:-1]
        child = self.root / '中文 subdir'
        child.mkdir()
        event = {'hook_event_name': 'PreToolUse', 'cwd': str(child),
                 'tool_name': 'apply_patch', 'tool_input': {'command':
                 '*** Begin Patch\n*** Add File: login.plan.md\n+中文\n*** End Patch'}}
        launcher = command if os.name == 'nt' else [sys.executable, '-X', 'utf8', '-c', code]
        result = subprocess.run(launcher, shell=os.name == 'nt', cwd=child,
                                input=json.dumps(event), capture_output=True, text=True,
                                encoding='utf-8', check=True)
        output = json.loads(result.stdout)['hookSpecificOutput']
        self.assertIn('login.plan.md', output['updatedInput']['command'])
        self.assertEqual(output['permissionDecision'], 'allow')
        self.assertEqual(c.routes(self.root)['中文 subdir/login.plan.md'], 'docs/plans/login.plan.md')
        if os.name != 'nt':
            posix = subprocess.run(handler['command'], shell=True, cwd=child,
                                   input=json.dumps({'hook_event_name': 'SessionStart'}),
                                   capture_output=True, text=True, encoding='utf-8', check=True)
            self.assertIn('文件規範', json.loads(posix.stdout)['hookSpecificOutput']['additionalContext'])
        # Upgrade the previous Git-free command that still required py.exe.
        handler['commandWindows'] = command.replace('python -X utf8', 'py -3 -X utf8', 1)
        extra = {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'echo keep'}]}
        config['hooks']['PreToolUse'].append(extra)
        config_path.write_text(json.dumps(config))
        h.install(self.root, 'codex')
        h.install(self.root, 'codex')
        groups = json.loads(config_path.read_text())['hooks']['PreToolUse']
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[1], extra)
        self.assertEqual(groups[0]['hooks'][0]['commandWindows'], command)

    def test_install_requires_config_before_mutation(self):
        (self.root / c.CONFIG).unlink()
        with self.assertRaisesRegex(ValueError, 'project-setting.json'):
            h.install(self.root, 'codex')
        self.assertFalse((self.root / '.project-setting').exists())

    def test_no_git_install_relocation_and_missing_nearest_runtime(self):
        # No executable, including Git, is visible while installing.
        with mock.patch.dict(os.environ, {'PATH': ''}):
            h.install(self.root, 'codex')
            h.install(self.root, 'claude')
        self.assertFalse((self.root / '.gitignore').exists())
        with tempfile.TemporaryDirectory() as target:
            moved = Path(target) / '搬移 project'
            shutil.copytree(self.root, moved)
            shutil.rmtree(self.root)
            child = moved / 'nested'
            child.mkdir()
            config = json.loads((moved / '.codex/hooks.json').read_text())
            handler = config['hooks']['SessionStart'][0]['hooks'][0]
            code = handler['commandWindows'].split(' -c "', 1)[1][:-1]
            env = {**os.environ, 'PATH': '', 'PYTHONDONTWRITEBYTECODE': '1'}
            event = json.dumps({'hook_event_name': 'SessionStart'})
            result = subprocess.run([sys.executable, '-c', code], cwd=child, env=env,
                                    input=event, capture_output=True, text=True, check=True)
            self.assertIn('文件規範', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])
            if os.name != 'nt':
                binaries = Path(target) / 'bin'
                binaries.mkdir()
                (binaries / 'python3').symlink_to(sys.executable)
                for folder, filename in (('.codex', 'hooks.json'), ('.claude', 'settings.json')):
                    config = json.loads((moved / folder / filename).read_text())
                    command = config['hooks']['SessionStart'][0]['hooks'][0]['command']
                    result = subprocess.run(command, shell=True, cwd=child,
                                            env={**env, 'PATH': str(binaries)}, input=event,
                                            capture_output=True, text=True, check=True)
                    self.assertIn('文件規範', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])
            # A nested project must never fall back to its parent's runtime.
            c.initialize(child)
            result = subprocess.run([sys.executable, '-c', code], cwd=child, env=env,
                                    input=event, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('runtime not found', result.stderr)
            (child / c.CONFIG).unlink()
            (moved / c.CONFIG).unlink()
            result = subprocess.run([sys.executable, '-c', code], cwd=child, env=env,
                                    input=event, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('project-setting.json not found', result.stderr)

    def test_git_registrations_are_upgraded_exactly(self):
        for platform in ('codex', 'claude'):
            h.install(self.root, platform)
            path = self.root / ('.codex/hooks.json' if platform == 'codex' else '.claude/settings.json')
            config = json.loads(path.read_text())
            expected = json.loads(path.read_text())
            old_command = 'python3 "$(git rev-parse --show-toplevel)/.project-setting/runtime/hooks.py" hook --platform ' + platform
            old_bootstrap = (
                "import pathlib,runpy,subprocess,sys; "
                "root=subprocess.check_output(['git','rev-parse','--show-toplevel']).decode('utf-8').strip(); "
                "script=pathlib.Path(root)/'.project-setting/runtime/hooks.py'; "
                "sys.path.insert(0,str(script.parent)); "
                "sys.argv=[str(script),'hook','--platform','codex']; "
                "runpy.run_path(str(script),run_name='__main__')"
            )
            for groups in config['hooks'].values():
                group = groups[0]
                group['hooks'] = [{'type': 'command', 'command': old_command, 'timeout': 10}]
                if platform == 'codex':
                    windows = json.loads(json.dumps(group))
                    windows['hooks'][0]['commandWindows'] = 'py -3 -X utf8 -c "' + old_bootstrap + '"'
                    groups.append(windows)
            custom = {'hooks': [{'type': 'command', 'command': old_command, 'timeout': 20}]}
            config['hooks']['SessionStart'].append(custom)
            expected['hooks']['SessionStart'].append(custom)
            path.write_text(json.dumps(config))
            with mock.patch.dict(os.environ, {'PATH': ''}):
                h.install(self.root, platform)
                h.install(self.root, platform)
            self.assertEqual(json.loads(path.read_text()), expected)

    def test_invalid_hook_config_and_broken_symlink_leave_no_runtime(self):
        folder = self.root / '.codex'
        folder.mkdir()
        config = folder / 'hooks.json'
        for value in ([], {'hooks': []}, {'hooks': {'PreToolUse': {}}}):
            config.write_text(json.dumps(value))
            before = config.read_bytes()
            with self.assertRaises(ValueError):
                h.install(self.root, 'codex')
            self.assertEqual(config.read_bytes(), before)
            self.assertFalse((self.root / '.project-setting').exists())
        config.write_text('{}')
        (folder / 'config.toml').symlink_to(self.root / 'missing.toml')
        with self.assertRaises(ValueError):
            h.install(self.root, 'codex')
        self.assertFalse((self.root / 'missing.toml').exists())
        self.assertFalse((self.root / '.project-setting').exists())

    def test_shell_not_rewritten_and_patch_collision(self):
        result = self.event('Bash', {'command': 'python generate_docs.py'})
        self.assertNotIn('updatedInput', result.get('hookSpecificOutput', {}))
        dest = self.root / 'docs/plans/login.plan.md'
        dest.parent.mkdir(parents=True)
        dest.write_text('existing')
        patch = '*** Begin Patch\n*** Add File: login.plan.md\n+replace\n*** End Patch'
        self.assertEqual(self.event('apply_patch', {'command': patch})['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(dest.read_text(), 'existing')

    def test_canonical_duplicate_in_same_patch_is_rejected(self):
        patch = '*** Begin Patch\n*** Add File: login.plan.md\n+first\n*** Add File: docs/plans/login.plan.md\n+second\n*** End Patch'
        result = self.event('apply_patch', {'command': patch})
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(c.routes(self.root), {})

    def test_add_cannot_overwrite_existing_canonical_or_alias_target(self):
        target = self.root / 'docs/plans/login.plan.md'
        target.parent.mkdir(parents=True)
        target.write_text('KEEP')
        c.remember(self.root, 'login.plan.md', 'docs/plans/login.plan.md')
        for source in ('docs/plans/login.plan.md', 'login.plan.md'):
            patch = f'*** Begin Patch\n*** Add File: {source}\n+REPLACE\n*** End Patch'
            result = self.event('apply_patch', {'command': patch})
            self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(target.read_text(), 'KEEP')

    def test_two_sources_cannot_reserve_same_destination(self):
        self.event('Write', {'file_path': str(self.root / 'login.plan.md'), 'content': 'one'}, 'claude')
        second = self.event('Write', {'file_path': str(self.root / 'login-plan.md'), 'content': 'two'}, 'claude')
        self.assertEqual(second['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(len(c.routes(self.root)), 1)

    def test_read_does_not_reserve_and_rename_is_explicitly_unsupported(self):
        self.event('Read', {'file_path': str(self.root / 'login.plan.md')}, 'claude')
        self.assertEqual(c.routes(self.root), {})
        patch = '*** Begin Patch\n*** Update File: login.plan.md\n*** Move to: renamed.plan.md\n@@\n-old\n+new\n*** End Patch'
        result = self.event('apply_patch', {'command': patch})
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_code_rename_survives_alongside_document_routing(self):
        rename = '*** Update File: src/old.py\n*** Move to: src/new.py\n@@\n-old\n+new\n'
        patch = '*** Begin Patch\n' + rename + '*** End Patch'
        self.assertEqual(self.event('apply_patch', {'command': patch}), {})
        patch = '*** Begin Patch\n' + rename + '*** Add File: login.plan.md\n+plan\n*** End Patch'
        result = self.event('apply_patch', {'command': patch})['hookSpecificOutput']
        self.assertIn(rename, result['updatedInput']['command'])
        self.assertIn('*** Add File: docs/plans/login.plan.md', result['updatedInput']['command'])


if __name__ == '__main__':
    unittest.main()
