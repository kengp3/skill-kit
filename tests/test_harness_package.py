"""Exercise the distributable package through its command-line boundary."""
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/package_harness.py'


class PackageTest(unittest.TestCase):
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
