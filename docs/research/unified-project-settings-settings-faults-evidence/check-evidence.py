"""Read-only independent assertions over recorded real settings trials."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 assert value,name
def load(name):return json.loads((ROOT/name/'summary.json').read_text())
def events(name,phase='phase1'):
 return [json.loads(s)for s in (ROOT/name/(phase+'.stdout.jsonl')).read_text().splitlines()]
def commands(name,phase='phase1'):
 return [e['item']for e in events(name,phase)if e.get('type')=='item.completed'and e.get('item',{}).get('type')=='command_execution']
valid=['repair-order','matcher-scope','write-failure-scoped-tools','read-failure-scoped-tools','delete-failure-scoped-tools']
for name in valid:
 s=load(name)
 check(name+': real terminal turns',all(p['exit_code']==0 and p['owned_process_terminal']for p in s['phases']))
 check(name+': correct final candidate',s['candidate_manifest_sha256']=='7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e')
 check(name+': original config/auth unchanged',s['global_config_auth_unchanged'])
 check(name+': preserve unchanged',s['initial_files']['preserve.txt']==s['final_files']['preserve.txt'])
 check(name+': helper scripts physically absent',not any('/scripts/'in n for n in s['initial_files']))
s=load('repair-order');p=ROOT/'repair-order/artifacts';md=(p/'project-setting.md').read_text();contracts=list((p/'docs/plans').glob('*.task-contract.md'))
check('repair: exact outcome',(p/'docs/research/repair-order.research.md').read_bytes()==b'REPAIR_ORDER_OK\n')
check('repair: schema 1 unique',len(re.findall(r'^\|\s*schema_version\s*\|\s*1\s*\|$',md,re.M))==1)
check('repair: unrelated section and model row retained','KEEP_CUSTOM_SECTION'in md and '|  model.default   |  [gpt-6.1-sol;low]  |'in md)
check('repair: original whitespace/order retained',md.index('|   hook-receipt')<md.index('| research')<md.index('|   task-contract'))
check('repair: one accepted contract',len(contracts)==1 and json.loads(re.search(r'```json\n(.*?)\n```',contracts[0].read_text(),re.S)[1])['status']=='done')
s=load('matcher-scope');check('matcher: all project bytes unchanged',s['initial_files']==s['final_files'])
text='\n'.join(e.get('item',{}).get('text','')for e in events('matcher-scope'))
check('matcher: partial startup coverage reported',all(v in text for v in ['startup','resume','compact','不等效']))
for name in valid[2:]:
 s=load(name)
 for file in ['harness-project.json','preserve.txt','docs/plans/harness/legacy.md','docs/research/receipts/old.jsonl']:
  check(name+': retained '+file,s['initial_files'][file]==s['final_files'][file])
 check(name+': no backup or replacement settings',not any(n.endswith('.bak')or n.endswith('.backup')for n in s['final_files']))
s=load('write-failure-scoped-tools')
check('write fault: original settings unchanged',s['initial_files']['project-setting.md']==s['final_files']['project-setting.md'])
write=[i for i in commands('write-failure-scoped-tools')if i.get('exit_code')!=0 and 'operation not permitted: project-setting.md'in i.get('aggregated_output','').lower()]
check('write fault: one real denied merge',len(write)==1 and write[0]['exit_code']!=0)
s=load('delete-failure-scoped-tools')
check('delete fault: new settings unchanged',s['initial_files']['project-setting.md']==s['final_files']['project-setting.md'])
delete=[i for i in commands('delete-failure-scoped-tools')if i.get('exit_code')!=0 and 'rm: harness-project.json: Operation not permitted'in i.get('aggregated_output','')]
check('delete fault: one real denied unlink',len(delete)==1 and delete[0]['exit_code']!=0)
s=load('read-failure-scoped-tools');first=json.loads((ROOT/'read-failure-scoped-tools/phase1-files.json').read_text())
check('read fault: first phase actually wrote new settings',s['initial_files']['project-setting.md']!=first['project-setting.md'])
check('read fault: phase2 made no project mutations',first==s['final_files'])
check('read fault: controller confirmed EACCES',any(v.get('controller_read_denied')and v.get('errno')==13 for v in s['controls']))
check('read fault: actual model read denied',any('cat: project-setting.md: Permission denied'in i.get('aggregated_output','')for i in commands('read-failure-scoped-tools','phase2')))
check('read fault: both phases terminal',len(s['phases'])==2)
for name in ['write-failure','read-failure','delete-failure']:
 check(name+': original sandbox-confounded raw retained',(ROOT/name/'phase1.stdout.jsonl').is_file())
print(json.dumps({'count':len(checks),'checks':checks},ensure_ascii=False,indent=2))
