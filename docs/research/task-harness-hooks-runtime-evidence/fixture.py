"""Run a complete synthetic hook fixture in a disposable directory, without a model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    handler = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[3] / 'packaging/codex/hooks/task_harness.py')
    with tempfile.TemporaryDirectory(prefix='task-hook-fixture-') as temporary:
        root = Path(temporary).resolve()
        (root / 'contracts').mkdir()
        config = {
            'schema_version': 1, 'project_root': str(root),
            'contract_dir': 'contracts', 'receipt_dir': 'receipts',
            # Synthetic assertions exercise the CLI; they are not host evidence.
            'host': {'session_identity': True, 'user_turn_identity': True,
                     'stop_continuation': True},
        }
        contract = {
            'schema_version': 1, 'task_id': 'fixture-parser-fix',
            'project_root': str(root), 'owner_session_id': 'fixture-session',
            'status': 'in_progress', 'objective': 'Fix parser and verify integration',
            'scope': ['Parser and relevant verification'],
            'requirements': [
                {'id': 'T1', 'outcome': 'Parser handles empty input', 'status': 'done',
                 'depends_on': [], 'evidence': ['synthetic:unit-check']},
                {'id': 'T2', 'outcome': 'Integration verified', 'status': 'pending',
                 'depends_on': ['T1'], 'evidence': []},
            ],
            'authorization': {'user_turn_id': 'fixture-user-turn', 'mode': 'execute',
                              'basis': 'Synthetic offline fixture only'},
            'recovery': {'next_action': 'Verify integration', 'blockers': [],
                         'unknown_operations': [], 'cancellation_reason': ''},
        }
        config_path = root / 'harness-project.json'
        config_path.write_text(json.dumps(config), encoding='utf-8')
        contract_path = root / 'contracts/fixture.md'
        contract_path.write_text('<!-- task-harness-contract:v1 -->\n```json\n'
                                 + json.dumps(contract) + '\n```\n<!-- /task-harness-contract -->\n',
                                 encoding='utf-8')
        before = contract_path.read_bytes()
        outputs = []
        for name in ('SessionStart', 'UserPromptSubmit', 'Stop', 'Stop'):
            event = {'hook_event_name': name, 'cwd': str(root),
                     'session_id': 'fixture-session', 'turn_id': 'fixture-user-turn',
                     'stop_hook_active': False}
            result = subprocess.run([sys.executable, '-B', str(handler), '--project-config', str(config_path)],
                                    input=json.dumps(event), text=True, capture_output=True, timeout=10, check=True)
            assert not result.stderr, result.stderr
            outputs.append(json.loads(result.stdout))
        assert 'hookSpecificOutput' in outputs[0]
        assert 'hookSpecificOutput' in outputs[1]
        assert outputs[2]['decision'] == 'block'
        assert outputs[3] == {}
        assert before == contract_path.read_bytes()
        receipts = list((root / 'receipts').glob('*.json'))
        assert len(receipts) == 1
        print(json.dumps({'outputs': outputs, 'receipt': json.loads(receipts[0].read_text()),
                          'contract_unchanged': True, 'evidence_kind': 'synthetic-cli-only'},
                         ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
