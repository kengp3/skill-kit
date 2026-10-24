"""Codex task-contract hooks. Python 3.10+, standard library only.

Contracts remain agent-owned. Receipts only reserve one continuation request;
they never record authoritative progress, authorization or execution results.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

START = '<!-- task-harness-contract:v1 -->'
END = '<!-- /task-harness-contract -->'
STATES = {'pending', 'in_progress', 'blocked', 'done', 'cancelled'}
HOST_KEYS = ('session_identity', 'user_turn_identity', 'stop_continuation')
EVENT_LIMIT = 1024 * 1024
CONTRACT_LIMIT = 512 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, label, empty=False):
    require(isinstance(value, str) and (empty or bool(value.strip())), label + ' must be text')


def strings(value, label):
    require(isinstance(value, list), label + ' must be a list')
    for item in value:
        text(item, label + ' item')


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def parse_json(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: require(False, 'invalid JSON constant'))


def no_links(path):
    for part in (*reversed(path.parents), path):
        require(not part.is_symlink(), 'symlink paths are not supported')


def read_regular(path, limit):
    no_links(path)
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, 'rb') as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'expected a regular file')
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, 'file exceeds read limit')
    return raw.decode('utf-8')


def validate_event(event):
    require(isinstance(event, dict), 'event must be an object')
    require(event.get('hook_event_name') in ('SessionStart', 'UserPromptSubmit', 'Stop'),
            'unsupported or missing event name')
    text(event.get('session_id'), 'session_id')
    text(event.get('cwd'), 'cwd')
    require(Path(event['cwd']).is_absolute(), 'cwd must be absolute')
    if event['hook_event_name'] != 'SessionStart':
        text(event.get('turn_id'), 'turn_id')
    if event['hook_event_name'] == 'Stop':
        require(type(event.get('stop_hook_active')) is bool, 'stop_hook_active must be boolean')


def load_config(event, config_path):
    cwd = Path(event['cwd'])
    no_links(cwd)
    require(cwd.is_dir(), 'cwd must be an existing directory')
    cwd = cwd.resolve(strict=True)
    if config_path is None:
        for directory in (cwd, *cwd.parents):
            candidate = directory / 'harness-project.json'
            if os.path.lexists(candidate):
                config_path = candidate
                break
            if os.path.lexists(directory / '.git'):
                break
    if config_path is None:
        return None
    config_path = config_path.absolute()
    config = parse_json(read_regular(config_path, EVENT_LIMIT))
    require(isinstance(config, dict), 'project configuration must be an object')
    require(type(config.get('schema_version')) is int and config['schema_version'] == 1,
            'unsupported project schema_version')
    text(config.get('project_root'), 'project_root')
    root = Path(config['project_root'])
    require(root.is_absolute() and root == root.resolve() and root == config_path.parent,
            'project_root must be the actual configuration directory')
    require(cwd.is_relative_to(root), 'event cwd is outside configured project')
    paths = []
    for key in ('contract_dir', 'receipt_dir'):
        text(config.get(key), key)
        relative = Path(config[key])
        require(not relative.is_absolute() and '..' not in relative.parts,
                key + ' must remain project-relative')
        path = root / relative
        require(path != root, key + ' must not be project root')
        no_links(path)
        require(not path.exists() or path.is_dir(), key + ' must be a directory')
        paths.append(path)
    require(not paths[0].is_relative_to(paths[1]) and not paths[1].is_relative_to(paths[0]),
            'contract and receipt directories must not contain each other')
    require(paths[0].is_dir(), 'contract directory is unavailable')
    host = config.get('host')
    require(isinstance(host, dict) and all(type(host.get(key)) is bool for key in HOST_KEYS),
            'host qualification flags must be booleans')
    return config


def validate_contract(contract, root):
    require(isinstance(contract, dict), 'contract must be an object')
    require(type(contract.get('schema_version')) is int and contract['schema_version'] == 1,
            'unsupported contract schema_version')
    for field in ('task_id', 'project_root', 'objective'):
        text(contract.get(field), field)
    require(contract['project_root'] == root, 'contract belongs to another project')
    require('owner_session_id' in contract, 'missing owner_session_id')
    if contract['owner_session_id'] is not None:
        text(contract['owner_session_id'], 'owner_session_id')
    require(contract.get('status') in STATES, 'invalid task status')
    strings(contract.get('scope'), 'scope')
    require(bool(contract['scope']), 'scope must not be empty')
    requirements = contract.get('requirements')
    require(isinstance(requirements, list) and bool(requirements), 'requirements must be nonempty')
    dependencies = {}
    for item in requirements:
        require(isinstance(item, dict), 'requirement must be an object')
        for field in ('id', 'outcome'):
            text(item.get(field), 'requirement ' + field)
        require(item['id'] not in dependencies, 'duplicate requirement id')
        require(item.get('status') in STATES, 'invalid requirement status')
        strings(item.get('depends_on'), 'depends_on')
        strings(item.get('evidence'), 'evidence')
        require(len(item['depends_on']) == len(set(item['depends_on'])), 'duplicate dependency')
        if item['status'] == 'cancelled':
            text(item.get('cancellation_reason'), 'cancelled requirement basis')
        dependencies[item['id']] = set(item['depends_on'])
    require(all(values <= dependencies.keys() and key not in values
                for key, values in dependencies.items()), 'missing or self dependency')
    remaining = dict(dependencies)
    while remaining:
        ready = {key for key, values in remaining.items() if not values.intersection(remaining)}
        require(bool(ready), 'dependency cycle')
        remaining = {key: values for key, values in remaining.items() if key not in ready}
    authorization = contract.get('authorization')
    require(isinstance(authorization, dict), 'missing authorization')
    text(authorization.get('user_turn_id'), 'authorization user_turn_id')
    text(authorization.get('basis'), 'authorization basis')
    require(authorization.get('mode') in ('execute', 'discuss', 'wait', 'stop'), 'invalid authorization mode')
    recovery = contract.get('recovery')
    require(isinstance(recovery, dict), 'missing recovery')
    for field in ('next_action', 'cancellation_reason'):
        text(recovery.get(field), field, empty=True)
    for field in ('blockers', 'unknown_operations'):
        strings(recovery.get(field), field)
    if contract['status'] == 'blocked':
        require(bool(recovery['blockers']) and bool(recovery['next_action'].strip()),
                'blocked task needs blockers and next_action')
    if contract['status'] == 'cancelled':
        text(recovery['cancellation_reason'], 'cancellation basis')


def find_contracts(config):
    directory = Path(config['project_root']) / config['contract_dir']
    paths = sorted(path for path in directory.iterdir() if path.name.endswith('.md'))
    require(len(paths) <= 64, 'contract scan exceeds 64 Markdown files')
    contracts, task_ids, owners = [], set(), set()
    for path in paths:
        raw = read_regular(path, CONTRACT_LIMIT)
        if START not in raw and END not in raw:
            continue
        require(raw.count(START) == 1 and raw.count(END) == 1, 'expected one contract block')
        start, end = raw.index(START) + len(START), raw.index(END)
        require(start < end, 'invalid contract marker order')
        block = raw[start:end].strip()
        require(block.startswith('```json\n') and block.endswith('\n```') and block.count('```') == 2,
                'expected one json fenced contract block')
        contract = parse_json(block[len('```json\n'):-len('\n```')])
        validate_contract(contract, config['project_root'])
        require(contract['task_id'] not in task_ids, 'duplicate task_id')
        task_ids.add(contract['task_id'])
        owner = contract['owner_session_id']
        if owner is not None and contract['status'] not in ('done', 'cancelled'):
            require(owner not in owners, 'multiple active contracts bound to one session')
            owners.add(owner)
        contracts.append((path, contract, hashlib.sha256(raw.encode('utf-8')).hexdigest()))
    return contracts


def select_contract(contracts, event):
    matches = [entry for entry in contracts if entry[1]['owner_session_id'] == event['session_id']]
    active = [entry for entry in matches if entry[1]['status'] not in ('done', 'cancelled')]
    if active:
        return active[0]
    # Historical terminal contracts do not steal a live binding. A terminal
    # contract for this exact user turn can still have an invalid done claim.
    current = [entry for entry in matches
               if entry[1]['authorization']['user_turn_id'] == event.get('turn_id')]
    require(len(current) <= 1, 'ambiguous terminal contracts for this user turn')
    return current[0] if current else None


def reserve_receipt(event, contract, fingerprint, directory):
    no_links(directory)
    directory.mkdir(parents=True, exist_ok=True)
    no_links(directory)
    key = json.dumps([event['session_id'], contract['authorization']['user_turn_id']])
    target = directory / (hashlib.sha256(key.encode()).hexdigest() + '.json')
    receipt = {'session_id': event['session_id'],
               'user_turn_id': contract['authorization']['user_turn_id'],
               'task_id': contract['task_id'], 'contract_sha256': fingerprint,
               'operation': 'request_closeout_reconciliation'}
    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    except FileExistsError:
        no_links(target)
        require(stat.S_ISREG(target.stat().st_mode), 'receipt is not a regular file')
        return False
    # A partial/empty reservation is deliberately retained after any failure.
    # Output loss or a crash must never grant a second intervention.
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    return True


def stop(event, config, contract, fingerprint):
    authorization = contract['authorization']
    require(event['turn_id'] == authorization['user_turn_id'],
            'current turn does not match the saved user authorization')
    if authorization['mode'] != 'execute' or contract['status'] in ('blocked', 'cancelled'):
        return {}
    missing = [item['id'] for item in contract['requirements']
               if item['status'] not in ('done', 'cancelled')
               or (item['status'] == 'done' and not item['evidence'])]
    accepted = any(item['status'] == 'done' for item in contract['requirements'])
    unknown = contract['recovery']['unknown_operations']
    if contract['status'] == 'done' and accepted and not missing and not unknown:
        return {}
    directory = Path(config['project_root']) / config['receipt_dir']
    if not reserve_receipt(event, contract, fingerprint, directory):
        return {}
    if unknown:
        instruction = 'Query actual results and reconcile unknown operations before any replay; do not repeat product mutations.'
    else:
        instruction = ('Reconcile necessary outcomes ' + ', '.join(missing)
                       + '; continue only authorized ready work, or save the concrete blocker. '
                       'All-cancelled outcomes do not prove successful completion.')
    return {'decision': 'block', 'reason': (
        'Task harness closeout reconciliation (same user work turn; no new authority or budget). '
        + instruction + ' Recheck the latest user request, acceptance evidence and saved contract. '
        'Respect user Stop and cancellation; do not weaken completion criteria.')}


def handle(event, config_path):
    validate_event(event)
    if event['hook_event_name'] == 'Stop' and event['stop_hook_active']:
        return {}
    config = load_config(event, config_path)
    if config is None:
        return {}
    required = HOST_KEYS if event['hook_event_name'] == 'Stop' else HOST_KEYS[:1]
    if event['hook_event_name'] == 'UserPromptSubmit':
        required = HOST_KEYS[:2]
    require(all(config['host'][key] for key in required),
            'required host identity/continuation qualification is unverified')
    selected = select_contract(find_contracts(config), event)
    readiness = {}
    if not all(config['host'][key] for key in HOST_KEYS):
        readiness['systemMessage'] = ('Task harness not ready: required host qualification is incomplete; '
                                      'available context does not establish full harness readiness.')
    if event['hook_event_name'] == 'SessionStart':
        context = f"Task harness session_id={event['session_id']}. "
        if selected:
            path, contract, _ = selected
            context += f"Contract {path}; task_id={contract['task_id']}. Reconcile current artifacts and authorization before resuming."
        else:
            context += 'No active task is bound. Only bind or take over after explicit task activation and reconciliation.'
        return {**readiness, 'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': context}}
    if event['hook_event_name'] == 'UserPromptSubmit':
        context = (f"Task harness session_id={event['session_id']}, turn_id={event['turn_id']}. "
                   'Reconcile the latest user request and save its effective authorization in the bound contract. '
                   'Do not infer authorization from old state; a hook continuation is not a new user request '
                   'and must not reset the original user_turn_id or intervention budget.')
        return {**readiness, 'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': context}}
    if selected:
        _, contract, fingerprint = selected
        return stop(event, config, contract, fingerprint)
    return {}


class HookArguments(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default exit 2 has hook-continuation semantics on hosts.
        raise ValueError(message)


def main():
    try:
        parser = HookArguments(description=__doc__)
        parser.add_argument('--project-config', type=Path)
        args = parser.parse_args()
        raw = sys.stdin.buffer.read(EVENT_LIMIT + 1)
        require(len(raw) <= EVENT_LIMIT, 'event exceeds read limit')
        result = handle(parse_json(raw.decode('utf-8')), args.project_config)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        result = {'systemMessage': f'Task harness not ready: {str(error)[:240]}'}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
