import hashlib
import itertools
import json
from pathlib import Path
import unittest

from harness.evidence import summarize_events


ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):
    def check_summary(self, result, conflict):
        self.assertEqual(result['coverage'], 'partial' if conflict else 'complete')
        self.assertEqual(result['metrics']['commands_completed'], 0 if conflict else 1)
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 1 if conflict else 0)
        self.assertEqual(result['final_turn_status'], 'completed')
        self.assertEqual(len(result['items']), 1)
        item = result['items'][0]
        self.assertEqual(item['type'], 'commandExecution')
        self.assertEqual(len(item['evidence']), 2)
        if conflict:
            self.assertEqual(item['status'], 'unknown')
            self.assertIsNone(item['exit_code'])
            self.assertTrue(any('Conflicting' in issue for issue in result['unverified']))

    def test_fixed_inputs(self):
        for name, conflict in [('consistent', False), ('conflict', True)]:
            with self.subTest(name=name):
                self.check_summary(summarize_events([ROOT / (name + '.jsonl')],
                                   thread_id='root', turn_ids=['first']), conflict)

    def test_event_permutations(self):
        # Separate source files exercise the public paths interface without
        # changing either fixed input or depending on an internal parser mock.
        directory = ROOT / 'verification'
        for name, conflict in [('consistent', False), ('conflict', True)]:
            paths = []
            for index, line in enumerate((ROOT / (name + '.jsonl')).read_text().splitlines()):
                path = directory / f'{name}-event-{index}.jsonl'
                path.write_text(line + '\n')
                paths.append(path)
            for permutation in itertools.permutations(paths):
                with self.subTest(name=name, order=[p.name for p in permutation]):
                    self.check_summary(summarize_events(permutation, thread_id='root',
                                                       turn_ids=['first']), conflict)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EvidenceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    fingerprints = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [ROOT / 'harness/evidence.py', Path(__file__),
                              ROOT / 'consistent.jsonl', ROOT / 'conflict.jsonl']}
    output = {'passed': result.wasSuccessful(), 'tests_run': result.testsRun,
              'failures': len(result.failures), 'errors': len(result.errors),
              'sha256': fingerprints}
    import sys
    destination = sys.argv[1] if len(sys.argv) > 1 else 'results.json'
    (ROOT / 'verification' / destination).write_text(json.dumps(output, indent=2) + '\n')
    sys.exit(0 if result.wasSuccessful() else 1)
