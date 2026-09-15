import importlib.util
import json
import subprocess
import sys
from unittest import mock
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/project-setting/scripts/conventions.py'


class ConventionsTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('conventions', SCRIPT)
        self.c = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.c)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_import_without_fcntl_and_lock_release_on_failure(self):
        code = "import sys; sys.modules['fcntl'] = None; sys.path.insert(0, " + repr(str(SCRIPT.parent)) + "); import conventions"
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        # Simulate the Windows lock API here; the full suite exercises the real
        # selected backend when run on Windows.
        backend = mock.Mock(LK_NBLCK=2, LK_UNLCK=0)
        with mock.patch.object(self.c, 'msvcrt', backend):
            with self.assertRaisesRegex(RuntimeError, 'body failed'):
                with self.c.route_lock(self.root):
                    raise RuntimeError('body failed')
            self.assertEqual([call.args[1:] for call in backend.locking.call_args_list],
                             [(2, 1), (0, 1)])
            backend.locking.reset_mock()
            backend.locking.side_effect = OSError('busy')
            with self.assertRaises(OSError):
                with self.c.route_lock(self.root):
                    self.fail('must not enter an unlocked section')
            self.assertEqual(backend.locking.call_count, 1)

    def test_real_lock_released_after_exception(self):
        with self.assertRaises(RuntimeError):
            with self.c.route_lock(self.root):
                raise RuntimeError('release on exit')
        code = ("import sys; sys.path.insert(0, " + repr(str(SCRIPT.parent)) +
                "); import conventions as c; c.remember(" + repr(str(self.root)) +
                ", 'login.plan.md', 'docs/plans/login.plan.md')")
        subprocess.run([sys.executable, '-c', code], check=True, timeout=5)
        self.assertEqual(self.c.routes(self.root), {'login.plan.md': 'docs/plans/login.plan.md'})

    def test_init_custom_preserved_and_five_defaults(self):
        self.c.initialize(self.root)
        cfg = self.c.read_config(self.root)
        self.assertEqual(set(cfg['documents']), {'prd', 'spec', 'plan', 'adr', 'research'})
        cfg['documents']['plan']['path'] = '.project/plans/{slug}.md'
        self.c.save_config(self.root, cfg)
        self.c.initialize(self.root)
        self.assertEqual(self.c.read_config(self.root), cfg)
        self.assertEqual(self.c.resolve(self.root, 'login.plan.md')['destination'], '.project/plans/login.md')

    def test_root_discovery_ignores_git_and_explicit_root_wins(self):
        child = self.root / 'nested'
        child.mkdir()
        (self.root / '.git').mkdir()
        self.assertEqual(self.c.project_root(child), child)
        self.c.initialize(self.root)
        self.assertEqual(self.c.project_root(child), self.root)
        subprocess.run([sys.executable, str(SCRIPT), '--root', str(child), 'init'],
                       capture_output=True, check=True)
        self.assertTrue((child / self.c.CONFIG).exists())
        self.assertEqual(self.c.project_root(child), child)

    def test_unknown_missing_ambiguous_and_missing_name(self):
        self.assertEqual(self.c.resolve(self.root, 'login.plan.md')['reason'], 'missing_config')
        self.c.initialize(self.root)
        self.assertEqual(self.c.resolve(self.root, 'notes.md')['reason'], 'unmatched')
        self.assertEqual(self.c.resolve(self.root, 'plan.md')['reason'], 'missing_metadata')
        cfg = self.c.read_config(self.root)
        cfg['documents']['spec']['match'].append('*.plan.md')
        self.c.save_config(self.root, cfg)
        self.assertEqual(self.c.resolve(self.root, 'login.plan.md')['reason'], 'ambiguous')

    def test_all_default_destinations_and_adr_identifier(self):
        self.c.initialize(self.root)
        examples = {
            'login.prd.md': 'docs/prds/login.prd.md',
            'login.spec.md': 'docs/specs/login.spec.md',
            'login.plan.md': 'docs/plans/login.plan.md',
            '0001-database.adr.md': 'docs/adr/0001-database.adr.md',
            'cache.research.md': 'docs/research/cache.research.md',
        }
        for source, expected in examples.items():
            self.assertEqual(self.c.resolve(self.root, source)['destination'], expected)
        self.assertEqual(self.c.resolve(self.root, 'database.adr.md')['reason'], 'missing_metadata')

    def test_confirmed_choice_continuity_and_config_change(self):
        self.c.initialize(self.root)
        self.c.choose(self.root, 'plan.md', kind='plan', slug='login')
        result = self.c.resolve(self.root, 'plan.md')
        self.assertEqual(result['destination'], 'docs/plans/login.plan.md')
        target = self.root / result['destination']
        target.parent.mkdir(parents=True)
        target.write_text('first')
        self.assertEqual(self.c.resolve(self.root, 'plan.md', operation='read')['destination'], result['destination'])
        cfg = self.c.read_config(self.root)
        cfg['documents']['plan']['path'] = 'plans/{slug}.md'
        self.c.save_config(self.root, cfg)
        self.assertEqual(self.c.resolve(self.root, 'plan.md')['destination'], result['destination'])
        self.assertEqual(self.c.resolve(self.root, 'other.plan.md')['destination'], 'plans/other.md')

    def test_collision_and_path_escape(self):
        self.c.initialize(self.root)
        target = self.root / 'docs/plans/login.plan.md'
        target.parent.mkdir(parents=True)
        target.write_text('keep')
        self.assertEqual(self.c.resolve(self.root, 'login.plan.md')['reason'], 'collision')
        for value in ('../outside.md', '/tmp/outside.md', '.git/config'):
            with self.assertRaises(ValueError):
                self.c.choose(self.root, 'notes.md', destination=value)
        outside = Path(self.temp.name).parent
        (self.root / 'link').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.c.choose(self.root, 'notes.md', destination='link/outside.md')
        self.assertEqual(target.read_text(), 'keep')

    def test_custom_type_and_once_choice_do_not_change_match_rules(self):
        self.c.initialize(self.root)
        cfg = self.c.read_config(self.root)
        cfg['documents']['comparison'] = {'path': 'docs/comparisons/{slug}.md', 'description': '比較', 'match': ['*.comparison.md']}
        self.c.save_config(self.root, cfg)
        self.c.choose(self.root, 'comparison.md', kind='comparison', slug='databases')
        self.assertEqual(self.c.resolve(self.root, 'comparison.md')['destination'], 'docs/comparisons/databases.md')
        self.c.choose(self.root, 'notes.md', destination='notes/review.md')
        self.assertEqual(self.c.resolve(self.root, 'notes.md')['destination'], 'notes/review.md')
        self.assertEqual(self.c.read_config(self.root), cfg)

    def test_unrelated_files_and_canonical_paths(self):
        self.c.initialize(self.root)
        for name in ('README.md', 'src/app.py', 'skills/foo/references/plan.md', '.claude/skills/foo/SKILL.md'):
            self.assertEqual(self.c.resolve(self.root, name)['status'], 'ignore')
        self.assertEqual(self.c.resolve(self.root, 'docs/specs/login.spec.md')['destination'], 'docs/specs/login.spec.md')
        self.assertEqual(self.c.resolve(self.root, '/private/tmp/config.json')['status'], 'ignore')

    def test_invalid_config(self):
        self.c.initialize(self.root)
        for pattern in ('../{slug}.md', 'docs/{unknown}.md', '.git/{slug}.md'):
            cfg = self.c.read_config(self.root)
            cfg['documents']['plan']['path'] = pattern
            with self.assertRaises(ValueError):
                self.c.save_config(self.root, cfg)

    def test_alias_chains_rejected_in_both_insertion_orders(self):
        self.c.choose(self.root, 'notes.md', destination='docs/other.md')
        for source, destination in [('docs/other.md', 'docs/final.md'), ('start.md', 'notes.md')]:
            with self.assertRaises(ValueError):
                self.c.choose(self.root, source, destination=destination)
        self.assertEqual(self.c.resolve(self.root, 'notes.md')['destination'], 'docs/other.md')
        self.assertEqual(self.c.resolve(self.root, 'docs/other.md')['destination'], 'docs/other.md')

    def test_project_inside_skills_directory_still_routes(self):
        root = self.root / 'skills' / 'example'
        root.mkdir(parents=True)
        self.c.initialize(root)
        result = self.c.resolve(root, str(root / 'login.plan.md'))
        self.assertEqual(result['status'], 'route')
        self.assertEqual(result['destination'], 'docs/plans/login.plan.md')
        self.assertEqual(self.c.resolve(root, str(root / 'skills/foo/plan.md'))['status'], 'ignore')


if __name__ == '__main__':
    unittest.main()
