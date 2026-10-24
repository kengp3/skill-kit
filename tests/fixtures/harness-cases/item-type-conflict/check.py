"""Check only the frozen item-type-conflict contract; emit the existing grader format."""
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    raise SystemExit('usage: check.py <product-root>')
sys.path.insert(0, str(Path(sys.argv[1]).resolve(strict=True)))
from harness.evidence import summarize_events

FIXTURE = Path(__file__).resolve().parent


class ItemTypeContract(unittest.TestCase):
    def assert_conflict(self, path):
        result = summarize_events([path], thread_id='root', turn_ids=['first'])
        self.assertEqual(result['final_turn_status'], 'completed')
        self.assertEqual(result['coverage'], 'partial')
        self.assertEqual(result['metrics']['commands_completed'], 0)
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 1)
        self.assertTrue(result['unverified'])

    def test_started_completed_type_conflict(self):
        self.assert_conflict(FIXTURE / 'conflict.jsonl')

    def test_reordered_type_conflict(self):
        records = (FIXTURE / 'conflict.jsonl').read_text().splitlines()
        path = Path('reordered.jsonl')
        with path.open('x') as stream:
            stream.write('\n'.join([records[1], records[0], records[2]]) + '\n')
        self.assert_conflict(path)

    def test_consistent_command_still_completes(self):
        result = summarize_events([FIXTURE / 'consistent.jsonl'],
                                  thread_id='root', turn_ids=['first'])
        self.assertEqual(result['final_turn_status'], 'completed')
        self.assertEqual(result['coverage'], 'complete')
        self.assertEqual(result['metrics']['commands_completed'], 1)
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 0)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ItemTypeContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = ET.Element('testsuite', name='item-type-conflict-v1',
                        tests=str(result.testsRun), failures=str(len(result.failures)),
                        errors=str(len(result.errors)), skipped=str(len(result.skipped)))
    with Path('TEST-item-type-conflict.xml').open('xb') as stream:
        ET.ElementTree(report).write(stream, encoding='utf-8', xml_declaration=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)
