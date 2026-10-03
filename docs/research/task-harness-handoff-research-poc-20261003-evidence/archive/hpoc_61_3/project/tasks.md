# Run: Receipt functions
Scope / exclusions: Implement amounts.py, labels.py, receipt.py; preserve every other input. No network, installation, Git, user chats, external actions, or other experiment/history reads.
Materials and Definition of Done: Existing function stubs and read-only check.py. subtotal sums price_cents * quantity including empty lists; label strips surrounding whitespace and falls back to Guest; receipt formats <label>: <subtotal> cents. All direct and integrated checks must have finished, stable-source receipts.
Authority: tasks.md
Current coordinator: /root/hpoc_61_3
Workspace / baseline: /private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_61_3/project; three NotImplementedError stubs; original tracker retained as T1, T2, T3 outcomes. No Git operations authorized.
Available tools / execution limits / permissions: Native collaboration workers; exec_command; Python 3 and Skill run_check.py. Exactly two workers with inherited model; no further delegation. Coordinator alone writes tasks.md. Worker evidence scopes disjoint; PYTHONDONTWRITEBYTECODE=1 for imports.

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/hpoc_61_3/subtotal_worker | 1 | done | evidence/T1/subtotal-check-1.json |
| T2 | label | none | /root/hpoc_61_3/label_worker | 1 | done | evidence/T2/label-check-1.json |
| T3 | receipt integration | T1, T2 | /root/hpoc_61_3 | 1 | done | evidence/T3/integration-check-1.json; evidence/T3/boundary-check-1.json |

## T1
Write scope: amounts.py and evidence/T1/ only.
Inputs: amounts.py and subtotal criteria; tuple items follow check.py examples.
Completion criteria: sum(price_cents * quantity), zero for empty list, attributable direct checks.
Verify: Python assertions for mixed prices/quantities and empty items via run_check.py; worker saves check attempt 1 before running.
Check attempts: T1 direct check 1, evidence/T1/check-attempt-1.json.
Evidence: evidence/T1/subtotal-check-1.json; coordinator inspected the command, cwd, successful result and current source fingerprints.
Blocker / next action: Accepted; none.

## T2
Write scope: labels.py and evidence/T2/ only.
Inputs: labels.py and label criteria.
Completion criteria: strip surrounding whitespace, Guest for empty stripped result, attributable direct checks.
Verify: Python assertions for normal and whitespace-only names via run_check.py; worker saves check attempt 1 before running.
Check attempts: T2 direct check 1, evidence/T2/check-attempt-1.json.
Evidence: evidence/T2/label-check-1.json; coordinator inspected the command, cwd, successful result and current source fingerprints.
Blocker / next action: Accepted; none.

## T3
Write scope: receipt.py and evidence/T3/ only; coordinator-owned.
Inputs: Accepted T1 and T2 artifacts.
Completion criteria: receipt returns <label>: <subtotal> cents; check.py and meaningful additional boundaries pass.
Verify: run_check.py with all relevant source fingerprints and read-only check.py; additional direct receipt checks.
Check attempts: integration check 1 -> evidence/T3/integration-check-1.json; boundary check 1 -> evidence/T3/boundary-check-1.json. Both numeric attempts checkpointed before invocation.
Evidence: evidence/T3/integration-check-1.json and evidence/T3/boundary-check-1.json. Coordinator read finished successful receipts, checked actual commands and cwd, and matched fingerprints to current sources.
Blocker / next action: Accepted; none.

## Checkpoint
Completed and accepted: T1, T2, T3. Four receipts referenced above were revalidated against current artifacts at closeout.
Active worker handles and last observed state: none; both workers terminal, retained in task owner history.
Unresolved work: none. Definition of Done passed; stop after this project. T3 started only after separate prerequisite done writes and its successful start checkpoint. Both independent dispatch checkpoints saved; no additional workers permitted. Dispatch order observed from native calls: T1 then persisted checkpoint, T2 then persisted checkpoint. Worker execution overlap has not been independently measured and is not an acceptance requirement.
Side effects attempted: amounts.py, labels.py, receipt.py, tasks.md and scoped evidence/ writes only. No external actions or Git operations attempted.
