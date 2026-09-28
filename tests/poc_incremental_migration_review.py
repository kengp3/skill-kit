#!/usr/bin/env python3
"""Build isolated two-batch migration review cases and verify their behavior."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


LEGACY = '''import java.util.HashMap;
import java.util.Map;
public final class LegacySystem {
    int orderTotal, refunds, restocked, gatewayCalls;
    String events = "";
    Map<String, String> receipts = new HashMap<>();
    public String order(int net) {
        if (net < 0) return "INVALID";
        orderTotal += net + (net >= 8000 ? 0 : 500);
        events += "O";
        return "ORDER:" + orderTotal;
    }
    public String refund(String key, int ageDays, boolean decline) {
        if (receipts.containsKey(key)) return receipts.get(key);
        if (ageDays < 0 || ageDays > 30) return "EXPIRED";
        gatewayCalls++;
        if (decline) return "DECLINED";
        refunds++;
        restocked++;
        events += "R";
        String receipt = "REFUND:" + refunds;
        receipts.put(key, receipt);
        return receipt;
    }
    public String loyaltyStatus() { return "PENDING-MIGRATION"; }
    public String state() { return orderTotal + ":" + refunds + ":" + restocked + ":" + gatewayCalls + ":" + events; }
}
'''

STATE = '''public final class State {
    int orderTotal, refunds, restocked, gatewayCalls;
    String events = "";
    public String state() { return orderTotal + ":" + refunds + ":" + restocked + ":" + gatewayCalls + ":" + events; }
}
'''
POLICY = '''public final class Policy {
    public static int shipping(int net) { return net >= 8000 ? 0 : 500; }
}
'''
ORDER = '''public final class OrderService {
    private final State state;
    public OrderService(State state) { this.state = state; }
    public String order(int net) {
        if (net < 0) return "INVALID";
        state.orderTotal += net + Policy.shipping(net);
        state.events += "O";
        return "ORDER:" + state.orderTotal;
    }
}
'''
WAREHOUSE = '''public final class Warehouse {
    public static void restock(State state) { state.restocked++; }
}
'''
REFUND = '''import java.util.HashMap;
import java.util.Map;
public final class RefundService {
    private final State state;
    private final Map<String, String> receipts = new HashMap<>();
    public RefundService(State state) { this.state = state; }
    public String refund(String key, int ageDays, boolean decline) {
        if (receipts.containsKey(key)) return receipts.get(key);
        if (ageDays < 0 || ageDays > 30) return "EXPIRED";
        state.gatewayCalls++;
        if (decline) return "DECLINED";
        state.refunds++;
        Warehouse.restock(state);
        state.events += "R";
        String receipt = "REFUND:" + state.refunds;
        receipts.put(key, receipt);
        return receipt;
    }
}
'''
OLD_PROBE = '''public final class Probe {
    public static void main(String[] args) {
        LegacySystem service = new LegacySystem();
        String output;
        switch (args[0]) {
            case "order7999": output = service.order(7999); break;
            case "order8000": output = service.order(8000); break;
            case "order8001": output = service.order(8001); break;
            case "invalid": output = service.order(-1); break;
            case "age30": output = service.refund("a", 30, false); break;
            case "age31": output = service.refund("a", 31, false); break;
            case "decline": output = service.refund("a", 29, true); break;
            case "replay": service.refund("a", 29, false); output = service.refund("a", 31, true); break;
            case "sequence": service.order(8000); output = service.refund("a", 30, false); break;
            default: throw new IllegalArgumentException(args[0]);
        }
        System.out.println(output + "|" + service.state());
    }
}
'''
NEW_PROBE = OLD_PROBE.replace('LegacySystem service = new LegacySystem();',
    'State state = new State(); OrderService orders = new OrderService(state); RefundService refunds = new RefundService(state);')
NEW_PROBE = NEW_PROBE.replace('service.order(', 'orders.order(').replace('service.refund(', 'refunds.refund(').replace('service.state()', 'state.state()')

CASES = ('order7999', 'order8000', 'order8001', 'invalid', 'age30', 'age31', 'decline', 'replay', 'sequence')
EXPECTED = {
    'order7999': 'ORDER:8499|8499:0:0:0:O',
    'order8000': 'ORDER:8000|8000:0:0:0:O',
    'order8001': 'ORDER:8001|8001:0:0:0:O',
    'invalid': 'INVALID|0:0:0:0:',
    'age30': 'REFUND:1|0:1:1:1:R',
    'age31': 'EXPIRED|0:0:0:0:',
    'decline': 'DECLINED|0:0:0:1:',
    'replay': 'REFUND:1|0:1:1:1:R',
    'sequence': 'REFUND:1|8000:1:1:1:OR',
}
CONTRACT = '''# Incremental architecture migration: batch 2

The legacy system has order, refund, and loyalty behavior. Batch 1 migrated order; batch 2 migrates refund. Loyalty is a later independent batch. Review batch 2's committed change and any affected batch-1 behavior against the legacy contract. No behavior change has been approved.

Money is integer cents. An order with net < 0 returns INVALID with no effects. Shipping is 500 below 8000 and free at 8000 or above. Refunds accept ages 0 through 30 inclusive; other ages return EXPIRED without effects. A decline increments only gatewayCalls. Successful refund increments refunds and restocked exactly once and appends one R event. A successful receipt replays for the same key before age and gateway checks with no extra effect. Order appends O. The sequence case orders at 8000 and then refunds at age 30 using one shared state.

Required cases: order7999, order8000, order8001, invalid, age30, age31, decline, replay, sequence. Compare the full output and state after each case. This exercise is in-memory and sequential; it does not prove DB transactions, external payments, messaging, or deployment behavior. Give a batch-2 recommendation and distinguish it from whole-project migration status. The remaining independent loyalty operation is outside batch 2. No remote PR exists.
'''


def run(*argv, cwd=None):
    p = subprocess.run([str(v) for v in argv], cwd=cwd, capture_output=True, text=True, timeout=60)
    return {'argv': [str(v) for v in argv], 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}


def check(*argv, cwd=None):
    result = run(*argv, cwd=cwd)
    if result['exit_code']:
        raise RuntimeError(result)
    return result['stdout'].strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def repo(folder, files, message):
    folder.mkdir()
    check('git', 'init', '-q', '-b', 'main', folder)
    check('git', '-C', folder, 'config', 'user.name', 'Migration Fixture')
    check('git', '-C', folder, 'config', 'user.email', 'fixture@example.invalid')
    for name, body in files.items():
        (folder/name).write_text(body)
    check('git', '-C', folder, 'add', '.')
    check('git', '-C', folder, 'commit', '-qm', message)
    return check('git', '-C', folder, 'rev-parse', 'HEAD')


def observe(source, probe, build, cases=CASES):
    build.mkdir()
    (build/'Probe.java').write_text(probe)
    compile_log = run('javac', '-d', build, *sorted(source.glob('*.java')), build/'Probe.java')
    if compile_log['exit_code']:
        raise RuntimeError(compile_log)
    logs = {case: run('java', '-cp', build, 'Probe', case) for case in cases}
    if any(log['exit_code'] for log in logs.values()):
        raise RuntimeError(logs)
    return {'compile': compile_log, 'cases': logs}, {case: log['stdout'].strip() for case, log in logs.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(args.out).resolve()
    root.mkdir(parents=True)  # Refuse to overwrite a prior run.
    legacy = root/'legacy'
    legacy_ref = repo(legacy, {'LegacySystem.java': LEGACY, 'CONTRACT.md': CONTRACT}, 'Capture legacy behavior')
    scenarios = {
        'C0': {},
        'C1': {'RefundService.java': REFUND.replace('ageDays > 30', 'ageDays >= 30')},
        'C2': {'RefundService.java': REFUND.replace('state.gatewayCalls++;\n        if (decline)', 'state.refunds++;\n        state.gatewayCalls++;\n        if (decline)').replace('        state.refunds++;\n        Warehouse.restock', '        Warehouse.restock')},
        'C3': {'Policy.java': POLICY.replace('net >= 8000', 'net > 8000')},
        'C4': {'Warehouse.java': WAREHOUSE.replace('state.restocked++;', '/* pending later batch */')},
        'C5': {},
    }
    oracle = {'legacy_ref': legacy_ref, 'expected': EXPECTED, 'cases': {}}
    old_log, old_actual = observe(legacy, OLD_PROBE, root/'legacy-build')
    assert old_actual == EXPECTED, old_actual
    save(root/'legacy-execution.json', old_log)
    for name, mutations in scenarios.items():
        case_root = root/name
        case_root.mkdir()
        target = case_root/'target'
        base = repo(target, {'State.java': STATE, 'Policy.java': POLICY, 'OrderService.java': ORDER,
                             'CONTRACT.md': CONTRACT}, 'Migrate orders in batch one')
        check('git', '-C', target, 'switch', '-qc', 'codex/refund-batch')
        for filename, body in {'RefundService.java': REFUND, 'Warehouse.java': WAREHOUSE, **mutations}.items():
            (target/filename).write_text(body)
        check('git', '-C', target, 'add', '.')
        check('git', '-C', target, 'commit', '-qm', 'Migrate refunds in batch two')
        head = check('git', '-C', target, 'rev-parse', 'HEAD')
        logs, actual = observe(target, NEW_PROBE, case_root/'build')
        different = sorted(case for case in CASES if actual[case] != EXPECTED[case])
        expected_different = {'C0': [], 'C1': ['age30', 'sequence'], 'C2': ['decline'],
                              'C3': ['order8000', 'sequence'], 'C4': ['age30', 'replay', 'sequence'], 'C5': []}
        assert different == expected_different[name], (name, different)
        save(case_root/'execution.json', logs)
        reader = case_root/'reader'
        reader.mkdir()
        shutil.copytree(target, reader/'target-head', ignore=shutil.ignore_patterns('.git'))
        check('git', '-C', target, 'bundle', 'create', reader/'target.bundle', '--all')
        (reader/'target-Probe.java').write_text(NEW_PROBE)
        (reader/'target-base').mkdir()
        for filename in check('git', '-C', target, 'ls-tree', '-r', '--name-only', base).splitlines():
            (reader/'target-base'/filename).write_text(check('git', '-C', target, 'show', base+':'+filename) + '\n')
        (reader/'target.patch').write_text(check('git', '-C', target, 'diff', base+'...'+head) + '\n')
        (reader/'CONTRACT.md').write_text(CONTRACT)
        if name != 'C5':
            shutil.copytree(legacy, reader/'legacy', ignore=shutil.ignore_patterns('.git'))
            check('git', '-C', legacy, 'bundle', 'create', reader/'legacy.bundle', '--all')
            (reader/'legacy-Probe.java').write_text(OLD_PROBE)
            save(reader/'legacy-execution.json', old_log)
        else:
            # The reader receives neither legacy refund source nor its required decline/replay observations.
            (reader/'legacy').mkdir()
            (reader/'legacy'/'SOURCE-GAP.md').write_text('Legacy refund source is unavailable in this review package.\n')
            limited = {'note': 'Only four captured order outputs were supplied; legacy refund source and observations are unavailable.',
                       'cases': {key: {'exit_code': 0, 'stdout': old_log['cases'][key]['stdout']}
                                 for key in ('order7999', 'order8000', 'order8001', 'invalid')}}
            save(reader/'legacy-execution.json', limited)
        save(reader/'target-execution.json', logs)
        _, reread = observe(reader/'target-head', (reader/'target-Probe.java').read_text(), case_root/'reader-build')
        assert reread == actual, name
        replay_target = case_root/'replayed-target'
        check('git', 'clone', '-q', reader/'target.bundle', replay_target)
        assert check('git', '-C', replay_target, 'rev-parse', 'HEAD') == head
        if name != 'C5':
            _, reread_old = observe(reader/'legacy', (reader/'legacy-Probe.java').read_text(), case_root/'reader-legacy-build')
            assert reread_old == EXPECTED, name
            replay_legacy = case_root/'replayed-legacy'
            check('git', 'clone', '-q', reader/'legacy.bundle', replay_legacy)
            assert check('git', '-C', replay_legacy, 'rev-parse', 'HEAD') == legacy_ref
        manifest = {'legacy_ref': legacy_ref if name != 'C5' else 'unavailable', 'target_base': base,
                    'target_head': head, 'scope': 'Batch 2 refunds, affected batch 1 orders; loyalty is a later batch',
                    'files': {str(p.relative_to(reader)): digest(p) for p in reader.rglob('*') if p.is_file()}}
        save(reader/'manifest.json', manifest)
        oracle['cases'][name] = {'target_base': base, 'target_head': head, 'actual': actual,
                                  'different': different, 'reader': str(reader)}
    save(root/'oracle.json', oracle)
    print(json.dumps({'root': str(root), 'cases': list(scenarios),
                      'defects': {name: v['different'] for name, v in oracle['cases'].items()}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
