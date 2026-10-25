"""Read-only independent evidence checks; no native server or model is started."""
import argparse, copy, hashlib, json
from pathlib import Path

OUT = Path(__file__).resolve().parent
CASE = Path('/private/tmp/g03-persisted-trust-case')


def correlate(rows, messages, expected, identity):
    hooks = []
    for number, row in enumerate(rows, 1):
        message = row['message']
        if message.get('method') != 'hook/completed':
            continue
        params = message['params']; run = params['run']
        assert params['threadId'] == identity['thread_id'] and params['turnId'] == identity['turn_id']
        assert run['sourcePath'] == str(CASE/'.codex/hooks.json') and run['status'] == 'completed'
        hooks.append({'rpc_line': number, 'event': run['eventName'], 'display_order': run['displayOrder'], 'entries': run['entries']})
    assert sorted(x['display_order'] for x in hooks) == [0, 1, 2, 4]
    for order, text in expected.items():
        assert any(x['display_order'] == order and x['entries'] == [{'kind': 'context', 'text': text}] for x in hooks)
        assert text in messages, 'hook output absent from actual developer message'
    assert next(x for x in hooks if x['display_order'] == 4)['entries'] == []
    return hooks


def verify(self_check=False):
    original = json.loads((OUT/'hooks-before.json').read_text())['data'][0]['hooks']
    expected = {h['displayOrder']: h['command'][5:] for h in original if h['displayOrder'] in (0, 1, 2)}
    result = []
    for index in (1, 2):
        folder = OUT/f'invocation-{index}'
        identity = json.loads((folder/'invocation.json').read_text())
        rows = [json.loads(line) for line in (folder/'rpc.jsonl').read_text().splitlines()]
        session = next(folder.glob('*.excerpt.jsonl'))
        excerpts = [json.loads(line) for line in session.read_text().splitlines()]
        source_index = json.loads((folder/'session-excerpt-index.json').read_text())
        source = Path(source_index['private_original']).read_bytes()
        assert hashlib.sha256(source).hexdigest() == source_index['original_sha256']
        source_lines = source.splitlines(keepends=True)
        assert session.read_bytes() == b''.join(source_lines[n-1] for n in source_index['exact_retained_source_lines'])
        assert all(json.loads(source_lines[x['line']-1])['type'] == 'session_meta' for x in source_index['omitted'])
        messages = []; message_lines = []
        for number, line in enumerate(source_lines, 1):
            event = json.loads(line); payload = event.get('payload', {})
            if event.get('type') == 'response_item' and payload.get('type') == 'message' and payload.get('role') == 'developer':
                for content in payload.get('content', []):
                    if content.get('text') in expected.values():
                        messages.append(content['text']); message_lines.append(number)
        hooks = correlate(rows, messages, expected, identity)
        contexts = [x['payload'] for x in excerpts if x.get('type') == 'turn_context']
        assert len(contexts) == 1 and contexts[0]['model'] == 'gpt-6.1-sol' and contexts[0]['effort'] == 'low'
        terminals = [r['message']['params']['turn'] for r in rows if r['message'].get('method') == 'turn/completed']
        assert len(terminals) == 1 and terminals[0]['id'] == identity['turn_id'] and terminals[0]['status'] == 'completed'
        tools = [x['payload'] for x in excerpts if x.get('type') == 'response_item' and x['payload'].get('type') == 'custom_tool_call']
        assert all(x['name'] == 'exec' and 'tools.exec_command' in x.get('input', '') for x in tools)
        assert not any('tools.spawn_agent' in x.get('input', '') or 'python3 ' in x.get('input', '') or 'node ' in x.get('input', '') for x in tools)
        stderr = (folder/'server.stderr.log').read_text()
        result.append({'invocation': index, 'identity': identity, 'hook_completed': hooks, 'actual_developer_source_lines': message_lines, 'actual_model': contexts[0]['model'], 'actual_effort': contexts[0]['effort'], 'custom_tool_calls': len(tools), 'stderr_retry_429_lines': [line for line in stderr.splitlines() if '429' in line or 'retry' in line.lower() or 'reconnect' in line.lower()], 'stderr_bytes': len(stderr.encode()), 'excerpt_matches_private_full_source': True})
        if self_check:
            for mutated_rows, mutated_messages in ((rows, []), (copy.deepcopy(rows), messages)):
                if mutated_messages:
                    next(r['message']['params']['run'] for r in mutated_rows if r['message'].get('method') == 'hook/completed')['status'] = 'failed'
                try:
                    correlate(mutated_rows, mutated_messages, expected, identity)
                except AssertionError:
                    pass
                else:
                    raise AssertionError('negative control was accepted')
    return {'verdict': 'pass', 'invocations': result, 'self_check_missing_developer_and_failed_hook_rejected': self_check}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--self-check', action='store_true'); args = parser.parse_args()
    print(json.dumps(verify(args.self_check), ensure_ascii=False, indent=2))
