"""Separate public behavior checks from this refactor's explicit structural contract."""
import ast
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

if len(sys.argv) not in (2, 3) or len(sys.argv) == 3 and sys.argv[2] != '--structure':
    raise SystemExit('usage: check.py <product-root> [--structure]')
PRODUCT = Path(sys.argv[1]).resolve(strict=True)
sys.path.insert(0, str(PRODUCT))
from harness.evidence import summarize_events

FIXTURE = Path(__file__).resolve().parent
METRICS = {'commands_completed', 'commands_nonzero', 'command_outcomes_unknown',
           'help_requests', 'retries', 'repairs'}


class Behavior(unittest.TestCase):
    def test_normal_summary_is_preserved(self):
        result = summarize_events([FIXTURE / 'events.jsonl'], thread_id='root',
                                  turn_ids=['first', 'second', 'empty'])
        self.assertEqual(result['metrics'], {'commands_completed': 3, 'commands_nonzero': 1,
            'command_outcomes_unknown': 0, 'help_requests': None, 'retries': None, 'repairs': None})
        self.assertEqual(result['coverage'], 'complete')
        self.assertEqual(result['final_turn_status'], 'completed')

    def test_conflict_unknown_summary_is_preserved(self):
        result = summarize_events([FIXTURE / 'conflict.jsonl'], thread_id='root', turn_ids=['first'])
        self.assertEqual(result['metrics'], {'commands_completed': 0, 'commands_nonzero': 0,
            'command_outcomes_unknown': 1, 'help_requests': None, 'retries': None, 'repairs': None})
        self.assertEqual(result['coverage'], 'partial')
        self.assertEqual(result['final_turn_status'], 'completed')

    def test_invalid_identity_and_missing_source_are_preserved(self):
        for turns in [[], ['first', 'first']]:
            with self.subTest(turns=turns), self.assertRaises(ValueError):
                summarize_events([], thread_id='root', turn_ids=turns)
        result = summarize_events([FIXTURE / 'missing.jsonl'], thread_id='root', turn_ids=['first'])
        self.assertEqual(result['coverage'], 'partial')
        self.assertEqual(result['final_turn_status'], 'unknown')


class Structure(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((PRODUCT / 'harness/evidence.py').read_text())
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.helper = functions.get('_command_metrics')
        self.public = functions['summarize_events']

    def test_helper_exists(self):
        self.assertIsNotNone(self.helper)

    def test_public_summary_uses_the_single_helper_result(self):
        calls = [node for node in ast.walk(self.public) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == '_command_metrics']
        self.assertEqual(len(calls), 1)
        assignments = [node for node in ast.walk(self.public) if isinstance(node, ast.Assign)
                       and node.value is calls[0]]
        self.assertEqual(len(assignments), 1)
        target = assignments[0].targets[0]
        self.assertIsInstance(target, ast.Name)
        returned = [value.id for node in ast.walk(self.public) if isinstance(node, ast.Dict)
                    for key, value in zip(node.keys, node.values)
                    if isinstance(key, ast.Constant) and key.value == 'metrics'
                    and isinstance(value, ast.Name)]
        self.assertIn(target.id, returned)

    def test_metrics_dictionary_belongs_to_helper(self):
        self.assertIsNotNone(self.helper)
        helper_keys = {key.value for node in ast.walk(self.helper) if isinstance(node, ast.Dict)
                       for key in node.keys if isinstance(key, ast.Constant)}
        self.assertTrue(METRICS <= helper_keys)
        public_keys = {key.value for node in ast.walk(self.public) if isinstance(node, ast.Dict)
                       for key in node.keys if isinstance(key, ast.Constant)}
        self.assertFalse(METRICS & public_keys)


if __name__ == '__main__':
    checks = Structure if len(sys.argv) == 3 else Behavior
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(checks))
    report = ET.Element('testsuite', name='command-metrics-refactor-v1',
                        tests=str(result.testsRun), failures=str(len(result.failures)),
                        errors=str(len(result.errors)), skipped=str(len(result.skipped)))
    with Path('TEST-command-metrics-refactor.xml').open('xb') as stream:
        ET.ElementTree(report).write(stream, encoding='utf-8', xml_declaration=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)
