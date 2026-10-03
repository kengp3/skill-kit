"""Archive completed fixtures and verify native provenance; not a behavior evaluator."""
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
sessions = Path('/Users/kengp3/.codex/sessions/2026/10')

def save(name, value):
    (here / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

subprocess.run([sys.executable, str(here / 'export_traces.py'), str(sessions), str(here / 'native-traces')], check=True)
manifest = json.loads((here / 'native-traces/manifest.json').read_text())
assert len(manifest) == 12, 'Require eight main actors and four workers'
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
        if row['type'] == 'event_msg' and payload.get('type') in ('task_complete', 'item_started', 'item_completed'):
            observations.append(dict(**provenance, payload=payload))
    expected = 'gpt-6.1-sol' if '_61_' in entry['actor'] else 'gpt-5.6-sol'
    actual = sorted({c['model'] for c in contexts})
    assert actual == [expected], (entry['actor'], actual)
    assert any(o['payload']['type'] == 'task_complete' for o in observations), entry['actor']
    terminal.append(entry['actor'])
    models.append(dict(actor=entry['actor'], source_file=str(source), actual_models=actual, contexts=contexts))
    lifecycle.append(dict(actor=entry['actor'], source_file=str(source), observations=observations))
save('model-observation.json', models)
save('lifecycle-observation.json', lifecycle)
save('trace-verification.json', dict(actors=len(manifest), tool_events=sum(x['events'] for x in manifest), raw_hashes_match=True, terminal_actors=terminal))
for model in ('sol61', 'sol56'):
    destination = here / model
    assert not destination.exists(), 'Never overwrite archived fixture'
    shutil.copytree(workspace / model, destination, ignore=shutil.ignore_patterns('__pycache__'))
    for relative, expected in run['runtime_sha256'].items():
        for root in (repo / 'skills/task-harness', workspace / model / 'skill', destination / 'skill'):
            assert digest(root / relative) == expected, (root, relative)
    argv = [sys.executable, '-B', str(destination / 'verify.py'), str(repo / 'skills/task-harness')]
    result = subprocess.run(argv, capture_output=True, text=True)
    save(model + '/verification-process.json', dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    save(model + '/verification.json', json.loads(result.stdout))
baseline = json.loads((here / 'preservation-baseline.json').read_text())
changed = [name for name, expected in baseline.items() if not (repo / name).is_file() or digest(repo / name) != expected]
save('preservation-check.json', dict(checked=len(baseline), changed=changed))
assert not changed, changed
save('runtime-check.json', dict(runtime_sha256=run['runtime_sha256'], source_and_two_workspaces_and_archives_match=True))
actors = json.loads((here / 'actors.json').read_text())
for actor in actors:
    assert actor['handle'] in terminal
    actor.update(state='completed', evidence='lifecycle-observation.json')
save('actors.json', actors)
print('Collected all terminal actors; interpret behavior independently.')
