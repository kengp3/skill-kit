"""Qualify one frozen development bug case; no model or host integration."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from harness.boundary import Limits
from harness.grader import case_inputs, qualify, regrade

CASE = Path(__file__).resolve().parent / 'fixtures/harness-cases/item-type-conflict'


class FrozenCaseTest(unittest.TestCase):
    def test_frozen_products_match_their_recorded_source(self):
        manifest = json.loads((CASE / 'case.json').read_text())
        self.assertEqual(manifest['case_id'], 'item-type-conflict-v1')
        for role, product in manifest['products'].items():
            self.assertEqual(len(product['revision']), 40)
            for name, expected in product['files'].items():
                source = CASE / 'products' / role / name
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected)

    def test_bug_qualification_requires_failed_defect_and_passing_correction(self):
        manifest = json.loads((CASE / 'case.json').read_text())
        files = {'requirement': CASE / 'task.md', 'checker': CASE / 'check.py',
                 'fixture': CASE / 'conflict.jsonl', 'normal': CASE / 'consistent.jsonl',
                 'manifest': CASE / 'case.json'}
        command = [sys.executable, '-I', '-B', str(CASE / 'check.py')]
        case = {'case_id': manifest['case_id'], 'kind': manifest['kind'],
                'inputs': case_inputs(files, dependencies={'python': sys.version},
                                     environment={}, command=command,
                                     reports=manifest['reports'])}
        with tempfile.TemporaryDirectory() as temp:
            observations = {}
            for role, expected in [('defect', False), ('correct', True)]:
                workspace = Path(temp).resolve() / role
                workspace.mkdir()
                product = CASE / 'products' / role
                result = regrade(case, product_id=role, product_root=product,
                    input_files=files, workspace=workspace,
                    argv=command + [str(product)], reports=manifest['reports'],
                    receipt=Path(temp) / (role + '.json'), limits=Limits())
                self.assertEqual(result['status'], 'graded', result)
                self.assertIs(result['product_passed'], expected)
                self.assertEqual(result['source_before'], result['source_after'])
                self.assertEqual(result['test_counts']['TEST-item-type-conflict.xml']['failures'],
                                 0 if expected else 2)
                observations[role] = result
            self.assertEqual(qualify(case, observations)['status'], 'qualified')


if __name__ == '__main__':
    unittest.main()
