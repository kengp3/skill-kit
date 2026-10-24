"""Qualify the small offline bug, feature and refactor cases; no model execution."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from harness.boundary import Limits
from harness.grader import case_inputs, qualify, regrade

CASE = Path(__file__).resolve().parent / 'fixtures/harness-cases/item-type-conflict'
CASES = CASE.parent


class FrozenCaseTest(unittest.TestCase):
    def grade_case(self, directory, files, runs):
        manifest = json.loads((directory / 'case.json').read_text())
        files = {'requirement': directory / 'task.md', 'checker': directory / 'check.py',
                 'manifest': directory / 'case.json',
                 **{name: directory / path for name, path in files.items()}}
        command = [sys.executable, '-I', '-B', str(directory / 'check.py')]
        case = {'case_id': manifest['case_id'], 'kind': manifest['kind'],
                'inputs': case_inputs(files, dependencies={'python': sys.version},
                                     environment={}, command=command,
                                     reports=manifest['reports'])}
        with tempfile.TemporaryDirectory() as temp:
            observations = {}
            for role, (product_name, extra) in runs.items():
                workspace = Path(temp).resolve() / role
                workspace.mkdir()
                product = directory / 'products' / product_name
                result = regrade(case, product_id=role, product_root=product,
                    input_files=files, workspace=workspace,
                    argv=command + [str(product), *extra], reports=manifest['reports'],
                    receipt=Path(temp) / (role + '.json'), limits=Limits())
                self.assertEqual(result['status'], 'graded', result)
                self.assertEqual(result['source_before'], result['source_after'])
                observations[role] = result
        return case, observations

    def test_frozen_products_match_their_recorded_source(self):
        for name in ['item-type-conflict', 'command-counts-by-turn', 'command-metrics-refactor']:
            directory = CASES / name
            manifest = json.loads((directory / 'case.json').read_text())
            self.assertEqual(manifest['case_id'], name + '-v1')
            for role, product in manifest['products'].items():
                revision = product.get('revision', product.get('base_revision'))
                self.assertEqual(len(revision), 40)
                if 'base_revision' in product:
                    self.assertTrue(product['derivation'])
                for source_name, expected in product['files'].items():
                    source = directory / 'products' / role / source_name
                    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected)

    def test_bug_qualification_requires_failed_defect_and_passing_correction(self):
        case, observations = self.grade_case(CASE,
            {'fixture': 'conflict.jsonl', 'normal': 'consistent.jsonl'},
            {'defect': ('defect', []), 'correct': ('correct', [])})
        for role, expected in [('defect', False), ('correct', True)]:
            result = observations[role]
            self.assertIs(result['product_passed'], expected)
            self.assertEqual(result['test_counts']['TEST-item-type-conflict.xml']['failures'],
                             0 if expected else 2)
        self.assertEqual(qualify(case, observations)['status'], 'qualified')

    def test_feature_checks_new_counts_and_preserves_old_contract(self):
        directory = CASES / 'command-counts-by-turn'
        case, observations = self.grade_case(directory,
            {'fixture': 'events.jsonl', 'unknown': 'unknown.jsonl'},
            {'missing_feature': ('missing_feature', []), 'implemented': ('implemented', [])})
        self.assertFalse(observations['missing_feature']['product_passed'])
        self.assertTrue(observations['implemented']['product_passed'])
        self.assertEqual(observations['missing_feature']['test_counts']
                         ['TEST-command-counts-by-turn.xml']['failures'], 2)
        self.assertEqual(qualify(case, observations)['status'], 'qualified')
        incomplete = dict(observations, implemented=observations['missing_feature'])
        self.assertEqual(qualify(case, incomplete)['status'], 'unverified')

    def test_refactor_preserves_behavior_and_requires_the_structural_change(self):
        directory = CASES / 'command-metrics-refactor'
        case, observations = self.grade_case(directory,
            {'fixture': 'events.jsonl', 'conflict': 'conflict.jsonl'},
            {'before': ('before', []), 'after': ('after', []),
             'structure': ('after', ['--structure']),
             'unchanged_structure': ('before', ['--structure'])})
        for role in ['before', 'after', 'structure']:
            self.assertTrue(observations[role]['product_passed'])
        self.assertFalse(observations['unchanged_structure']['product_passed'])
        self.assertEqual(observations['unchanged_structure']['test_counts']
                         ['TEST-command-metrics-refactor.xml']['failures'], 3)
        self.assertEqual(qualify(case, observations)['status'], 'qualified')
        unchanged = dict(observations, structure=observations['unchanged_structure'])
        self.assertEqual(qualify(case, unchanged)['status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
