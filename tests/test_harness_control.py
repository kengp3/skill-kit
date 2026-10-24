"""Control contracts exercised with native events, without a model trial."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness.control import TrialControl

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/research/codex-coding-harness-implementation-evidence'
ROOT_THREAD = '01a16c4c-7553-7fa2-a343-82de75b28593'
INITIAL_TURN = '01a16c4c-7583-7040-9bcb-822eb1360c75'
CONTINUED_TURN = '01a16c52-0e8b-7d32-b02f-8c101c0e71c4'


def responses(relative):
    for line in (EVIDENCE / relative).read_text().splitlines():
        record = json.loads(line)
        if 'response' in record:
            yield record['response']


class ControlTest(unittest.TestCase):
    def test_recorded_child_completion_does_not_finish_root(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        child_terminals = 0
        for event in responses('cli-smoke-C/rpc.jsonl'):
            child_terminals += event.get('method') == 'turn/completed'
            control.observe(event)
        self.assertEqual(child_terminals, 1)
        self.assertEqual(control.outcome, 'running')

    def test_invalid_identity_and_clock_cannot_start_or_rebind_trial(self):
        for args in ({'started_at': float('nan'), 'wall_seconds': 900},
                     {'started_at': 100, 'wall_seconds': 0},
                     {'started_at': True, 'wall_seconds': 900}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                TrialControl(**args)
        control = TrialControl(started_at=100, wall_seconds=900)
        with self.assertRaises(ValueError):
            control.bind('', INITIAL_TURN)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        with self.assertRaises(ValueError):
            control.bind(ROOT_THREAD, CONTINUED_TURN)

    def test_recorded_interruption_requires_reconciliation_and_stopped_writers(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        control.disconnected()
        self.assertEqual(control.outcome, 'unknown')
        with self.assertRaises(ValueError):
            control.resume(CONTINUED_TURN, now=467)
        readback = json.loads((EVIDENCE /
            'cli-smoke-C/interrupted-root-readback.json').read_text())
        self.assertTrue(control.reconcile_readback(readback))
        self.assertEqual(control.outcome, 'interrupted')
        with self.assertRaises(ValueError):
            control.resume(CONTINUED_TURN, now=467)
        control.confirm_writers_stopped(False)
        with self.assertRaises(ValueError):
            control.resume(CONTINUED_TURN, now=467)
        control.confirm_writers_stopped(True)
        control.resume(CONTINUED_TURN, now=467)
        self.assertEqual(control.deadline, 1000)
        self.assertEqual(control.remaining(now=467), 533)
        self.assertIsNone(control.writers_stopped)
        for event in responses('cli-smoke-C-continuation-1/rpc.jsonl'):
            control.observe(event)
        self.assertEqual(control.outcome, 'completed')
        self.assertIsNone(control.writers_stopped)
        control.disconnected()
        self.assertEqual(control.outcome, 'completed')
        control.confirm_writers_stopped(True)
        with self.assertRaises(ValueError):
            control.resume('third-turn', now=800)

    def test_early_completion_survives_binding_and_malformed_events_are_ignored(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        for event in responses('cli-smoke-C-continuation-1/rpc.jsonl'):
            control.observe(event)
        control.bind(ROOT_THREAD, CONTINUED_TURN)
        self.assertEqual(control.outcome, 'completed')
        malformed = [None, [], {}, {'method': 'turn/completed', 'params': None},
                     {'method': 'turn/completed', 'params': {'turn': []}},
                     {'method': 'turn/completed', 'params': {
                         'threadId': ROOT_THREAD,
                         'turn': {'id': CONTINUED_TURN, 'status': 'inProgress'}}}]
        for event in malformed:
            control.observe(event)
        self.assertEqual(control.outcome, 'completed')
        self.assertIsNone(control.writers_stopped)

    def test_cancel_is_not_proof_of_stopping_or_permission_to_resume(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        control.request_cancel()
        self.assertEqual(control.outcome, 'unknown')
        control.confirm_writers_stopped(True)
        with self.assertRaises(ValueError):
            control.resume(CONTINUED_TURN, now=200, allow_after_cancel=True)
        readback = {'thread': {'id': ROOT_THREAD},
                    'turns': [{'id': INITIAL_TURN, 'status': 'interrupted'}]}
        self.assertTrue(control.reconcile_readback(readback))
        with self.assertRaises(ValueError):
            control.resume(CONTINUED_TURN, now=200)
        control.confirm_writers_stopped(True)
        control.resume(CONTINUED_TURN, now=200, allow_after_cancel=True)
        self.assertEqual(control.outcome, 'running')
        self.assertEqual(control.deadline, 1000)

    def test_native_readback_and_late_old_events_cannot_complete_continuation(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        readback = next(event['result'] for event in responses(
            'cli-smoke-C-continuation-1/rpc.jsonl')
            if isinstance(event.get('result'), dict)
            and isinstance(event['result'].get('thread'), dict))
        self.assertTrue(control.reconcile_readback(readback))
        control.confirm_writers_stopped(True)
        control.resume(CONTINUED_TURN, now=467)
        control.observe({'method': 'turn/completed', 'params': {
            'threadId': ROOT_THREAD,
            'turn': {'id': INITIAL_TURN, 'status': 'completed'}}})
        self.assertEqual(control.outcome, 'running')
        for status in ('failed', 'interrupted', 'completed'):
            terminal = TrialControl(started_at=100, wall_seconds=900)
            terminal.bind(ROOT_THREAD, INITIAL_TURN)
            terminal.observe({'method': 'turn/completed', 'params': {
                'threadId': ROOT_THREAD,
                'turn': {'id': INITIAL_TURN, 'status': status}}})
            self.assertEqual(terminal.outcome, status)
            self.assertIsNone(terminal.writers_stopped)

    def test_deadline_expiry_clock_reversal_and_reused_turn_are_rejected(self):
        readback = {'thread': {'id': ROOT_THREAD},
                    'turns': [{'id': INITIAL_TURN, 'status': 'interrupted'}]}
        for now in (99, float('nan'), float('inf'), 1000, 1001):
            with self.subTest(now=now):
                control = TrialControl(started_at=100, wall_seconds=900)
                control.bind(ROOT_THREAD, INITIAL_TURN)
                control.reconcile_readback(readback)
                control.confirm_writers_stopped(True)
                with self.assertRaises(ValueError):
                    control.resume(CONTINUED_TURN, now=now)
                self.assertEqual(control.turn_id, INITIAL_TURN)
                self.assertEqual(control.deadline, 1000)
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        control.reconcile_readback(readback)
        control.confirm_writers_stopped(True)
        control.resume(CONTINUED_TURN, now=400)
        control.reconcile_readback({'thread': {'id': ROOT_THREAD},
            'turns': [{'id': CONTINUED_TURN, 'status': 'interrupted'}]})
        control.confirm_writers_stopped(True)
        with self.assertRaises(ValueError):
            control.resume(INITIAL_TURN, now=500)
        with self.assertRaises(ValueError):
            control.remaining(now=399)

    def test_conflicting_terminal_events_require_readback_not_last_event_wins(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        for status in ('completed', 'interrupted'):
            control.observe({'method': 'turn/completed', 'params': {
                'threadId': ROOT_THREAD,
                'turn': {'id': INITIAL_TURN, 'status': status}}})
        self.assertEqual(control.outcome, 'unknown')
        control.confirm_writers_stopped(True)
        with self.assertRaises(ValueError):
            control.resume(CONTINUED_TURN, now=500)

    def test_new_observation_invalidates_old_liveness_and_readback_resolves_conflict(self):
        control = TrialControl(started_at=100, wall_seconds=900)
        control.bind(ROOT_THREAD, INITIAL_TURN)
        control.confirm_writers_stopped(True)
        control.disconnected()
        self.assertIsNone(control.writers_stopped)
        for status in ('completed', 'interrupted'):
            control.observe({'method': 'turn/completed', 'params': {
                'threadId': ROOT_THREAD,
                'turn': {'id': INITIAL_TURN, 'status': status}}})
        self.assertEqual(control.outcome, 'unknown')
        control.confirm_writers_stopped(True)
        readback = {'thread': {'id': ROOT_THREAD},
                    'turns': [{'id': INITIAL_TURN, 'status': 'interrupted'}]}
        self.assertTrue(control.reconcile_readback(readback))
        self.assertIsNone(control.writers_stopped)
        self.assertEqual(control.outcome, 'interrupted')
        control.observe({'method': 'turn/completed', 'params': {
            'threadId': ROOT_THREAD,
            'turn': {'id': INITIAL_TURN, 'status': 'interrupted'}}})
        self.assertEqual(control.outcome, 'interrupted')
        for bad in (None, {}, {'thread': {'id': 'wrong'}, 'turns': readback['turns']},
                    {'thread': {'id': ROOT_THREAD}, 'turns': readback['turns'] * 2}):
            self.assertFalse(control.reconcile_readback(bad))
            self.assertEqual(control.outcome, 'interrupted')


if __name__ == '__main__':
    unittest.main()
