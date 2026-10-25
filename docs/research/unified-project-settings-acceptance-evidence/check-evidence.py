"""Read-only checks of literal expected outcomes; does not execute the product."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
results={}
def check(name,condition):
 assert condition,name
 results[name]='pass'
def contract(path):return json.loads(re.search(r'```json\n(.*?)\n```',path.read_text(),re.S)[1])
p=HERE/'staged/A-standalone/artifacts';s=(p/'project-setting.md').read_text()
check('A_five_categories_no_harness',all('| '+n+' |'in s for n in ('prd','spec','plan','adr','research'))and'Task Harness'not in s and'task-contract'not in s)
check('A_preserved',(p/'preserve.txt').read_bytes()==b'KEEP_EXISTING_CONTENT\n')
p=HERE/'staged/BD-nohelpers/artifacts';c=contract(p/'docs/plans/basic-result.task-contract.md')
check('BD_exact_result_one_done_contract',(p/'docs/research/basic-result.research.md').read_bytes()==b'BASIC_TASK_OK\n'and c['status']=='done'and len(list((p/'docs/plans').glob('*.task-contract.md')))==1)
run=json.loads((HERE/'staged/BD-nohelpers/run.json').read_text())
check('BD_no_installed_script_helpers',not any('/scripts/'in n for n in run['source_files']))
for name in ('C-migration','C-conflict'):
 p=HERE/'staged'/name;before=json.loads((p/'fixture-before.json').read_text())
 for rel,text in before.items():
  if rel in ('harness-project.json','project-setting.md')and name=='C-migration':continue
  check(name+':preserved:'+rel,(p/'artifacts'/rel).read_text()==text)
p=HERE/'staged/C-migration/artifacts';s=(p/'project-setting.md').read_text()
check('C_success_deletes_only_legacy',not(p/'harness-project.json').exists()and'docs/plans/harness/{filename}'in s and'docs/research/receipts/{filename}'in s)
p=HERE/'staged/E-resume/artifacts';c=contract(p/'docs/plans/resume-once.task-contract.md')
check('E_unknown_reconciled_no_replay',(p/'ledger.txt').read_bytes()==b'APPENDED_ONCE\n'and(p/'docs/research/resume-result.research.md').read_bytes()==b'RESUMED_OK\n'and c['status']=='done'and c['recovery']['unknown_operations']==[])
p=HERE/'staged/G-disabled/artifacts';c=contract(p/'docs/plans/no-agent.task-contract.md')
check('G_independent_pending_other_work_done',c['status']!='done'and {x['id']:x['status']for x in c['requirements']}=={'T1':'blocked','T2':'done'}and(p/'docs/research/no-agent.research.md').read_bytes()==b'MAIN_WORK_DONE\n')
p=HERE/'readonly-invalid';s=json.loads((p/'summary.json').read_text())
check('readonly_all_project_bytes_preserved',s['initial_files']==s['final_files'])
p=HERE/'packaged-hooks';s=json.loads((p/'summary.json').read_text())
check('installed_candidate_manifest_matches',s['candidate_manifest_sha256']==s['installed_manifest_sha256'])
check('packaged_result_exact',(p/'artifacts/docs/research/packaged-result.research.md').read_bytes()==b'PACKAGED_OK\n')
for name in ('packaged-hooks','readonly-invalid'):
 events=json.loads((HERE/name/'hook-session-records.json').read_text());injections=[e for e in events if e.get('type')=='response_item'and e.get('payload',{}).get('role')=='developer']
 check(name+':two_actual_hook_injections',len(injections)==2)
p=HERE/'standalone-copy/artifacts';actual=json.loads((p/'.codex/hooks.json').read_text())['hooks'];canonical=json.loads(Path('/private/tmp/unified-review-final-0.3.0/skills/task-harness/assets/codex-hooks.json').read_text())['hooks']
check('copy_canonical_handlers_each_once',all(sum(h==wanted for g in actual.get(event,[])for h in g['hooks'])==1 for event,groups in canonical.items()for g in groups for wanted in g['hooks']))
p=HERE/'fallback-dispatch';text=(p/'model.stdout.jsonl').read_text()
check('fallback_real_model_not_found','model_not_found'in text and'The \'not-a-real-model-for-unified-test\' model is not supported'in text)
c=contract(p/'artifacts/docs/plans/fallback.task-contract.md');check('fallback_contract_done',c['status']=='done')
check('fallback_preserves_input_and_settings',all(json.loads((p/'summary.json').read_text())['initial_files'][name]==hashlib.sha256((p/'artifacts'/name).read_bytes()).hexdigest() for name in ('preserve.txt','project-setting.md','.codex/agents/unavailable_worker.toml')))
p=HERE/'hook-recovery';before=p/'artifacts-phase1';after=p/'artifacts';c1=contract(before/'docs/plans/hook-recovery.task-contract.md');c2=contract(after/'docs/plans/hook-recovery.task-contract.md')
check('recovery_both_native_turns_terminal',all(x['exit_code']==0 for x in json.loads((p/'summary.json').read_text())['phases']))
check('recovery_wait_no_early_T2',c1['authorization']['mode']=='wait'and not(before/'docs/research/recovery-result.research.md').exists())
check('recovery_same_contract_no_double_effect',c1['task_id']==c2['task_id']and c2['status']=='done'and(before/'ledger.txt').read_bytes()==(after/'ledger.txt').read_bytes()==b'T1_ONCE\n'and len(list((after/'docs/plans').glob('*.task-contract.md')))==1)
check('recovery_T2_exact',(after/'docs/research/recovery-result.research.md').read_bytes()==b'RECOVERED_OK\n')
check('recovery_unrelated_handler_kept','echo UNRELATED_SENTINEL'in(after/'.codex/hooks.json').read_text()and'exit 17'not in(after/'.codex/hooks.json').read_text())
final=json.loads((HERE/'final-loader/summary.json').read_text());check('final_candidate_native_load_exact',final['installed_manifest_matches']and final['canonical_asset_matches_plugin_hooks']and len(final['skills'])==4 and len(final['hooks'])==3)
check('all_new_trials_global_config_auth_preserved',all(json.loads((HERE/n/'summary.json').read_text())['global_config_auth_unchanged'] for n in ('packaged-hooks','readonly-invalid','model-policy','standalone-copy','fallback-dispatch','hook-recovery','effort-preflight','migration-resume','final-loader','final-upgrade')))
p=HERE/'effort-preflight';metadata=json.loads((p/'artifacts/host-model-metadata.json').read_text());model=next(x for x in metadata['data']if x['model']=='gpt-6-sol')
check('effort_real_host_metadata_preflight',model['defaultReasoningEffort']=='medium'and'none'not in [x['reasoningEffort']for x in model['supportedReasoningEfforts']])
check('effort_keeps_model_uses_host_default',any(x['model']=='gpt-6-sol'and x['effort']=='medium'for x in json.loads((p/'session-contexts.json').read_text())))
summary=json.loads((p/'summary.json').read_text());check('effort_long_term_settings_unchanged',summary['initial_files']['project-setting.md']==summary['final_files']['project-setting.md'])
p=HERE/'migration-resume';a=p/'artifacts';summary=json.loads((p/'summary.json').read_text())
check('migration_resume_deletes_only_legacy',not(a/'harness-project.json').exists()and summary['initial_files']['project-setting.md']==summary['final_files']['project-setting.md'])
check('migration_resume_preserves_history_bytes',(a/'docs/plans/harness/legacy.md').read_bytes()==b'# Historical artifact\nKEEP_CONTRACT_BYTES\n'and(a/'docs/research/receipts/old.jsonl').read_bytes()==b'{"kind":"legacy"}\n')
upgrade=json.loads((HERE/'final-upgrade/summary.json').read_text());check('final_exact_upgrade_native_loaded',upgrade['upgraded_from']=='0.2.1'and upgrade['installed_manifest_matches']and upgrade['canonical_asset_matches_plugin_hooks'])
check('temporary_credential_states_removed',all(not Path(json.loads((HERE/n/'summary.json').read_text())['state_root']).exists()for n in ('packaged-hooks','readonly-invalid','model-policy','standalone-copy','fallback-dispatch','hook-recovery','effort-preflight','migration-resume')))
# This checks only accidental archival exposure, never prints credential values.
auth=json.loads(Path('/Users/kengp3/.codex/auth.json').read_text())
def strings(x):
 if isinstance(x,dict):return [s for v in x.values()for s in strings(v)]
 if isinstance(x,list):return [s for v in x for s in strings(v)]
 return [x]if isinstance(x,str)and len(x)>=20 else []
secrets=[s.encode()for s in strings(auth)]
check('no_credentials_archived',all(f.name!='auth.json'and not any(s in f.read_bytes()for s in secrets)for f in HERE.rglob('*')if f.is_file()))
(HERE/'assertions.json').write_text(json.dumps({'checks':results,'count':len(results),'scope':'artifact and raw-record verification only; not new product executions'},ensure_ascii=False,indent=2))
print('Evidence assertions passed:',len(results))
