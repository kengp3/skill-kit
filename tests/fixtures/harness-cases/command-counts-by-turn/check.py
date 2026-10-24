"""Check the per-turn count feature and its compatibility contract."""
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    raise SystemExit('usage: check.py <product-root>')
sys.path.insert(0, str(Path(sys.argv[1]).resolve(strict=True)))
from harness.evidence import summarize_events

FIXTURE = Path(__file__).resolve().parent
TURNS = ['first', 'second', 'empty']


class PerTurnCounts(unittest.TestCase):
    def test_new_counts_include_failed_commands_but_not_duplicates_or_children(self):
        result = summarize_events([FIXTURE / 'events.jsonl'], thread_id='root', turn_ids=TURNS)
        self.assertEqual(result['metrics'].get('commands_by_turn'),
                         {'first': 2, 'second': 1, 'empty': 0})

    def test_unknown_commands_are_excluded_from_new_counts(self):
        result = summarize_events([FIXTURE / 'unknown.jsonl'],
                                  thread_id='root', turn_ids=['first'])
        self.assertEqual(result['metrics'].get('commands_by_turn'), {'first': 0})
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 1)
        self.assertEqual(result['coverage'], 'partial')

    def test_existing_summary_contract_is_preserved(self):
        result = summarize_events([FIXTURE / 'events.jsonl'], thread_id='root', turn_ids=TURNS)
        self.assertEqual(result['metrics']['commands_completed'], 3)
        self.assertEqual(result['metrics']['commands_nonzero'], 1)
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 0)
        self.assertEqual(result['coverage'], 'complete')
        self.assertEqual(result['final_turn_status'], 'completed')

    def test_existing_invalid_turn_ids_are_rejected(self):
        for turns in [[], ['first', 'first']]:
            with self.subTest(turns=turns), self.assertRaises(ValueError):
                summarize_events([FIXTURE / 'events.jsonl'], thread_id='root', turn_ids=turns)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PerTurnCounts))
    report = ET.Element('testsuite', name='command-counts-by-turn-v1',
                        tests=str(result.testsRun), failures=str(len(result.failures)),
                        errors=str(len(result.errors)), skipped=str(len(result.skipped)))
    with Path('TEST-command-counts-by-turn.xml').open('xb') as stream:
        ET.ElementTree(report).write(stream, encoding='utf-8', xml_declaration=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)
