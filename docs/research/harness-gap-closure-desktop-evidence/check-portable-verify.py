"""Exercise the offline --verify CLI from another checkout with unavailable provenance."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
KIT = 'manual-kit-20261026-4a9d7f20'
PROMPTS = ('stop-start.prompt.txt', 'stop-resume.prompt.txt', 'model-start.prompt.txt', 'model-continue.prompt.txt')

with tempfile.TemporaryDirectory(prefix='g07-relocated-verify-') as tmp:
    relocated = Path(tmp)/'another-checkout'; relocated.mkdir()
    builder = relocated/'prepare-manual-kit.py'
    shutil.copyfile(HERE/builder.name, builder)
    for name in PROMPTS: shutil.copyfile(HERE/name, relocated/name)
    shutil.copytree(HERE/KIT, relocated/KIT)
    manifest_path = relocated/KIT/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    for item in manifest['prompts']:
        item['template'] = str(Path(tmp)/'removed-original-worktree'/item['file'])
        assert not Path(item['template']).exists()
    manifest_path.write_text(json.dumps(manifest))
    def verify():
        return subprocess.run([sys.executable, str(builder), '--verify'], capture_output=True, text=True)
    result = verify()
    assert result.returncode == 0, f'relocated verify failed with unavailable historical paths: {result.stderr}'
    assert json.loads(result.stdout)['result'] == 'passed'
    print('relocated --verify with unavailable historical template paths: passed')
    original_hash = manifest['prompts'][0]['template_sha256']
    manifest['prompts'][0]['template_sha256'] = '0'*64
    manifest_path.write_text(json.dumps(manifest))
    result = verify()
    assert result.returncode != 0 and 'prepared prompt/template changed' in result.stderr
    print('wrong template hash: rejected')
    manifest['prompts'][0]['template_sha256'] = original_hash
    prompt_hash = manifest['prompts'][0]['sha256']
    manifest['prompts'][0]['sha256'] = '0'*64
    manifest_path.write_text(json.dumps(manifest))
    result = verify()
    assert result.returncode != 0 and 'prepared prompt/template changed' in result.stderr
    print('wrong prepared prompt hash: rejected')
    manifest['prompts'][0]['sha256'] = prompt_hash
    for bad_name in ('../stop-start.prompt.txt', str(relocated/'stop-start.prompt.txt'), 'unexpected.prompt.txt'):
        manifest['prompts'][0]['file'] = bad_name
        manifest_path.write_text(json.dumps(manifest))
        result = verify()
        assert result.returncode != 0 and 'prepared prompt inventory mismatch' in result.stderr
    print('traversal, absolute and unexpected prompt names: rejected before prompt reads')
    manifest['prompts'][0]['file'] = PROMPTS[0]
    manifest['prompts'][1]['file'] = PROMPTS[0]
    manifest_path.write_text(json.dumps(manifest))
    result = verify()
    assert result.returncode != 0 and 'prepared prompt inventory mismatch' in result.stderr
    print('duplicate/missing expected prompt: rejected')
