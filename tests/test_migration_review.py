"""Behavior checks for the independently installable review helper."""
import importlib.util
import copy
import json
import os
import shutil
import socket
import sys
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/ai-code-review/scripts/review.py'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.STDOUT)


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location('review', SCRIPT)
        self.review = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.review)
        self.repos = []
        for name, branch in [('舊 repo', 'legacy'), ('new', 'migration')]:
            repo = self.root / name
            repo.mkdir()
            git(repo, 'init', '-q', '-b', branch)
            git(repo, 'config', 'user.email', 'fixture@example.invalid')
            git(repo, 'config', 'user.name', 'Fixture')
            (repo / 'rule.java').write_text(name + '\n')
            (repo / '.gitattributes').write_text('rule.java export-ignore\n')
            git(repo, 'add', '.')
            git(repo, 'commit', '-qm', 'fixture')
            self.repos.append(repo)

    def prepare(self):
        return self.review.prepare(self.repos[0], 'refs/heads/legacy',
                                   self.repos[1], 'refs/heads/migration', self.root / 'run')

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, timeout=3)

    @unittest.skipUnless(hasattr(os, 'mkfifo') and hasattr(socket, 'AF_UNIX'), 'POSIX special files')
    def test_snapshot_rejects_added_special_files(self):
        self.prepare()
        run = self.root / 'run'
        entry = run / 'snapshots/old/added'
        for kind in ('fifo', 'socket'):
            with self.subTest(kind=kind):
                sock = None
                try:
                    if kind == 'fifo':
                        os.mkfifo(entry)
                    else:
                        sock = socket.socket(socket.AF_UNIX)
                        sock.bind(str(entry))
                    result = self.cli('verify', '--run', run)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertEqual(json.loads(result.stdout)['status'], 'UNKNOWN')
                finally:
                    if sock:
                        sock.close()
                    entry.unlink()
        self.assertEqual(self.cli('verify', '--run', run).returncode, 0)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO')
    def test_all_evidence_read_paths_reject_fifo_without_blocking(self):
        manifest = self.prepare()
        run = self.root / 'run'
        (run / 'runner.txt').write_text('runner fixture')
        case = dict(id='one', input={}, initial_state={}, environment={}, observe=['result'])
        self.review.write_json(run / 'contract.json', dict(scope='fixture', cases=[case],
            artifacts={'runner.txt': self.review.digest(run / 'runner.txt')}))
        for side in ('old', 'new'):
            record = {k: v for k, v in case.items() if k != 'observe'}
            record['observed'] = {'result': 'same'}
            self.review.write_json(run / (side + '.json'), dict(side=side,
                commit=manifest[side]['commit'], command=['fixture'], exit_code=0, records=[record],
                manifest_sha256=self.review.digest(run / 'manifest.json'),
                contract_sha256=self.review.digest(run / 'contract.json')))
        for name in ('runner.txt', 'manifest.json', 'contract.json', 'old.json', 'new.json'):
            with self.subTest(path=name):
                path = run / name
                original = path.read_bytes()
                path.unlink()
                os.mkfifo(path)
                output = run / (name + '.result')
                try:
                    result = self.cli('compare', '--run', run, '--contract', run / 'contract.json',
                                      '--old', run / 'old.json', '--new', run / 'new.json', '--out', output)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertEqual(json.loads(result.stdout)['status'], 'UNKNOWN')
                    self.assertFalse(output.exists())
                finally:
                    path.unlink()
                    path.write_bytes(original)
        result = self.cli('compare', '--run', run, '--contract', run / 'contract.json',
                          '--old', run / 'old.json', '--new', run / 'new.json', '--out', run / 'ok.json')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'PASS')

    def test_prepare_checks_case_collisions_in_every_path_component(self):
        repo = self.repos[0]
        blob = git(repo, 'rev-parse', 'HEAD:rule.java').decode().strip()
        def make_tree(node):
            entries = []
            for name, value in node.items():
                entries.append(f'040000 tree {make_tree(value)}\t{name}\n' if isinstance(value, dict)
                               else f'100644 blob {blob}\t{name}\n')
            return subprocess.check_output(['git', '-C', str(repo), 'mktree'],
                                           input=''.join(entries).encode()).decode().strip()
        for index, names in enumerate((['A/x', 'a/y'], ['A/B/x', 'A/b/y'],
                                       ['A/x', 'A/X'], ['A', 'a/y'], ['A/x', 'A/y'])):
            with self.subTest(paths=names):
                tree = {}
                for name in names:
                    node = tree
                    parts = name.split('/')
                    for part in parts[:-1]:
                        node = node.setdefault(part, {})
                    node[parts[-1]] = None
                commit = git(repo, 'commit-tree', make_tree(tree), '-m', 'path fixture').decode().strip()
                out = self.root / f'case-{index}'
                result = self.cli('prepare', '--old-repo', repo, '--old-ref', commit,
                                  '--new-repo', repo, '--new-ref', commit, '--out', out)
                if index == 4:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(self.cli('verify', '--run', out).returncode, 0)
                else:
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertEqual(json.loads(result.stdout)['status'], 'UNKNOWN')
                    self.assertFalse((out / 'manifest.json').exists())

    def test_freezes_independent_refs_without_dirty_or_archive_filters(self):
        baseline = git(self.repos[0], 'show', 'HEAD:rule.java')
        (self.repos[0] / 'rule.java').write_text('dirty')
        before = git(self.repos[0], 'status', '--porcelain')
        manifest = self.prepare()
        self.assertEqual((self.root / 'run/snapshots/old/rule.java').read_bytes(), baseline)
        self.assertEqual(git(self.repos[0], 'status', '--porcelain'), before)
        self.assertNotEqual(manifest['old']['commit'], manifest['new']['commit'])
        self.review.verify(self.root / 'run')
        (self.root / 'run/snapshots/old/rule.java').write_text('changed')
        with self.assertRaises(ValueError):
            self.review.verify(self.root / 'run')

    def test_refuses_existing_output_and_unsupported_links(self):
        self.prepare()
        with self.assertRaises(FileExistsError):
            self.prepare()
        link = self.repos[0] / 'escape'
        link.symlink_to('/tmp')
        git(self.repos[0], 'add', 'escape')
        git(self.repos[0], 'commit', '-qm', 'link')
        with self.assertRaises(ValueError):
            self.review.prepare(self.repos[0], 'HEAD', self.repos[1], 'HEAD', self.root / 'unsafe')

    def test_installed_copy_cli_is_self_contained_and_invalid_inputs_fail_closed(self):
        installed = self.root / 'installed'
        shutil.copytree(SCRIPT.parent.parent, installed)
        script = installed / 'scripts/review.py'
        def cli(*args):
            return subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                                  cwd=self.root, capture_output=True, text=True)
        result = cli('prepare', '--old-repo', self.repos[0], '--old-ref', 'legacy',
                     '--new-repo', self.repos[1], '--new-ref', 'migration', '--out', self.root / 'copy-run')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        git(self.repos[0], 'commit', '--allow-empty', '-qm', 'branch moved')
        self.assertEqual(cli('verify', '--run', self.root / 'copy-run').returncode, 0)
        extra = self.root / 'copy-run/snapshots/new/injected.java'
        extra.write_text('changed build input')
        self.assertEqual(cli('verify', '--run', self.root / 'copy-run').returncode, 2)
        extra.unlink()
        (self.root / 'copy-run/manifest.json').write_text('[]')
        self.assertEqual(cli('verify', '--run', self.root / 'copy-run').returncode, 2)
        # Missing/invalid evidence must not turn into a successful empty comparison.
        (self.root / 'bad.json').write_text('{"v":NaN}')
        with self.assertRaises(ValueError):
            self.review.read_json(self.root / 'bad.json')
        (self.root / 'bad.json').write_text('[]')
        with self.assertRaises(ValueError):
            self.review.read_json(self.root / 'bad.json')
        (self.root / 'bad.json').write_text('{"v":1,"v":2}')
        with self.assertRaises(ValueError):
            self.review.read_json(self.root / 'bad.json')
        for value in ('9007199254740992.0', '9007199254740993.0', '1e999'):
            (self.root / 'bad.json').write_text('{"amount":' + value + '}')
            with self.assertRaises(ValueError):
                self.review.read_json(self.root / 'bad.json')

    def test_observations_detect_difference_missing_evidence_and_staleness(self):
        manifest = self.prepare()
        run = self.root / 'run'
        runner = run / 'runner.txt'
        runner.write_text('test runner')
        case = {'id': 'retry', 'input': {'amount': '1.00'}, 'initial_state': {},
                'environment': {'clock': 'fixed'}, 'observe': ['result', 'state', 'events']}
        contract = {'scope': 'test workflow', 'cases': [case],
                    'artifacts': {'runner.txt': self.review.digest(runner)}}
        self.review.write_json(run / 'contract.json', contract)
        record = {k: v for k, v in case.items() if k != 'observe'}
        record['observed'] = {'result': None, 'state': {'balance': '1.00'}, 'events': ['created']}
        envelopes = {}
        for side in ('old', 'new'):
            envelopes[side] = {'side': side, 'commit': manifest[side]['commit'],
                'manifest_sha256': self.review.digest(run / 'manifest.json'),
                'contract_sha256': self.review.digest(run / 'contract.json'),
                'command': ['test-runner'], 'exit_code': 0, 'records': [copy.deepcopy(record)]}
        def compare():
            for side, value in envelopes.items():
                (run / (side + '.json')).write_text(json.dumps(value))
            return self.review.compare(run, run / 'contract.json', run / 'old.json', run / 'new.json')
        self.assertEqual(compare()['status'], 'PASS')
        for command in (True, 1, 'java Harness', {'tool': 'java'}, [True], [], [[]],
                        [''], ['java', 1], ['java', '\x00'], [['java'], ['']]):
            with self.subTest(command=command):
                envelopes['new']['command'] = command
                self.assertEqual(compare()['status'], 'UNKNOWN')
        for command in (['java', 'Harness', ''], [['javac', 'Harness.java'], ['java', 'Harness']]):
            envelopes['new']['command'] = command
            self.assertEqual(compare()['status'], 'PASS')
        envelopes['new']['records'][0]['observed']['extra_write'] = ['unexpected']
        extra = compare()
        self.assertEqual(extra['status'], 'UNKNOWN')
        self.assertIn('new: undeclared observation: extra_write', extra['cases'][0]['unknowns'])
        cli = subprocess.run([sys.executable, '-B', str(SCRIPT), 'compare', '--run', str(run),
            '--contract', str(run / 'contract.json'), '--old', str(run / 'old.json'),
            '--new', str(run / 'new.json'), '--out', str(run / 'extra-result.json')],
            capture_output=True, text=True)
        self.assertEqual(cli.returncode, 2, cli.stdout + cli.stderr)
        self.assertEqual(json.loads((run / 'extra-result.json').read_text())['status'], 'UNKNOWN')
        envelopes['new']['records'][0]['observed']['events'].append('created')
        self.assertEqual(compare()['status'], 'FAIL')
        envelopes['new']['records'] = [copy.deepcopy(record)]
        for side in ('old', 'new'):
            envelopes[side]['records'][0]['observed']['extra_write'] = []
        self.assertEqual(compare()['status'], 'UNKNOWN')
        for side in ('old', 'new'):
            envelopes[side]['records'] = [copy.deepcopy(record)]
        envelopes['new']['records'][0]['observed']['events'].append('created')
        self.assertEqual(compare()['status'], 'FAIL')
        del envelopes['new']['records'][0]['observed']['state']
        self.assertEqual(compare()['status'], 'FAIL')
        envelopes['new']['records'][0]['observed']['events'] = ['created']
        self.assertEqual(compare()['status'], 'UNKNOWN')
        envelopes['new']['records'] = [copy.deepcopy(record)]
        envelopes['new']['records'][0]['observed']['result'] = False
        envelopes['old']['records'][0]['observed']['result'] = 0
        self.assertEqual(compare()['status'], 'FAIL')
        envelopes['new']['exit_code'] = 1
        self.assertEqual(compare()['status'], 'UNKNOWN')
        runner.write_text('changed after testing')
        with self.assertRaises(ValueError):
            compare()

    def test_poc_cannot_write_inside_source_repo_even_on_failure(self):
        poc = Path(__file__).with_name('poc_migration_demo002.py')
        self.assertTrue(poc.is_file(), f'Missing test dependency: {poc}')
        output = self.repos[0] / 'evidence'
        result = subprocess.run([sys.executable, '-B', str(poc), '--repo', str(self.repos[0]),
            '--out', str(output), '--spring-context', '/missing.jar', '--spring-core', '/missing.jar'],
            capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('--out must be outside the source repository', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse(output.exists(), result.stderr)
        self.assertEqual(git(self.repos[0], 'status', '--porcelain'), b'')


if __name__ == '__main__':
    unittest.main()
