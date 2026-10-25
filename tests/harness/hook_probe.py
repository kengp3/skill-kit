"""Development-only C0 hook probe; never a product handler or model runner.

One explicit evidence directory is one probe attempt. Observations do not
establish host qualification, and this command never changes a task contract.
"""
import argparse
import json
import os
from pathlib import Path
import sys

FIELDS = ('hook_event_name', 'session_id', 'turn_id', 'stop_hook_active')
CANARY = ('C0 probe only: reply exactly C0_PROBE_CONTINUATION_CONFIRMED, then finish. '
          'Do not run tools, modify files or perform product work.')
EVENT_LIMIT = 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_links(path):
    for component in (*reversed(path.parents), path):
        require(not component.is_symlink(), 'symlink paths are not allowed')


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON keys')
        result[key] = value
    return result


def validate_scope(root, directory, event):
    require(root.is_absolute() and directory.is_absolute(), 'explicit absolute test paths are required')
    require(root == root.resolve() and root.is_dir(), 'test root must be an existing canonical directory')
    require(directory != root and directory.is_relative_to(root) and '..' not in directory.parts,
            'evidence directory must be strictly inside the test root')
    no_links(root)
    no_links(directory)
    require(not directory.exists() or directory.is_dir(), 'evidence path must be a directory')
    cwd = event.get('cwd')
    require(isinstance(cwd, str), 'event cwd is required')
    cwd = Path(cwd)
    require(cwd.is_absolute() and cwd.is_relative_to(root) and '..' not in cwd.parts,
            'event cwd is outside the explicit test root')
    no_links(cwd)
    require(cwd.is_dir(), 'event cwd must be an existing test directory')


def validate_event(event):
    require(isinstance(event, dict), 'event must be a JSON object')
    require(event.get('hook_event_name') in ('SessionStart', 'UserPromptSubmit', 'Stop'),
            'unsupported or missing event name')
    for key in ('session_id', 'turn_id'):
        value = event.get(key)
        require(value is None or (isinstance(value, str) and len(value) <= 4096),
                'native identity fields must be bounded strings or null')
    flag = event.get('stop_hook_active')
    require(flag is None or type(flag) is bool, 'stop_hook_active must be boolean or null')


def reserve_continuation(directory, event):
    path = directory / 'continuation.json'
    try:
        stream = path.open('x', encoding='utf-8')
    except FileExistsError:
        no_links(path)
        require(path.is_file(), 'existing receipt is not a regular file')
        return False
    with stream:
        json.dump({key: event[key] for key in FIELDS if key in event}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    return True


def record_event(directory, event):
    for sequence in range(1, 257):
        path = directory / f'event-{sequence:04d}.json'
        try:
            stream = path.open('x', encoding='utf-8')
        except FileExistsError:
            no_links(path)
            require(path.is_file(), 'existing observation is not a regular file')
            continue
        with stream:
            record = {'sequence': sequence, **{key: event[key] for key in FIELDS if key in event}}
            json.dump(record, stream)
            stream.flush()
            os.fsync(stream.fileno())
        return
    raise ValueError('probe event limit reached')


def probe(root, directory, event):
    validate_event(event)
    validate_scope(root, directory, event)
    directory.mkdir(parents=True, exist_ok=True)
    no_links(directory)
    is_stop = event['hook_event_name'] == 'Stop'
    eligible = (is_stop and event.get('stop_hook_active') is False
                and isinstance(event.get('session_id'), str) and bool(event['session_id'].strip()))
    # Reserve before recording: a failed/uncertain save consumes this attempt,
    # so a later native turn cannot retry a potentially emitted continuation.
    request_canary = eligible and reserve_continuation(directory, event)
    record_event(directory, event)
    if is_stop and (not isinstance(event.get('session_id'), str) or not event['session_id'].strip()
                    or type(event.get('stop_hook_active')) is not bool):
        raise ValueError('native Stop session or continuation flag is unavailable; observation only')
    return {'decision': 'block', 'reason': CANARY} if request_canary else {}


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        # Exit 2 may request continuation on a host; configuration errors must not.
        raise ValueError('required CLI arguments are missing or invalid')


def main():
    try:
        parser = Arguments(description=__doc__)
        parser.add_argument('--test-root', type=Path, required=True)
        parser.add_argument('--evidence-dir', type=Path, required=True)
        args = parser.parse_args()
        raw = sys.stdin.buffer.read(EVENT_LIMIT + 1)
        require(len(raw) <= EVENT_LIMIT, 'event exceeds 1 MiB limit')
        event = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_keys,
                           parse_constant=lambda _: require(False, 'invalid JSON constant'))
        output = probe(args.test_root, args.evidence_dir, event)
    except (OSError, UnicodeError, RecursionError):
        output = {'systemMessage': 'C0 probe not ready: input or test evidence unavailable; no continuation requested.'}
    except ValueError as error:
        output = {'systemMessage': 'C0 probe not ready: ' + str(error)[:180]}
    print(json.dumps(output))


if __name__ == '__main__':
    main()
