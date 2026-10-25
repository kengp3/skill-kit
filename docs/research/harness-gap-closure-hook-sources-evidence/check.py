"""Independent saved-artifact seam; optional argument 2 supplies original root for a public snapshot."""
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
assert (p/'ledger.txt').read_bytes()==b'G06_ONCE\n', 'model-written canary must exist exactly once'
assert (p/'preserve.txt').read_bytes()==b'G06_PRESERVE\n'
cs=list((p/'docs/plans').glob('*.task-contract.md'))
assert len(cs)==1, 'one contract required'
s=cs[0].read_text(); assert s.count('<!-- task-harness-contract:v1 -->')==1
c=json.loads(s.split('```json',1)[1].split('```',1)[0])
assert c['task_id']=='g06-lifecycle' and c['project_root']==(sys.argv[2] if len(sys.argv)>2 else str(p))
assert c['status'] in ('in_progress','done')
assert c['requirements'][0]['status']=='done' and not c['recovery']['unknown_operations']
print(json.dumps({'product':'exact bytes','contract':str(cs[0]),'task_id':c['task_id'],'status':c['status']}))
