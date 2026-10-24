"""Exercise hooks through their public event CLI, never the implementation."""
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'packaging/codex/hooks/task_harness.py'


class HookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'project'
        self.root.mkdir()
        self.contracts = self.root / 'contracts'
        self.contracts.mkdir()
        self.config_path = self.root / 'harness-project.json'
        self.config = {
            'schema_version': 1, 'project_root': str(self.root),
            'contract_dir': 'contracts', 'receipt_dir': 'receipts',
            'host': {'session_identity': True, 'user_turn_identity': True,
                     'stop_continuation': True},
        }
        self.contract = {
            'schema_version': 1, 'task_id': 'fix-parser',
            'project_root': str(self.root), 'owner_session_id': 'session-1',
            'status': 'in_progress', 'objective': 'Fix parser and verify integration',
            'scope': ['parser and checks'],
            'requirements': [
                {'id': 'T1', 'outcome': 'Fix parser', 'status': 'done',
                 'depends_on': [], 'evidence': ['native:check-1']},
                {'id': 'T2', 'outcome': 'Verify integration', 'status': 'pending',
                 'depends_on': ['T1'], 'evidence': []},
            ],
            'authorization': {'user_turn_id': 'turn-1', 'mode': 'execute',
                              'basis': 'User requested the complete fix'},
            'recovery': {'next_action': 'Run integration check', 'blockers': [],
                         'unknown_operations': [], 'cancellation_reason': ''},
        }
        self.contract_path = self.contracts / 'fix-parser.md'
        self.save()

    def save(self):
        self.config_path.write_text(json.dumps(self.config), encoding='utf-8')
        self.contract_path.write_text(
            '# Task\n\n<!-- task-harness-contract:v1 -->\n```json\n'
            + json.dumps(self.contract) + '\n```\n<!-- /task-harness-contract -->\n',
            encoding='utf-8')

    def event(self, name='Stop', **changes):
        result = {'hook_event_name': name, 'session_id': 'session-1',
                  'cwd': str(self.root), 'turn_id': 'turn-1',
                  'stop_hook_active': False}
        result.update(changes)
        return result

    def run_event(self, event=None, explicit=False, raw=None):
        command = [sys.executable, '-B', str(SCRIPT)]
        if explicit:
            command.extend(['--project-config', str(self.config_path)])
        result = subprocess.run(command, input=raw if raw is not None else json.dumps(event or self.event()),
                                text=True, capture_output=True, cwd=self.root, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return json.loads(result.stdout)

    def test_session_start_recovers_contract_without_mutation(self):
        before = self.contract_path.read_bytes()
        result = self.run_event(self.event('SessionStart', source='resume'))
        context = result['hookSpecificOutput']['additionalContext']
        self.assertEqual(result['hookSpecificOutput']['hookEventName'], 'SessionStart')
        self.assertIn(str(self.contract_path), context)
        self.assertIn('fix-parser', context)
        self.assertIn('session-1', context)
        self.assertEqual(self.contract_path.read_bytes(), before)
        self.assertFalse((self.root / 'receipts').exists())

    def test_stop_requests_once_and_preserves_contract(self):
        before = self.contract_path.read_bytes()
        first = self.run_event()
        self.assertEqual(first['decision'], 'block')
        self.assertIn('T2', first['reason'])
        receipt_paths = list((self.root / 'receipts').glob('*.json'))
        self.assertEqual(len(receipt_paths), 1)
        receipt = json.loads(receipt_paths[0].read_text())
        self.assertEqual(receipt['session_id'], 'session-1')
        self.assertEqual(receipt['user_turn_id'], 'turn-1')
        self.assertEqual(receipt['task_id'], 'fix-parser')
        self.assertNotIn('decision', self.run_event())
        self.assertEqual(self.contract_path.read_bytes(), before)
        self.assertEqual(len(list((self.root / 'receipts').glob('*.json'))), 1)

    def test_new_prompt_does_not_reset_budget_and_stale_authorization_is_rejected(self):
        self.assertEqual(self.run_event()['decision'], 'block')
        result = self.run_event(self.event('UserPromptSubmit', turn_id='turn-2', prompt='Discuss only'))
        context = result['hookSpecificOutput']['additionalContext']
        self.assertIn('turn-2', context)
        self.assertIn('latest user', context)
        self.assertNotIn('decision', self.run_event())
        stale = self.run_event(self.event(turn_id='turn-2'))
        self.assertNotIn('decision', stale)
        self.assertIn('not ready', stale['systemMessage'])

    def test_task_switch_does_not_reset_same_user_turn_budget(self):
        self.assertEqual(self.run_event()['decision'], 'block')
        self.contract['task_id'] = 'another-task'
        self.save()
        self.assertNotIn('decision', self.run_event())

    def test_stop_respects_modes_terminal_and_blocked_states(self):
        for mode in ('discuss', 'wait', 'stop'):
            with self.subTest(mode=mode):
                self.contract['authorization']['mode'] = mode
                self.save()
                self.assertNotIn('decision', self.run_event())
        self.contract['authorization']['mode'] = 'execute'
        for status in ('blocked', 'cancelled'):
            with self.subTest(status=status):
                self.contract['status'] = status
                self.contract['recovery']['blockers'] = ['User input required']
                self.contract['recovery']['cancellation_reason'] = 'User cancelled'
                self.save()
                self.assertNotIn('decision', self.run_event())
        self.assertFalse((self.root / 'receipts').exists())

    def test_existing_native_continuation_never_requests_again(self):
        self.assertEqual(self.run_event(self.event(stop_hook_active=True)), {})
        self.assertFalse((self.root / 'receipts').exists())

    def test_unqualified_host_reports_gap_and_never_requests_continuation(self):
        self.config['host']['user_turn_identity'] = False
        self.save()
        result = self.run_event()
        self.assertIn('not ready', result['systemMessage'])
        self.assertNotIn('decision', result)
        self.assertFalse((self.root / 'receipts').exists())

    def test_partial_capabilities_keep_context_and_report_overall_gap(self):
        self.config['host']['stop_continuation'] = False
        self.save()
        for name in ('SessionStart', 'UserPromptSubmit'):
            with self.subTest(name=name):
                result = self.run_event(self.event(name))
                self.assertIn('hookSpecificOutput', result)
                self.assertIn('not ready', result.get('systemMessage', ''))
                self.assertNotIn('decision', result)
        self.assert_gap()
        self.config['host']['user_turn_identity'] = False
        self.save()
        result = self.run_event(self.event('SessionStart'))
        self.assertIn('hookSpecificOutput', result)
        self.assertIn('not ready', result['systemMessage'])
        result = self.assert_gap(event=self.event('UserPromptSubmit'))
        self.assertNotIn('hookSpecificOutput', result)
        self.assertFalse((self.root / 'receipts').exists())

    def assert_gap(self, **kwargs):
        result = self.run_event(**kwargs)
        self.assertIn('not ready', result.get('systemMessage', ''))
        self.assertNotIn('decision', result)
        return result

    def test_contract_schema_and_dependencies_are_not_guessed(self):
        original = copy.deepcopy(self.contract)
        mutations = [
            lambda c: c.pop('authorization'),
            lambda c: c.update(schema_version=True),
            lambda c: c.update(status='verifying'),
            lambda c: c.update(owner_session_id=[]),
            lambda c: c.update(scope='not a list'),
            lambda c: c['authorization'].update(mode='anything'),
            lambda c: c['authorization'].update(user_turn_id=''),
            lambda c: c['requirements'][1].update(id='T1'),
            lambda c: c['requirements'][1].update(depends_on=['missing']),
            lambda c: c['requirements'][0].update(depends_on=['T1']),
            lambda c: c['requirements'][0].update(depends_on=['T2']),
            lambda c: c['requirements'][0].update(evidence=[42]),
            lambda c: c['requirements'][0].update(status='cancelled'),
            lambda c: c['recovery'].update(unknown_operations='not a list'),
            lambda c: c.update(status='blocked'),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                self.contract = copy.deepcopy(original)
                mutate(self.contract)
                self.save()
                self.assert_gap()
        self.assertFalse((self.root / 'receipts').exists())

    def test_duplicate_json_keys_and_multiple_blocks_are_rejected(self):
        original = self.contract_path.read_text()
        duplicate = original.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')
        self.contract_path.write_text(duplicate)
        self.assert_gap()
        self.contract_path.write_text(original + original)
        self.assert_gap()
        self.contract_path.write_text(original.replace('```json', '```python'))
        self.assert_gap()

    def test_ambiguous_bindings_and_duplicate_task_ids_are_rejected(self):
        other = self.contracts / 'other.md'
        other.write_bytes(self.contract_path.read_bytes())
        self.assert_gap()
        other.write_text(other.read_text().replace('fix-parser', 'other-task'))
        self.assert_gap()
        # Historical terminal tasks may retain their owner without stealing a live binding.
        old = copy.deepcopy(self.contract)
        old['task_id'] = 'historical'
        old['status'] = 'done'
        for item in old['requirements']:
            item['status'] = 'done'
            item['evidence'] = ['native:historical']
        other.write_text('<!-- task-harness-contract:v1 -->\n```json\n' + json.dumps(old)
                         + '\n```\n<!-- /task-harness-contract -->')
        self.assertEqual(self.run_event()['decision'], 'block')

    def test_missing_bad_or_oversized_event_reports_gap(self):
        for raw in ('not json', '[]', '{}', '{"hook_event_name":"Stop","hook_event_name":"Stop"}',
                    ' ' * (1024 * 1024 + 1)):
            with self.subTest(length=len(raw)):
                self.assert_gap(raw=raw)
        for changes in ({'stop_hook_active': 'false'}, {'turn_id': ''}, {'cwd': 'relative'},
                        {'session_id': ''}, {'hook_event_name': 'Unexpected'}):
            with self.subTest(changes=changes):
                self.assert_gap(event=self.event(**changes))
        self.assertFalse((self.root / 'receipts').exists())

    def test_unmarked_docs_are_ignored_but_marked_contract_limits_are_enforced(self):
        (self.contracts / 'notes.md').write_text('Ordinary planning notes')
        self.assertIn('hookSpecificOutput', self.run_event(self.event('SessionStart')))
        self.contract_path.write_text('x' * (512 * 1024 + 1))
        self.assert_gap()
        self.save()
        for index in range(64):
            (self.contracts / f'extra-{index}.md').write_text('notes')
        self.assert_gap()

    def test_outside_root_and_symlink_paths_are_rejected(self):
        original = copy.deepcopy(self.config)
        for field, value in (('contract_dir', '..'), ('receipt_dir', '../escape'),
                             ('receipt_dir', 'contracts'), ('receipt_dir', 'contracts/receipts'),
                             ('contract_dir', '.'), ('project_root', str(self.root.parent))):
            with self.subTest(field=field, value=value):
                self.config = copy.deepcopy(original)
                self.config[field] = value
                self.save()
                self.assert_gap(explicit=True)
        self.config = original
        self.save()
        self.assert_gap(event=self.event(cwd=str(self.root.parent)), explicit=True)
        self.contract_path.rename(self.root / 'outside.md')
        self.contract_path.symlink_to(self.root / 'outside.md')
        self.assert_gap()
        self.contract_path.unlink()
        (self.root / 'receipts').symlink_to(self.root.parent, target_is_directory=True)
        self.save()
        self.assert_gap()

    def test_cwd_parent_components_cannot_escape_explicit_project(self):
        outside = self.root.parent / 'other'
        outside.mkdir()
        before = self.contract_path.read_bytes()
        self.assert_gap(event=self.event(cwd=str(self.root / '..' / 'other')), explicit=True)
        self.assertFalse((self.root / 'receipts').exists())
        self.assertEqual(self.contract_path.read_bytes(), before)
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == 'posix' and os.geteuid() != 0,
                         'unreadable directory requires non-root POSIX')
    def test_unreadable_contract_directory_reports_gap(self):
        before = self.contract_path.read_bytes()
        try:
            self.contracts.chmod(0o000)
            self.assert_gap()
        finally:
            self.contracts.chmod(0o700)
        self.assertFalse((self.root / 'receipts').exists())
        self.assertEqual(self.contract_path.read_bytes(), before)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO check requires POSIX')
    def test_special_file_is_rejected_without_waiting(self):
        self.contract_path.unlink()
        os.mkfifo(self.contract_path)
        self.assert_gap()

    def test_unknown_results_only_request_reconciliation(self):
        self.contract['recovery']['unknown_operations'] = ['upload response lost']
        self.save()
        result = self.run_event()
        self.assertEqual(result['decision'], 'block')
        self.assertIn('do not repeat product mutations', result['reason'])

    def test_done_requires_non_cancelled_accepted_outcomes(self):
        self.contract['status'] = 'done'
        self.save()
        self.assertEqual(self.run_event()['decision'], 'block')
        # A fresh user turn may diagnose a separate invalid closeout.
        self.contract['authorization']['user_turn_id'] = 'turn-2'
        for item in self.contract['requirements']:
            item['status'] = 'cancelled'
            item['cancellation_reason'] = 'Scope withdrawn'
        self.save()
        self.assertEqual(self.run_event(self.event(turn_id='turn-2'))['decision'], 'block')

    def test_done_with_accepted_outcomes_allows_closeout(self):
        self.contract['status'] = 'done'
        for item in self.contract['requirements']:
            item['status'] = 'done'
            item['evidence'] = ['native:accepted']
        self.save()
        self.assertEqual(self.run_event(), {})
        self.assertFalse((self.root / 'receipts').exists())

    def test_parallel_stop_and_lost_output_never_reissue(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.run_event(), range(8)))
        self.assertEqual(sum(result.get('decision') == 'block' for result in results), 1)
        self.assertEqual(len(list((self.root / 'receipts').glob('*.json'))), 1)
        # Losing the winning stdout does not permit a second continuation.
        self.assertEqual(self.run_event(), {})

    def test_unwritable_receipt_location_is_not_continuation(self):
        (self.root / 'receipts').write_text('occupied by a regular file')
        self.assert_gap()
        (self.root / 'receipts').unlink()
        (self.root / 'receipts').mkdir(mode=0o500)
        self.addCleanup(lambda: (self.root / 'receipts').chmod(0o700))
        if os.geteuid() != 0:
            self.assert_gap()

    def test_existing_incomplete_reservation_is_not_retried(self):
        directory = self.root / 'receipts'
        directory.mkdir()
        key = hashlib.sha256(json.dumps(['session-1', 'turn-1']).encode()).hexdigest()
        target = directory / (key + '.json')
        target.write_text('')
        self.assertEqual(self.run_event(), {})
        self.assertEqual(target.read_text(), '')
        target.unlink()
        target.symlink_to(self.contract_path)
        self.assert_gap()

    def test_configuration_and_discovery_do_not_activate_other_projects(self):
        self.assertEqual(self.run_event(self.event(session_id='other-session')), {})
        context = self.run_event(self.event('SessionStart', session_id='other-session'))
        self.assertIn('Only bind or take over after explicit', context['hookSpecificOutput']['additionalContext'])
        nested = self.root / 'subproject'
        nested.mkdir()
        self.assertIn('hookSpecificOutput', self.run_event(self.event('SessionStart', cwd=str(nested))))
        (nested / '.git').write_text('gitdir: irrelevant-for-boundary')
        self.assertEqual(self.run_event(self.event(cwd=str(nested))), {})
        self.config_path.unlink()
        self.assertEqual(self.run_event(), {})
        self.assertFalse((self.root / 'receipts').exists())

    def test_host_flag_types_missing_event_fields_and_done_unknown_fail_safely(self):
        self.config['host']['user_turn_identity'] = 'true'
        self.save()
        self.assert_gap()
        self.config['host']['user_turn_identity'] = True
        self.config['schema_version'] = True
        self.save()
        self.assert_gap()
        self.config['schema_version'] = 1
        self.save()
        event = self.event()
        del event['stop_hook_active']
        self.assert_gap(event=event)
        self.contract['status'] = 'done'
        for item in self.contract['requirements']:
            item.update(status='done', evidence=['native:checked'])
        self.contract['recovery']['unknown_operations'] = ['unconfirmed external operation']
        self.save()
        result = self.run_event()
        self.assertEqual(result['decision'], 'block')
        self.assertIn('do not repeat product mutations', result['reason'])

    def test_invalid_cli_argument_is_visible_without_exit_two(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--project-config'],
                                input=json.dumps(self.event()), text=True, capture_output=True,
                                cwd=self.root, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, '')
        self.assertIn('not ready', json.loads(result.stdout)['systemMessage'])


if __name__ == '__main__':
    unittest.main()
