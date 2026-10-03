"""Read-only receipt/native-command matching and nonzero-process inventory."""
from pathlib import Path
import hashlib
import json
import shlex

b = Path(__file__).resolve().parent
w = Path(json.loads((b / 'run.json').read_text())['workspace'])
commands, errors, patch_errors = [], [], []
for actor in json.loads((b / 'lifecycle-observation.json').read_text()):
    for o in actor['observations']:
        p = o['payload']
        item = p.get('item', {})
        if p['type'] != 'item_completed' or item.get('type') != 'CommandExecution':
            continue
        c = dict(actor=actor['actor'], source_file=actor['source_file'], source_line=o['source_line'],
                 command=item['command'], cwd=item['cwd'].removeprefix('file://'),
                 exit_code=item['exit_code'], stdout=item.get('stdout', ''), stderr=item.get('stderr', ''))
        commands.append(c)
        if c['exit_code'] not in (0, None):
            errors.append(c)
for trace in (b / 'native-traces').glob('reval*.json'):
    a = json.loads(trace.read_text())
    for ev in a['events']:
        p = ev['payload']
        if p['type'] in ('function_call_output', 'custom_tool_call_output') and 'Script error:' in str(p.get('output', '')):
            patch_errors.append(dict(actor=a['identity']['agent_path'], source_file=a['source_file'],
                                     source_line=ev['source_line'], call_id=p['call_id'], output=p['output']))
results = []
for model in ('sol61', 'sol56'):
    original = json.loads((b / model / 'original-inputs.json').read_text())
    for f in sorted((b / model).glob('*/evidence/*.json')):
        r = json.loads(f.read_text())
        matched = []
        for c in commands:
            text = c['command'][-1]
            marker = '/scripts/run_check.py'
            if marker not in text:
                continue
            start = text.rfind(' ', 0, text.index(marker)) + 1
            tokens = shlex.split(text[start:])
            if '--output' not in tokens or '--' not in tokens:
                continue
            output = Path(c['cwd']) / tokens[tokens.index('--output') + 1]
            if output != w / model / f.relative_to(b / model):
                continue
            assert tokens[tokens.index('--') + 1:] == r['argv'], f
            assert c['cwd'] == r['cwd'] and c['exit_code'] == r['returncode'], f
            matched.append(dict(actor=c['actor'], source_line=c['source_line'], source_file=c['source_file']))
        assert len(matched) == 1, (f, matched)
        versions = []
        for name, h in r['sources_after'].items():
            rel = Path(name).relative_to(w / model)
            current = hashlib.sha256((b / model / rel).read_bytes()).hexdigest()
            if h == current:
                versions.append(dict(source=str(rel), version='archived current'))
            else:
                assert str(rel) in original and hashlib.sha256(original[str(rel)].encode()).hexdigest() == h
                versions.append(dict(source=str(rel), version='original preimage, failed before-check'))
        results.append(dict(receipt=str(f.relative_to(b)), state=r['state'], returncode=r['returncode'],
                            sources_stable=r['sources_stable'], provenance=matched, versions=versions))
    for name, h in json.loads((b / model / 'misleading-baseline.json').read_text()).items():
        assert hashlib.sha256((b / model / 'misleading' / name).read_bytes()).hexdigest() == h
(b / 'receipt-integrity.json').write_text(json.dumps(dict(receipts=results, exact_argv_cwd_process_match=True,
    source_versions_valid=True, negative_protected_inputs_unchanged=True), ensure_ascii=False, indent=2) + '\n')
(b / 'observed-process-errors.json').write_text(json.dumps(dict(nonzero_commands=errors,
    tool_script_errors=patch_errors), ensure_ascii=False, indent=2) + '\n')
print(f'{len(results)} attributable receipts; {len(errors)} nonzero processes; {len(patch_errors)} script errors')
