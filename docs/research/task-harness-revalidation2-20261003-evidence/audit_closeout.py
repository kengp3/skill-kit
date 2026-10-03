"""Verify current frozen run integrity and persist collection closeout; never re-execute subject checks."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, shlex
repo=Path.cwd().resolve();b=repo/'docs/research/task-harness-revalidation2-20261003-evidence'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=load(b/'run.json');work=Path(run['workspace']);manifest=load(b/'native-traces/manifest.json')
assert len(manifest)==12
modelobs=load(b/'model-observation.json');lives=load(b/'lifecycle-observation.json')
bylive={x['actor']:x for x in lives};bymodel={x['actor']:x for x in modelobs}
paircount=0;eventcount=0;terminal=[];allcommands=[];rawverified=[]
for entry in manifest:
 t=load(b/'native-traces'/entry['file']);actor=t['identity']['agent_path'];assert actor==entry['actor']
 src=Path(bylive[actor]['source_file']);raw=src.read_text().splitlines(keepends=True)
 assert hashlib.sha256(raw[0].encode()).hexdigest()==t['identity_raw_line_sha256']
 assert all(json.loads(raw[0])['payload'].get(k)==v for k,v in t['identity'].items())
 events=t['events'];assert len(events)==entry['events'];eventcount+=len(events)
 calls={};results={}
 for ev in events:
  line=raw[ev['source_line']-1];assert hashlib.sha256(line.encode()).hexdigest()==ev['raw_line_sha256'];assert all(json.loads(line)['payload'].get(k)==v for k,v in ev['payload'].items())
  p=ev['payload'];cid=p['call_id']
  target=results if p['type'].endswith('_output') else calls
  assert cid not in target;target[cid]=ev
 assert calls.keys()==results.keys();paircount+=len(calls)
 for cid,c in calls.items():assert c['source_line']<results[cid]['source_line']
 expected='gpt-6.1-sol' if '_61_' in actor else 'gpt-5.6-sol'
 contexts=bymodel[actor]['contexts'];assert contexts
 for ctx in contexts:
  line=raw[ctx['source_line']-1];assert hashlib.sha256(line.encode()).hexdigest()==ctx['raw_line_sha256']
  row=json.loads(line);assert row['type']=='turn_context' and row['payload']['model']==ctx['model']==expected
 observations=bylive[actor]['observations']
 for o in observations:
  line=raw[o['source_line']-1];assert hashlib.sha256(line.encode()).hexdigest()==o['raw_line_sha256'];assert json.loads(line)['payload']==o['payload']
  item=o['payload'].get('item',{})
  if o['payload']['type']=='item_completed' and item.get('type')=='CommandExecution':
   allcommands.append((actor,o['source_line'],item))
 assert any(o['payload']['type']=='task_complete' for o in observations);terminal.append(actor)
 rawverified.append({'actor':actor,'source_file':str(src),'source_sha256':sha(src),'events':len(events),'model':expected})
assert eventcount==224 and paircount==112
assert load(b/'trace-verification.json')['tool_events']==eventcount
runtime=[];protected=[];counters=[]
for rel,h in run['runtime_sha256'].items():
 for p in [repo/'skills/task-harness'/rel,work/'sol61/skill'/rel,work/'sol56/skill'/rel,b/'sol61/skill'/rel,b/'sol56/skill'/rel]:
  assert sha(p)==h;runtime.append({'path':str(p),'sha256':h})
assert sorted(str(p.relative_to(repo/'skills/task-harness')) for p in (repo/'skills/task-harness').rglob('*') if p.is_file())==sorted(run['runtime_sha256'])
for model in ['sol61','sol56']:
 baseline=load(b/model/'baseline.json')
 for rel in load(b/model/'protected.json'):
  assert sha(b/model/rel)==sha(work/model/rel)==baseline[rel];protected.append({'model':model,'path':rel,'sha256':baseline[rel]})
 # Archived files are the actual terminal fixture outputs, not rewritten evidence.
 for f in (b/model).rglob('*'):
  if f.is_file():assert sha(f)==sha(work/model/f.relative_to(b/model)),f
 for n in ['probe-attempts.txt','unavailable-attempts.txt']:
  assert (b/model/'resume'/n).read_text()=='2';counters.append({'model':model,'counter':n,'value':2})
 assert (b/model/'resume/deliveries.txt').read_bytes()==b''
 assert not any(p.name!='app.py' for p in (b/model/'plan').rglob('*.py'))
 receiptcheck=load(b/'receipt-integrity.json')
 # Each receipt is checked below only once outside this loop.
assert load(b/'fixture-errors.json')==[]
receipts=receiptcheck['receipts'];assert len(receipts)==23
for rr in receipts:
 r=load(b/rr['receipt']);assert r['state']==rr['state']=='finished';assert r['returncode']==rr['returncode'];assert r['sources_stable'];assert r['sources_before']==r['sources_after']
 prov=rr['provenance'];assert len(prov)==1;pr=prov[0]
 matched=[i for a,ln,i in allcommands if a==pr['actor'] and ln==pr['source_line']];assert len(matched)==1
 i=matched[0];assert i['cwd'].removeprefix('file://')==r['cwd'];assert i['exit_code']==r['returncode']
 text=i['command'][-1];marker='/scripts/run_check.py';assert marker in text
 start=text.rfind(' ',0,text.index(marker))+1
 lex=shlex.shlex(text[start:],posix=True,punctuation_chars=';&|');lex.whitespace_split=True;tokens=[]
 for token in lex:
  if token in [';','&&','||','|','&']:break
  tokens.append(token)
 assert tokens[tokens.index('--')+1:]==r['argv']
 out=(Path(r['cwd'])/tokens[tokens.index('--output')+1]).resolve()
 assert out==work/rr['receipt']
 assert str(out) in i['stdout'].splitlines()
 for src,h in r['sources_after'].items():assert sha(b/Path(src).relative_to(work))==h
for model in ['sol61','sol56']:
 check=load(b/model/'misleading/evidence/T1-check-1.json')
 hr=load(b/model/'misleading/evidence'/('T1-hash-1.json' if model=='sol61' else 'T1-sha256-1.json'))
 assert check['returncode']==7 and 'PASS' in check['stdout'] and hr['returncode']==0
 assert hr['stdout'].split()[0]==sha(b/model/'misleading/payload.txt')
for name in ['static-validation.json','runner-tests.json']:
 assert load(b/name)['returncode']==0
checks=load(b/'artifact-checks.json');assert {(c['model'],c['case']) for c in checks}=={(m,c) for m in ['sol61','sol56'] for c in ['parallel','resume']}
assert all(c['returncode']==0 for c in checks)
errors=load(b/'error-classification.json');nonzeros=load(b/'observed-process-errors.json')
assert len(errors['expected_negative_processes'])==10 and len(errors['tool_operation_processes'])==7 and len(errors['tool_script_errors'])==2
assert len(nonzeros['nonzero_commands'])==17
assert sorted((e['actor'],e['source_line'],e['exit_code']) for e in nonzeros['nonzero_commands'])==sorted((e['actor'],e['source_line'],e['exit_code']) for key in ['expected_negative_processes','tool_operation_processes'] for e in errors[key])
for key in ['expected_negative_processes','tool_operation_processes']:
 for e in errors[key]:
  matches=[i for a,ln,i in allcommands if a==e['actor'] and ln==e['source_line']];assert len(matches)==1
  i=matches[0];assert i['exit_code']==e['exit_code'] and i['command']==e['command'] and i['stdout']==e['stdout'] and i['stderr']==e['stderr']
assert errors['tool_script_errors']==nonzeros['tool_script_errors']
cases=load(b/'case-results.json')['cases'];assert len(cases)==8
assert {(c['model'],c['case']) for c in cases}=={(m,c) for m in run['models'] for c in run['cases']}
findings=load(b/'findings.json');assert len(findings['findings'])==4 and findings['fixes_applied'] is False and findings['sampling_reruns']==0
assert all(c['execution']=='completed' and c['actor'] in terminal and c['core_result']=='pass' for c in cases)
assert next(c for c in cases if c['model']=='gpt-5.6-sol' and c['case']=='parallel')['workflow_result']=='fail'
# Resolve every behavioral evidence reference; source-lines checked against the exact archived/native event.
def evidence_ref(ref):
 if isinstance(ref,str):assert (b/ref).is_file(),ref
 else:
  t=load(b/ref['artifact']);ns={e['source_line'] for e in t['events']};assert set(ref['source_lines'])<=ns
for c in cases:
 assert c['gates']
 for g in c['gates']:
  assert g['status'] in ['pass','fail','minor_deviation','observational']
  for r in g['evidence']:evidence_ref(r)
for f in findings['findings']:
 for r in f['evidence']:evidence_ref(r)
# Recompute all previously-existing files; no exclusions permitted.
baseline=load(b/'preservation-baseline.json');assert len(baseline)==2348
changed=[rel for rel,h in baseline.items() if not (repo/rel).is_file() or sha(repo/rel)!=h];assert changed==[],changed
actors=load(b/'actors.json');assert len(actors)==8 and all(a['state']=='completed' and a['handle'] in terminal for a in actors)
plan=repo/'docs/plans/task-harness-revalidation2-20261003.plan.md';report=repo/'docs/research/task-harness-revalidation2-20261003.research.md'
assert '| /root | 1 | verifying |' in plan.read_text()
auditpath=b/'completion-audit.json';assert not auditpath.exists()
links=[]
for doc in [plan,report]:
 body=doc.read_text();assert body.strip()
 for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',body):
  p=(doc.parent/target.split('#')[0]).resolve();assert p.is_relative_to(repo)
  assert p.is_file() or p==auditpath,(doc,target)
  links.append({'document':str(doc.relative_to(repo)),'target':target})
# Only after the above direct audit succeeds, persist C1 done.
s=plan.read_text().replace('| /root | 1 | verifying |','| /root | 1 | done |').replace('C1 已完成逐 gate 審閱與錯誤分類，最後 preservation／links／completion audit 正在核對；無活躍測試 workers。','C1 已完成逐 gate 審閱、錯誤分類及最後 preservation／links／completion audit；無活躍測試 workers。')
s+='\nFinal audit：[completion-audit.json](../research/task-harness-revalidation2-20261003-evidence/completion-audit.json)。收集 DoD 已達成；尚未修正受測 Skill 的 findings。\n'
plan.write_text(s);assert '| /root | 1 | done |' in plan.read_text()
audit_errors=load(b/'audit-checker-errors.json')['errors'];assert len(audit_errors)==1
for e in audit_errors:
 lines=Path(e['source_file']).read_text().splitlines(keepends=True);line=lines[e['source_line']-1]
 assert hashlib.sha256(line.encode()).hexdigest()==e['raw_line_sha256']
 item=json.loads(line)['payload']['item'];assert item['exit_code']==e['returncode']==1
 assert item['command']==e['command'] and item.get('stdout','')==e['stdout'] and item.get('stderr','')==e['stderr']
requirements=[
 ('以兩個指定模型實際執行','model-observation.json / raw turn_context；12 actors contexts exact model match'),
 ('四類案例各一次，八案例終態','actors.json / 12 raw task_complete；case-results covers exact 2×4 combinations'),
 ('Skill/runtime 完整且受測版本一致','run.json / all current, working-fixture and archived runtime bytes fingerprints matched'),
 ('官方 Skill validator 與 runner self-tests','static-validation.json / runner-tests.json actual process exit0；same current runtime'),
 ('plan-only 依賴、scope、驗收與不實作','case-results plan gates / tasks.md / raw calls / protected app.py hashes'),
 ('parallel dispatch／ownership／handoff／integration','case-results parallel gates / native coordinator+worker calls；handoff fail recorded, four safe archived checks exit0'),
 ('resume stale/unknown/tool/retry/counters/history','case-results resume gates / raw calls / process receipts / counters2 and preserved deliveries'),
 ('misleading PASS exit7／獨立 hash／assessment semantics','case-results misleading gates / raw check7 hash0 / hash stdout equals payload bytes'),
 ('收集全部觀察到的 process/script errors 與流程 findings','17 tested-agent native nonzeros＋2 script errors classified；4 scoped findings with raw references；1 root audit checker error separately preserved and corrected；Skill not fixed'),
 ('證據 attribution 與不偽造 exits/hash','224 raw event hashes／112 call-result pairs／23 exact argv,cwd,process/source receipts verified'),
 ('保留 protected inputs、歷史 evidence 與無關變更','44 protected-file instances verified against original baseline；2348 existing repo files hashes unchanged'),
 ('本輪只收集、不修改Skill、不為綠燈重跑','current runtime exact3 files unchanged；all archived fixture bytes equal terminal workspace；sampling_reruns0; non-pass verdicts retained'),
 ('完成結果報告／finding交付／tracker結案','report＋case-results＋findings read back；all evidence refs resolve；plan C1 done persisted after audit checks')]
audit={'objective':'重新驗證 Task Harness，以 gpt-6.1-sol／gpt-5.6-sol 執行並收集錯誤待後續修正','audit_time_utc':datetime.now(timezone.utc).isoformat(),'completion':'achieved','meaning':'收集與交付完成，並非受測 Skill 全流程通過或待修問題已修正。','requirements':[{'requirement':r,'status':'proven','evidence':e} for r,e in requirements],'counts':{'main_cases':8,'terminal_actors':12,'tool_events':eventcount,'call_result_pairs':paircount,'receipts':len(receipts),'safe_archived_product_checks':4,'expected_nonzero_processes':10,'tool_operation_nonzero_processes':7,'patch_script_errors':2,'root_audit_checker_errors':len(audit_errors),'medium_findings':1,'low_observations':3,'preserved_existing_repo_files':len(baseline),'protected_file_instances':len(protected)},'raw_sources_verified':rawverified,'runtime_verified':runtime,'protected_verified':protected,'retry_counters':counters,'changed_existing_repo_files':changed,'audit_checker_errors_evidence':'audit-checker-errors.json','behavioral_review':'Manual semantics with exact evidence refs in case-results; assertion-based file/trace/receipt audit only proves integrity/coverage, not universal behavioral correctness.','readback_sha256':{str(p.relative_to(repo)):sha(p) for p in [report,plan,b/'case-results.json',b/'findings.json']},'links_checked':links,'remaining_required_work':[],'pending_remediation_ids':[f['id'] for f in findings['findings']],'unverified_boundaries':load(b/'case-results.json')['unverified_boundaries']}
auditpath.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
assert load(auditpath)['completion']=='achieved'
for doc in [plan,report]:
 for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',doc.read_text()):assert (doc.parent/target.split('#')[0]).resolve().is_file(),target
print(json.dumps({'completion_audit':'achieved','counts':audit['counts'],'report':str(report),'remaining_required_work':[]},ensure_ascii=False))
