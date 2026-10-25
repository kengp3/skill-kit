"""C0 probe tests use only its public CLI and disposable evidence files."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROBE = Path(__file__).resolve().parent / 'harness/hook_probe.py'


class HookProbeTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / 'test-project'
        self.root.mkdir()
        self.evidence = self.root / 'probe-evidence'

    def event(self, name='SessionStart', **changes):
        event = {'hook_event_name': name, 'cwd': str(self.root),
                 'session_id': 'native-session', 'turn_id': 'native-turn',
                 'stop_hook_active': False}
        event.update(changes)
        return event

    def run_probe(self, event=None, root=None, evidence=None, raw=None):
        result = subprocess.run(
            [sys.executable, '-B', str(PROBE), '--test-root', str(root or self.root),
             '--evidence-dir', str(evidence or self.evidence)],
            input=json.dumps(event or self.event()) if raw is None else raw,
            text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return json.loads(result.stdout)

    def records(self):
        return [json.loads(path.read_text()) for path in sorted(self.evidence.glob('event-*.json'))]

    def test_records_only_native_whitelist_in_observed_order_without_execution(self):
        secret = 'PRIVATE-PROMPT-TRANSCRIPT-TOKEN'
        for name in ('SessionStart', 'UserPromptSubmit'):
            output = self.run_probe(self.event(name, prompt=secret, transcript=secret,
                                               credentials={'api_key': secret}))
            self.assertEqual(output, {})
        records = self.records()
        self.assertEqual([record['sequence'] for record in records], [1, 2])
        self.assertEqual([record['hook_event_name'] for record in records],
                         ['SessionStart', 'UserPromptSubmit'])
        self.assertEqual(set(records[0]), {'sequence', 'hook_event_name', 'session_id',
                                          'turn_id', 'stop_hook_active'})
        self.assertNotIn(secret, json.dumps(records))
        self.assertEqual(records[0]['session_id'], 'native-session')
        self.assertFalse((self.evidence / 'continuation.json').exists())

    def test_canary_is_once_per_attempt_even_when_native_turn_changes(self):
        protected = {self.root / 'product.txt': b'unchanged product',
                     self.root / 'contract.md': b'unchanged contract',
                     self.root / 'harness-project.json': b'{"host": "unverified"}'}
        for path, content in protected.items():
            path.write_bytes(content)
        first = self.run_probe(self.event('Stop'))
        self.assertEqual(first['decision'], 'block')
        self.assertIn('C0_PROBE_CONTINUATION_CONFIRMED', first['reason'])
        self.assertIn('Do not run tools', first['reason'])
        for event in (self.event('Stop'), self.event('Stop', turn_id='automatic-turn-2'),
                      self.event('Stop', stop_hook_active=True, turn_id='automatic-turn-3'),
                      self.event('UserPromptSubmit', turn_id='automatic-turn-4'),
                      self.event('Stop', session_id='another-session', turn_id='another-turn')):
            self.assertNotIn('decision', self.run_probe(event))
        receipt = json.loads((self.evidence / 'continuation.json').read_text())
        self.assertEqual(receipt['session_id'], 'native-session')
        self.assertEqual(receipt['turn_id'], 'native-turn')
        self.assertEqual(len(self.records()), 6)
        for path, content in protected.items():
            self.assertEqual(path.read_bytes(), content)

    def test_continuation_stop_is_observed_without_requesting_more_work(self):
        self.assertEqual(self.run_probe(self.event('Stop', stop_hook_active=True)), {})
        self.assertTrue(self.records()[0]['stop_hook_active'])

    def test_parallel_stops_have_one_reservation_and_unique_observation_order(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda index: self.run_probe(self.event('Stop', turn_id=f'turn-{index}')),
                                    range(8)))
        self.assertEqual(sum(output.get('decision') == 'block' for output in outputs), 1)
        records = self.records()
        self.assertEqual([record['sequence'] for record in records], list(range(1, 9)))
        self.assertEqual({record['turn_id'] for record in records}, {f'turn-{i}' for i in range(8)})
        # The winning stdout may be lost; another invocation must still not reissue.
        self.assertEqual(self.run_probe(self.event('Stop', turn_id='later-turn')), {})

    def test_scope_and_symlink_rejections_do_not_write_outside_test_root(self):
        outside = self.root.parent / 'outside'
        outside.mkdir()
        for event, evidence in ((self.event('Stop', cwd=str(outside)), self.evidence),
                                (self.event('Stop'), outside / 'evidence'),
                                (self.event('Stop'), self.root),
                                (self.event('Stop', cwd='relative'), self.evidence)):
            with self.subTest(event=event, evidence=evidence):
                output = self.run_probe(event, evidence=evidence)
                self.assertIn('not ready', output.get('systemMessage', ''))
                self.assertNotIn('decision', output)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(self.evidence.exists())
        self.evidence.symlink_to(outside, target_is_directory=True)
        output = self.run_probe(self.event('Stop'))
        self.assertIn('not ready', output.get('systemMessage', ''))
        self.assertEqual(list(outside.iterdir()), [])

    def test_record_failure_consumes_attempt_without_continuation_or_retry(self):
        self.evidence.mkdir()
        # A non-file where the first immutable observation must go is a save failure.
        obstacle = self.evidence / 'event-0001.json'
        obstacle.mkdir()
        output = self.run_probe(self.event('Stop'))
        self.assertIn('not ready', output.get('systemMessage', ''))
        self.assertNotIn('decision', output)
        obstacle.rmdir()
        self.assertEqual(self.run_probe(self.event('Stop', turn_id='changed-turn')), {})

    def test_missing_native_identity_is_preserved_without_fabrication(self):
        event = self.event('Stop')
        del event['turn_id']
        output = self.run_probe(event)
        # The development canary has a whole-attempt budget, independent of turn id.
        self.assertEqual(output.get('decision'), 'block')
        self.assertNotIn('turn_id', self.records()[0])
        self.assertNotIn('turn_id', json.loads((self.evidence / 'continuation.json').read_text()))
        missing_session = self.event('Stop', session_id=None)
        output = self.run_probe(missing_session)
        self.assertNotIn('decision', output)
        self.assertIn('not ready', output.get('systemMessage', ''))
        self.assertIsNone(self.records()[-1]['session_id'])
        fresh = self.root / 'missing-identity-evidence'
        self.assertNotIn('decision', self.run_probe(missing_session, evidence=fresh))
        self.assertFalse((fresh / 'continuation.json').exists())

    def test_bad_input_or_missing_control_flag_is_visible_without_block(self):
        for raw in ('not JSON', '[]', '{}', '{"hook_event_name":"Stop","hook_event_name":"Stop"}',
                    ' ' * (1024 * 1024 + 1)):
            with self.subTest(raw_length=len(raw)):
                output = self.run_probe(raw=raw)
                self.assertIn('not ready', output.get('systemMessage', ''))
                self.assertNotIn('decision', output)
        for changes in ({'stop_hook_active': 'false'}, {'session_id': ['private']},
                        {'hook_event_name': 'Unknown'}):
            output = self.run_probe(self.event('Stop', **changes))
            self.assertIn('not ready', output.get('systemMessage', ''))
            self.assertNotIn('decision', output)
        event = self.event('Stop')
        del event['stop_hook_active']
        output = self.run_probe(event)
        self.assertIn('not ready', output.get('systemMessage', ''))
        self.assertNotIn('decision', output)
        self.assertNotIn('stop_hook_active', self.records()[-1])

    def test_invalid_cli_arguments_do_not_use_exit_two(self):
        result = subprocess.run([sys.executable, '-B', str(PROBE)], input='{}',
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, '')
        self.assertIn('not ready', json.loads(result.stdout)['systemMessage'])


if __name__ == '__main__':
    unittest.main()
