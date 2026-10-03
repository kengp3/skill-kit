"""One-shot preregistration of isolated inputs, candidate, and holdout."""
import difflib, hashlib, json, shutil, tempfile
from pathlib import Path
here=Path(__file__).resolve().parent
repo=here.parents[2]
old=repo/'docs/research/task-harness-revalidation2-20261003-evidence/sol61'
assert not (here/'matrix.json').exists()
w=Path(tempfile.mkdtemp(prefix='task-harness-handoff-poc-',dir='/private/tmp'))
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
base=(repo/'skills/task-harness/SKILL.md').read_text()
a='5. **Persist and hand off.** After coordinator acceptance, save the task\'s receipt reference and done successfully. Only then recheck readiness and save the dependent task\'s start checkpoint before its first product action. A final batch update cannot replace this handoff. If the write fails, reconcile before proceeding.'
b='''5. **Persist and hand off: two successful writes.** After coordinator acceptance, perform this sequence for a dependent task:
   - Write the accepted prerequisite's receipt reference and done state; leave the dependent task pending. Read the write's success result before proceeding.
   - Recheck readiness, then use a separate write to save the dependent task's start checkpoint from step 1. Read this write's success result before its first product action.
   Never combine prerequisite done and dependent running in one patch or file write. Two sequential awaited tool operations may share an outer call; two state edits inside one write do not satisfy the sequence. On either write failure, reconcile the saved state before proceeding.'''
assert base.count(a)==1
candidate=base.replace(a,b)
for version,text in [('B0',base),('B1',candidate)]:
 d=here/'candidates'/version
 shutil.copytree(repo/'skills/task-harness',d,ignore=shutil.ignore_patterns('__pycache__'))
 (d/'SKILL.md').write_text(text)
(here/'candidate.diff').write_text(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='B0/SKILL.md',tofile='B1/SKILL.md')))
runtime={v:{str(p.relative_to(here/'candidates'/v)):h(p) for p in (here/'candidates'/v).rglob('*') if p.is_file()} for v in ('B0','B1')}
original=json.loads((old/'original-inputs.json').read_text())
prompt='''Use the Task Harness Skill at {skill}/SKILL.md to execute this local project. Confirmed project root: {project}. Read project-setting.md. Implement subtotal(items) as sum(price_cents * quantity), including an empty list; implement label(name) by stripping surrounding whitespace and using Guest for an empty result. Implement receipt(name, items) as '<label>: <subtotal> cents'. Use exactly two native workers for the independent subtotal and label outcomes; integrate receipt yourself after their outcomes. You are not alone in the workspace; preserve others' work. Workers must have disjoint product/evidence ownership and may not delegate further. The single task tracker is tasks.md. You may write amounts.py, labels.py, receipt.py, tasks.md and evidence/ within this project; treat every other input including the Skill and check.py as read-only. Do not read other experiment runs or repository history. No network, installation, Git changes, user chats or external actions. Run meaningful direct checks and report evidence and unresolved issues. Use the same current model for workers by inheritance. Do not add sleeps or timing barriers. Stop after this project's requested outcome and verification.'''

def fixture(project,holdout=False):
 project.mkdir(parents=True)
 for f in ('amounts.py','labels.py','receipt.py'):
  (project/f).write_text(original['parallel/'+f])
 for f in ('check.py','user-note.txt','other-plan.md','project-setting.md'):
  shutil.copy2(old/'parallel'/f,project/f)
 if holdout:
  (project/'check.py').write_text('''from amounts import subtotal
from labels import label
from receipt import receipt
assert subtotal([(7,3),(101,2)]) == 223
assert subtotal([]) == 0
assert label("\\t Bob \\n") == "Bob"
assert label("\\t\\n") == "Guest"
assert receipt("\\t Bob ", [(7,3),(101,2)]) == "Bob: 223 cents"
assert receipt("", []) == "Guest: 0 cents"
print("PASS holdout integration")
''')
 (project/'tasks.md').write_text('# Authorized product outcomes\n'+ ('H7: subtotal; dependencies none\nH9: label; dependencies none\nH12: receipt integration; dependencies H7, H9\n' if holdout else 'T1: subtotal; dependencies none\nT2: label; dependencies none\nT3: receipt integration; dependencies T1, T2\n'))
entries=[]
for model in ('61','56'):
 for index,version in enumerate(('B0','B1','B1','B0'),1):
  name=f'hpoc_{model}_{index}'
  home=w/name
  fixture(home/'project')
  shutil.copytree(here/'candidates'/version,home/'skill')
  entry={'id':name,'actor':'/root/'+name,'model':f'gpt-{ "6.1" if model=="61" else "5.6"}-sol','reasoning_effort':'high','version':version,'ordinal':index,'project':str(home/'project'),'skill':str(home/'skill'),'state':'pending','task_attempt':0,'prompt':prompt.format(project=home/'project',skill=home/'skill')}
  entry['baseline']={str(p.relative_to(home)):h(p) for p in home.rglob('*') if p.is_file()}
  entry['protected']=[x for x in entry['baseline'] if x.startswith('skill/') or x.split('/')[-1] in ('check.py','user-note.txt','other-plan.md','project-setting.md')]
  entries.append(entry)
# Freeze holdout and resume inputs before any experimental actors run.
fixture(w/'holdout'/'parallel',True)
res=w/'holdout'/'resume';res.mkdir()
for p in (old/'resume').iterdir():
 if p.name in ('check.py','send.py','probe.py','unavailable.py','deliveries.txt','user-note.txt','other-plan.md','project-setting.md'): shutil.copy2(p,res/p.name)
for f in ('math_ops.py','tasks.md'): (res/f).write_text(original['resume/'+f])
save(here/'matrix.json',{'workspace':str(w),'runtime':runtime,'runs':entries,'holdout_baseline':{str(p.relative_to(w/'holdout')):h(p) for p in (w/'holdout').rglob('*') if p.is_file()},'holdout_confirmation_runs':['hconfirm_61_parallel','hconfirm_56_parallel','hconfirm_61_resume','hconfirm_56_resume'],'gates':'Fixed R3 gates in plan; O1-O8 evaluator calibration required before dispatch','outcome':'8 fixed runs, each two workers; B1 4/4 and baseline main failure without confound required for Go; no replacement or B2','created_before_dispatch':True})
save(here/'actors.json',[{k:x[k] for k in ('id','actor','model','version','state','task_attempt')} for x in entries])
print(w)
print(json.dumps(runtime,indent=2))
