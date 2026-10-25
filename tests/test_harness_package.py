"""Exercise the distributable package through its command-line boundary."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/package_harness.py'


class PackageTest(unittest.TestCase):
    @unittest.skipUnless(os.name == 'posix', 'POSIX command replay; Windows qualification is separate')
    def test_copied_skill_supplies_the_same_executable_hooks_as_plugin(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'project'
            copied_skill = project / '.agents/skills/task-harness'
            shutil.copytree(ROOT / 'skills/task-harness', copied_skill)
            asset = copied_skill / 'assets/codex-hooks.json'
            hooks = json.loads(asset.read_text())['hooks']
            package = root / 'package'
            subprocess.run([sys.executable, str(SCRIPT), str(package)], check=True,
                           capture_output=True)
            self.assertEqual(asset.read_bytes(), (package / 'hooks/hooks.json').read_bytes())
            self.assertEqual(asset.read_bytes(),
                             (package / 'skills/task-harness/assets/codex-hooks.json').read_bytes())
            before = {p.relative_to(project): p.read_bytes()
                      for p in project.rglob('*') if p.is_file()}
            for event, groups in hooks.items():
                handler = groups[0]['hooks'][0]
                result = subprocess.run(['/bin/sh', '-c', handler['command']], cwd=project,
                                        env={'PATH': ''}, capture_output=True, text=True,
                                        timeout=5, check=True)
                self.assertEqual(result.stderr, '')
                if event == 'Stop':
                    self.assertEqual(json.loads(result.stdout), {})
                else:
                    self.assertIn('task-harness', result.stdout)
            self.assertEqual(before, {p.relative_to(project): p.read_bytes()
                                      for p in project.rglob('*') if p.is_file()})

    @unittest.skipUnless(os.name == 'posix', 'POSIX command replay; Windows qualification is separate')
    def test_static_hooks_run_without_runtime_and_do_not_mutate_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            package = root / 'package with spaces'
            subprocess.run([sys.executable, str(SCRIPT), str(package)], check=True,
                           capture_output=True)
            plugin = json.loads((package / '.codex-plugin/plugin.json').read_text())
            self.assertEqual(plugin['name'], 'kengp3-harness')
            hooks = json.loads((package / plugin['hooks']).read_text())['hooks']
            self.assertEqual(set(hooks), {'SessionStart', 'UserPromptSubmit', 'Stop'})
            project = root / 'project with spaces'
            project.mkdir()
            (project / 'project-setting.md').write_text('Custom rules stay unchanged.\n')
            (project / 'keep.txt').write_text('KEEP\n')
            before = {p.name: p.read_bytes() for p in project.iterdir()}
            for name in ('SessionStart', 'UserPromptSubmit', 'Stop', 'Stop'):
                with self.subTest(event=name):
                    self.assertEqual(len(hooks[name]), 1)
                    self.assertEqual(len(hooks[name][0]['hooks']), 1)
                    handler = hooks[name][0]['hooks'][0]
                    self.assertEqual(handler['type'], 'command')
                    result = subprocess.run(['/bin/sh', '-c', handler['command']],
                                            input='not JSON: static hooks need not parse input',
                                            text=True, capture_output=True, cwd=project,
                                            env={'PATH': '', 'PLUGIN_ROOT': str(package)}, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, '')
                    if name == 'Stop':
                        self.assertEqual(json.loads(result.stdout), {})
                    else:
                        self.assertIn('task-harness', result.stdout)
                        self.assertIn('explicit', result.stdout)
                        self.assertIn('project-setting.md', result.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in project.iterdir()})
            self.assertFalse((package / 'hooks/task_harness.py').exists())
            for relative in ('references/project-settings.md', 'references/settings-migration.md',
                             'references/model-selection.md', 'assets/project-settings.md'):
                self.assertTrue((package / 'skills/task-harness' / relative).is_file())
            self.assertEqual(subprocess.run([sys.executable, str(SCRIPT), '--verify', str(package)],
                                           capture_output=True).returncode, 0)

    def test_missing_or_linked_hooks_are_rejected(self):
        for relative, linked in (('skills/task-harness/assets/codex-hooks.json', False),
                                 ('skills/task-harness/assets/codex-hooks.json', True),
                                 ('skills/task-harness/assets', True)):
            with self.subTest(relative=relative, linked=linked), tempfile.TemporaryDirectory() as temp:
                fixture = Path(temp) / 'source'
                for directory in ('scripts', 'packaging', 'skills'):
                    shutil.copytree(ROOT / directory, fixture / directory)
                source = fixture / relative
                outside = Path(temp) / 'outside'
                source.rename(outside)
                if linked:
                    source.symlink_to(outside, target_is_directory=outside.is_dir())
                target = Path(temp) / 'release'
                result = subprocess.run([sys.executable, str(fixture / 'scripts/package_harness.py'),
                                         str(target)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertFalse(target.exists())

    def test_verify_detects_changed_or_missing_packaged_hooks(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / 'runtime'
            subprocess.run([sys.executable, str(SCRIPT), str(package)], check=True,
                           capture_output=True)
            manifest = json.loads((package / 'runtime-manifest.json').read_text())
            command = [sys.executable, str(SCRIPT), '--verify', str(package)]
            for relative in ('hooks/hooks.json', 'skills/task-harness/references/project-settings.md'):
                self.assertIn(relative, manifest['files'])
                path = package / relative
                original = path.read_bytes()
                path.write_bytes(original + b'\nchanged\n')
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
                path.unlink()
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
                path.write_bytes(original)
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_output_alias_cannot_write_into_runtime_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / 'source'
            for directory in ('scripts', 'packaging', 'skills'):
                shutil.copytree(ROOT / directory, fixture / directory)
            alias = Path(temp) / 'alias'
            alias.symlink_to(fixture / 'skills', target_is_directory=True)
            result = subprocess.run([sys.executable,
                str(fixture / 'scripts/package_harness.py'), str(alias / 'generated')],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((fixture / 'skills/generated').exists())

    def test_missing_or_linked_skill_root_is_rejected(self):
        for linked in (False, True):
            with self.subTest(linked=linked), tempfile.TemporaryDirectory() as temp:
                fixture = Path(temp) / 'source'
                for directory in ('scripts', 'packaging', 'skills'):
                    shutil.copytree(ROOT / directory, fixture / directory)
                skill = fixture / 'skills/define-task'
                shutil.rmtree(skill)
                if linked:
                    outside = Path(temp) / 'private'
                    outside.mkdir()
                    (outside / 'SKILL.md').write_text('private data')
                    skill.symlink_to(outside, target_is_directory=True)
                target = Path(temp) / 'release'
                result = subprocess.run([sys.executable,
                    str(fixture / 'scripts/package_harness.py'), str(target)],
                    capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertFalse(target.exists())

    def test_existing_release_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'release'
            target.mkdir()
            sentinel = target / 'keep'
            sentinel.write_text('original')
            result = subprocess.run([sys.executable, str(SCRIPT), str(target)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), 'original')

    def test_verify_rejects_changed_and_unlisted_files(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'release'
            subprocess.run([sys.executable, str(SCRIPT), str(target)], check=True,
                           capture_output=True)
            command = [sys.executable, str(SCRIPT), '--verify', str(target)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            extra = target / 'answer.txt'
            extra.write_text('must not be distributed')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            extra.unlink()
            (target / 'skills/task-harness/SKILL.md').write_text('stale release')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_package_runs_outside_checkout_and_excludes_research(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / 'runtime'
            result = subprocess.run([sys.executable, str(SCRIPT), str(package)],
                                    cwd=temp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((package / 'runtime-manifest.json').read_text())
            self.assertTrue(manifest['files'])
            self.assertFalse((package / 'docs').exists())
            for skill in ('task-harness', 'define-task', 'project-setting', 'ai-code-review'):
                self.assertTrue((package / 'skills' / skill / 'SKILL.md').is_file())
            check = subprocess.run([sys.executable,
                str(package / 'skills/task-harness/scripts/run_check.py'),
                '--output', str(Path(temp) / 'receipt.json'), '--',
                sys.executable, '-c', 'print("standalone")'], cwd=temp,
                capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertEqual(json.loads((Path(temp) / 'receipt.json').read_text())['stdout'],
                             'standalone\n')


if __name__ == '__main__':
    unittest.main()
