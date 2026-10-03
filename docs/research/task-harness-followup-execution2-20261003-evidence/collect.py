"""Archive this completed four-case run; behavioral gates require trace review."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
run = json.loads((here / 'run.json').read_text())
workspace = Path(run['workspace'])
sessions = Path('/Users/kengp3/.codex/sessions/2026/10/03')

def save(name, value):
    (here / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

subprocess.run([sys.executable, str(here / 'export_traces.py'), str(sessions), str(here / 'native-traces')], check=True)
manifest = json.loads((here / 'native-traces/manifest.json').read_text())
assert len(manifest) == 8, 'Four coordinators and four workers required'
models, lifecycle, terminal = [], [], []
for entry in manifest:
    trace = json.loads((here / 'native-traces' / entry['file']).read_text())
    source = sessions / trace['source_file']
    lines = source.read_text().splitlines(keepends=True)
    assert hashlib.sha256(lines[0].encode()).hexdigest() == trace['identity_raw_line_sha256']
    for event in trace['events']:
        assert hashlib.sha256(lines[event['source_line'] - 1].encode()).hexdigest() == event['raw_line_sha256']
    contexts, observations = [], []
    for number, line in enumerate(lines, 1):
        row = json.loads(line)
        payload = row.get('payload', {})
        provenance = dict(source_line=number, raw_line_sha256=hashlib.sha256(line.encode()).hexdigest(), timestamp=row.get('timestamp'))
        if row['type'] == 'turn_context':
            contexts.append(dict(**provenance, model=payload.get('model')))
        if row['type'] == 'event_msg' and payload.get('type') in ('task_started', 'task_complete', 'item_started', 'item_completed'):
            observations.append(dict(**provenance, payload=payload))
    expected = 'gpt-6.1-sol' if '_61_' in entry['actor'] else 'gpt-5.6-sol'
    assert {c['model'] for c in contexts} == {expected}, entry['actor']
    assert any(o['payload']['type'] == 'task_complete' for o in observations), entry['actor']
    terminal.append(entry['actor'])
    models.append(dict(actor=entry['actor'], source_file=str(source), contexts=contexts))
    lifecycle.append(dict(actor=entry['actor'], source_file=str(source), observations=observations))
save('model-observation.json', models)
save('lifecycle-observation.json', lifecycle)
save('trace-verification.json', dict(actors=len(manifest), tool_events=sum(x['events'] for x in manifest), raw_hashes_match=True, terminal_actors=terminal))

checks = []
for model in ('sol61', 'sol56'):
    source = workspace / model
    destination = here / model
    assert not destination.exists(), 'Never overwrite an archived fixture'
    baseline = json.loads((source / 'baseline.json').read_text())
    for relative in json.loads((source / 'protected.json').read_text()):
        assert digest(source / relative) == baseline[relative], relative
    for relative, expected in run['runtime_sha256'].items():
        assert digest(source / 'skill' / relative) == expected
        assert digest(repo / 'skills/task-harness' / relative) == expected
    for counter in ('probe-attempts.txt', 'unavailable-attempts.txt'):
        assert (source / 'resume' / counter).read_text() == '2', counter
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns('__pycache__'))
    for case in ('parallel', 'resume'):
        argv = [sys.executable, '-B', 'check.py']
        result = subprocess.run(argv, cwd=destination / case, text=True, capture_output=True, timeout=20)
        checks.append(dict(model=model, case=case, argv=argv, cwd=str(destination / case), returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
save('artifact-checks.json', checks)
assert all(c['returncode'] == 0 for c in checks)
baseline = json.loads((here / 'preservation-baseline.json').read_text())
authorized = {'skills/task-harness/SKILL.md', 'docs/specs/task-harness.spec.md', 'docs/plans/task-harness-followup-remediation-20261003.plan.md'}
changed = [p for p, h in baseline.items() if p not in authorized and (not (repo / p).is_file() or digest(repo / p) != h)]
save('preservation-check.json', dict(checked=len(baseline)-len(authorized), changed=changed))
assert not changed, changed
actors = json.loads((here / 'actors.json').read_text())
for actor in actors:
    assert actor['handle'] in terminal
    actor.update(state='completed', evidence='lifecycle-observation.json')
save('actors.json', actors)
print('PASS: eight native terminal actors, exact models, four artifact checks, counters and preservation. Review G1-G5 separately.')
