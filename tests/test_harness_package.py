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
    def test_registered_hooks_run_from_package_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            package = root / 'runtime with spaces'
            subprocess.run([sys.executable, str(SCRIPT), str(package)], check=True,
                           capture_output=True)
            plugin = json.loads((package / '.codex-plugin/plugin.json').read_text())
            self.assertEqual(plugin['version'], '0.2.0')
            hooks = json.loads((package / plugin['hooks']).read_text())['hooks']
            self.assertEqual(set(hooks), {'SessionStart', 'UserPromptSubmit', 'Stop'})
            project = root / 'project with spaces'
            (project / 'contracts').mkdir(parents=True)
            config = {'schema_version': 1, 'project_root': str(project),
                      'contract_dir': 'contracts', 'receipt_dir': 'receipts',
                      'host': {'session_identity': True, 'user_turn_identity': True,
                               'stop_continuation': True}}
            (project / 'harness-project.json').write_text(json.dumps(config))
            contract = {
                'schema_version': 1, 'task_id': 'packaged-task',
                'project_root': str(project), 'owner_session_id': 'package-session',
                'status': 'pending', 'objective': 'Verify packaged integration',
                'scope': ['offline packaging check'],
                'requirements': [{'id': 'T1', 'outcome': 'Complete the check',
                                  'status': 'pending', 'depends_on': [], 'evidence': []}],
                'authorization': {'user_turn_id': 'package-turn', 'mode': 'execute',
                                  'basis': 'Synthetic offline fixture, not host qualification'},
                'recovery': {'next_action': 'Check integration', 'blockers': [],
                             'unknown_operations': [], 'cancellation_reason': ''},
            }
            contract_path = project / 'contracts/task.md'
            contract_path.write_text('<!-- task-harness-contract:v1 -->\n```json\n'
                                     + json.dumps(contract) + '\n```\n<!-- /task-harness-contract -->\n')
            original = contract_path.read_bytes()
            outputs = []
            for name in ('SessionStart', 'UserPromptSubmit', 'Stop', 'Stop'):
                self.assertEqual(len(hooks[name]), 1)
                self.assertEqual(len(hooks[name][0]['hooks']), 1)
                handler = hooks[name][0]['hooks'][0]
                self.assertEqual(handler['type'], 'command')
                event = {'hook_event_name': name, 'session_id': 'package-session',
                         'turn_id': 'package-turn', 'cwd': str(project),
                         'stop_hook_active': False}
                result = subprocess.run(['/bin/sh', '-c', handler['command']],
                                        input=json.dumps(event), text=True, capture_output=True,
                                        cwd=project, env={**os.environ, 'PLUGIN_ROOT': str(package)},
                                        timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(result.stderr)
                outputs.append(json.loads(result.stdout))
            self.assertIn(str(contract_path), outputs[0]['hookSpecificOutput']['additionalContext'])
            self.assertIn('package-turn', outputs[1]['hookSpecificOutput']['additionalContext'])
            self.assertEqual(outputs[2]['decision'], 'block')
            self.assertEqual(outputs[3], {})
            self.assertEqual(len(list((project / 'receipts').glob('*.json'))), 1)
            self.assertEqual(contract_path.read_bytes(), original)
            self.assertTrue((package / 'skills/task-harness/references/task-contract.md').is_file())
            self.assertEqual(subprocess.run([sys.executable, str(SCRIPT), '--verify', str(package)],
                                           capture_output=True).returncode, 0)

    def test_missing_or_linked_hooks_are_rejected(self):
        for relative, linked in (('hooks/hooks.json', False), ('hooks/task_harness.py', False),
                                 ('hooks/task_harness.py', True), ('hooks', True)):
            with self.subTest(relative=relative, linked=linked), tempfile.TemporaryDirectory() as temp:
                fixture = Path(temp) / 'source'
                for directory in ('scripts', 'packaging', 'skills'):
                    shutil.copytree(ROOT / directory, fixture / directory)
                source = fixture / 'packaging/codex' / relative
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
            for relative in ('hooks/hooks.json', 'hooks/task_harness.py'):
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
