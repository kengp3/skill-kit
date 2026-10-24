"""Replay saved native evidence without launching a model or host."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness.evidence import summarize_events, replay_smoke

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'docs/research/codex-coding-harness-implementation-evidence'

def item(thread='root', turn='first', item_id='check', exit_code=0):
    return {'method': 'item/completed', 'params': {
        'threadId': thread, 'turnId': turn, 'item': {
            'id': item_id, 'type': 'commandExecution', 'status': 'completed',
            'exitCode': exit_code}}}


def completed(thread='root', turn='first', status='completed'):
    return {'method': 'turn/completed', 'params': {
        'threadId': thread, 'turn': {'id': turn, 'status': status}}}


class EvidenceTest(unittest.TestCase):
    def test_root_scope_and_duplicate_items_preserve_source_references(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'rpc.jsonl'
            events = [item(), item(), item('child'), completed('child'), completed()]
            path.write_text(''.join(json.dumps({'response': event}) + '\n'
                                    for event in events))
            result = summarize_events([path], thread_id='root', turn_ids=['first'])
        self.assertEqual(result['final_turn_status'], 'completed')
        self.assertEqual(result['metrics']['commands_completed'], 1)
        self.assertEqual(result['metrics']['commands_nonzero'], 0)
        self.assertEqual(len(result['items']), 1)
        self.assertEqual([ref['line'] for ref in result['items'][0]['evidence']], [1, 2])
        self.assertEqual(result['sources'][0]['path'], str(path))
        self.assertEqual(len(result['sources'][0]['sha256']), 64)
        self.assertIsNone(result['metrics']['help_requests'])

    def test_conflicts_and_missing_terminal_evidence_remain_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'rpc.jsonl'
            events = [item(), item(exit_code=1), completed(),
                      completed(status='failed'), item(turn='second', exit_code=None)]
            path.write_text(''.join(json.dumps({'response': event}) + '\n'
                                    for event in events))
            result = summarize_events([path], thread_id='root',
                                      turn_ids=['first', 'second'])
        self.assertEqual(result['turns'][0]['status'], 'unknown')
        self.assertEqual(result['final_turn_status'], 'unknown')
        self.assertEqual(result['metrics']['commands_completed'], 0)
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 2)
        self.assertGreater(len(result['unverified']), 1)

    def test_malformed_and_missing_sources_are_disclosed_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'rpc.jsonl'
            path.write_text('\n'.join([
                'truncated', '[]', '{"response":null}',
                json.dumps({'response': {'method': 'item/completed', 'params': None}}),
                json.dumps({'response': {'method': 'item/completed', 'params': {
                    'threadId': 'root', 'turnId': 'first', 'item': []}}}),
                json.dumps({'response': item()}),
            ]))
            result = summarize_events([path, Path(temp) / 'missing'],
                                      thread_id='root', turn_ids=['first'])
        self.assertEqual(result['final_turn_status'], 'unknown')
        self.assertEqual(result['metrics']['commands_completed'], 1)
        self.assertEqual(result['coverage'], 'partial')
        self.assertGreaterEqual(len(result['unverified']), 7)

    def test_identity_must_be_explicit_and_turn_ids_unique(self):
        for thread, turns in [('', ['one']), ('root', []), ('root', ['one', 'one']),
                              ('root', [None]), ('root', 'one')]:
            with self.subTest(thread=thread, turns=turns), self.assertRaises(ValueError):
                summarize_events([], thread_id=thread, turn_ids=turns)

    def test_saved_abc_counts_root_commands_across_continuation(self):
        for group, counts in [('A', (16, 3)), ('B', (18, 3)), ('C', (26, 1))]:
            with self.subTest(group=group):
                folder = ARCHIVE / f'cli-smoke-{group}'
                state = json.loads((folder / 'state.json').read_text())
                paths, turns = [folder / 'rpc.jsonl'], [state['turn_id']]
                if group == 'C':
                    continuation = ARCHIVE / 'cli-smoke-C-continuation-1'
                    paths.append(continuation / 'rpc.jsonl')
                    turns.append(json.loads((continuation / 'state.json').read_text())['turn_id'])
                result = summarize_events(paths, thread_id=state['thread_id'], turn_ids=turns)
                self.assertEqual(result['final_turn_status'], 'completed')
                self.assertEqual(result['metrics']['commands_completed'], counts[0])
                self.assertEqual(result['metrics']['commands_nonzero'], counts[1])
                self.assertEqual(result['metrics']['command_outcomes_unknown'], 0)
                self.assertIsNone(result['metrics']['repairs'])
                if group == 'C':
                    self.assertEqual(result['turns'][0]['status'], 'unknown')
                    self.assertEqual(result['coverage'], 'partial')

    def test_old_trial_replay_separates_grades_diagnostics_and_unknown_costs(self):
        result = replay_smoke(ARCHIVE)
        self.assertEqual(len(result), 3)
        a, b, c = result
        self.assertEqual(b['schema_version'], 2)
        self.assertTrue(b['observations']['frozen_external_grade']['passed'])
        self.assertFalse(b['observations']['later_factory_diagnostic']['passed'])
        self.assertEqual(b['delivery']['status'], 'completed_with_known_defect')
        self.assertEqual(c['observations']['trial_attempts'], 1)
        self.assertEqual(len(c['native_identity']['turn_ids']), 2)
        self.assertEqual(c['observations']['whole_trial_restarts'], 0)
        self.assertIn('no grader feedback', c['limits']['feedback_policy'])
        self.assertIsNone(a['human_active_time']['minutes'])
        self.assertEqual(a['human_active_time']['method'], 'unavailable')
        self.assertNotIn('observation_window', a['human_active_time'])
        self.assertIsNone(a['delivery']['human_takeover'])
        self.assertIsNone(a['interruptions'])
        self.assertIsNone(a['event_summary']['metrics']['retries'])
        self.assertTrue(a['sources'])

    def test_started_command_without_terminal_result_is_not_counted_as_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'rpc.jsonl'
            started = item(item_id='unfinished')
            started['method'] = 'item/started'
            started['params']['item']['status'] = 'inProgress'
            started['params']['item']['exitCode'] = None
            path.write_text(''.join(json.dumps({'response': event}) + '\n'
                                    for event in [started, completed()]))
            result = summarize_events([path], thread_id='root', turn_ids=['first'])
        self.assertEqual(result['metrics']['commands_completed'], 0)
        self.assertEqual(result['metrics']['command_outcomes_unknown'], 1)
        self.assertEqual(result['coverage'], 'partial')


if __name__ == '__main__':
    unittest.main()
