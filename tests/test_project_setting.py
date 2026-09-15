"""Maintainer-only checks; the installed skill has no Python runtime."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / 'skills/project-setting'


class ReminderTest(unittest.TestCase):
    def test_isolated_reminders_without_external_commands_are_read_only(self):
        if os.name == 'nt':
            self.skipTest('POSIX shell replay; native Windows is tested separately')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installed = root / 'standalone-skill'
            shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns('__pycache__'))
            project = root / '中文 project' / 'nested'
            project.mkdir(parents=True)
            rule = project.parent / 'project-setting.md'
            rule.write_text((installed / 'assets/document-rules.md').read_text())
            document = project / 'existing.md'
            document.write_text('KEEP\n')
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for platform in ('codex', 'claude'):
                config = json.loads((installed / f'assets/{platform}-hooks.json').read_text())
                self.assertEqual(set(config['hooks']), {'SessionStart', 'SubagentStart'})
                for event, groups in config['hooks'].items():
                    handler = groups[0]['hooks'][0]
                    # Execute the shipped command, not a reconstructed approximation.
                    result = subprocess.run(['/bin/sh', '-c', handler['command']], cwd=project,
                                            env={'PATH': ''}, input='{}', text=True,
                                            capture_output=True, timeout=5, check=True)
                    if platform == 'claude':
                        payload = json.loads(result.stdout)
                        specific = payload['hookSpecificOutput']
                        self.assertEqual(specific['hookEventName'], event)
                        self.assertEqual(set(specific), {'hookEventName', 'additionalContext'})
                        reminder = specific['additionalContext']
                    else:
                        reminder = result.stdout
                    self.assertIn('project-setting.md', reminder)
                    self.assertIn('project-setting', reminder)
                    self.assertEqual(result.stderr, '')
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_reminder_does_not_depend_on_instruction_files_or_load_rules(self):
        if os.name == 'nt':
            self.skipTest('POSIX replay; native cmd has its own check')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rule = root / 'project-setting.md'
            rule.write_text('Private custom rule content')
            expected = {}
            for state in ('absent', 'created', 'changed', 'removed', 'missing-rules'):
                for name in ('AGENTS.md', 'CLAUDE.md'):
                    path = root / name
                    if state in ('created', 'changed'):
                        path.write_text(state + ': user instructions')
                    elif state == 'removed':
                        path.unlink()
                if state == 'missing-rules':
                    rule.unlink()
                before = {p.name: p.read_bytes() for p in root.iterdir()}
                for platform in ('codex', 'claude'):
                    config = json.loads((SKILL / f'assets/{platform}-hooks.json').read_text())
                    for event, groups in config['hooks'].items():
                        command = groups[0]['hooks'][0]['command']
                        result = subprocess.run(['/bin/sh', '-c', command], cwd=root,
                                                env={'PATH': ''}, input='{}', text=True,
                                                capture_output=True, timeout=5, check=True)
                        key = (platform, event)
                        if state == 'absent':
                            expected[key] = result.stdout
                        self.assertEqual(result.stdout, expected[key])
                        self.assertNotIn('Private custom rule content', result.stdout)
                self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    @unittest.skipUnless(os.name == 'nt', 'requires native Windows cmd.exe')
    def test_windows_shipped_commands_without_python_or_git(self):
        config = json.loads((SKILL / 'assets/codex-hooks.json').read_text())
        with tempfile.TemporaryDirectory(prefix='project-setting-') as directory:
            project = Path(directory) / '中文 nested'
            project.mkdir()
            env = {**os.environ, 'PATH': str(Path(os.environ['SystemRoot']) / 'System32')}
            for groups in config['hooks'].values():
                command = groups[0]['hooks'][0]['commandWindows']
                result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                        text=True, timeout=5, check=True)
                self.assertIn('project-setting.md', result.stdout)
                self.assertEqual(result.stderr, '')
            self.assertEqual(list(project.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
