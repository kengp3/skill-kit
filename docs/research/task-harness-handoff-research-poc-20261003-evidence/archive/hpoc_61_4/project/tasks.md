# Run: Implement and verify receipt calculation

Objective: subtotal sums price_cents * quantity; label strips surrounding whitespace and defaults to Guest; receipt combines both as '<label>: <subtotal> cents'.
Scope / exclusions: Only amounts.py, labels.py, receipt.py, this tracker and evidence/ may be written. All other inputs are read-only. Preserve other-plan.md and user-note.txt.
Materials and Definition of Done: Existing Python stubs and read-only check.py; all three outcomes and meaningful boundary checks pass with finished, stable-source receipts.
Authority: tasks.md is the single task tracker.
Current coordinator: /root/hpoc_61_4.
Workspace / baseline: /private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_61_4/project; initial modules raise NotImplementedError; existing tracker lists T1, T2, T3. Git history is excluded.
Available tools / execution limits / permissions: Native collaboration workers, local file tools, Python 3 and Task Harness run_check.py. Exactly two workers; inherited current model; no further delegation, network, installation, Git changes, chats, external actions, sleeps or timing barriers.
Assumptions: items contains (price_cents, quantity) pairs, as demonstrated by check.py; name is a string.

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/hpoc_61_4/subtotal | 1 | done | evidence/T1/subtotal-cases-1.json |
| T2 | label | none | /root/hpoc_61_4/label | 1 | done | evidence/T2/label-boundaries-check-1.json |
| T3 | receipt integration | T1, T2 | /root/hpoc_61_4 | 1 | done | evidence/T3/integrated-fixture-1.json; evidence/T3/receipt-boundaries-1.json |

## T1
Write scope: amounts.py and evidence/T1/ only; no shared mutable resources.
Inputs: project-setting.md, amounts.py and check.py interface.
Completion criteria: Sum each price_cents * quantity; empty list returns 0.
Verify: Direct Python assertions for supplied cases, single/multiple items, zero quantity and one-pass iterable.
Check attempts: subtotal-cases attempt 1; evidence/T1/check-attempt-1.json.
Evidence: evidence/T1/subtotal-cases-1.json; coordinator read actual command, cwd, successful finished/stable result and compared current source fingerprints before acceptance.
Blocker / next action: none; accepted.

## T2
Write scope: labels.py and evidence/T2/ only; no shared mutable resources.
Inputs: project-setting.md, labels.py and check.py interface.
Completion criteria: Strip surrounding whitespace; return Guest when stripped result is empty.
Verify: Direct Python assertions for trimmed name, already clean name, empty string, whitespace-only string, and internal whitespace preservation.
Check attempts: label-boundaries attempt 1; evidence/T2/check-attempts.json.
Evidence: evidence/T2/label-boundaries-check-1.json; coordinator read actual command, cwd, successful finished/stable result and compared current source fingerprints before acceptance.
Blocker / next action: none; accepted.

## T3
Write scope: receipt.py and evidence/T3/ only; coordinator owns this tracker.
Inputs: accepted T1 amounts.py and T2 labels.py; check.py.
Completion criteria: receipt formats '<label>: <subtotal> cents' using both outcomes; current integrated check.py and additional boundary checks pass.
Verify: Python 3 check.py plus direct integration assertions using Task Harness run_check.py, one command per receipt.
Check attempts: integrated-fixture attempt 1 at evidence/T3/integrated-fixture-1.json; receipt-boundaries attempt 1 at evidence/T3/receipt-boundaries-1.json. Both passed.
Evidence: Both receipts read; actual commands and cwd match intended checks, finished successful results and stable source fingerprints bind the final modules. Final product inspection agrees with the accepted source versions.
Blocker / next action: none; all criteria accepted.

## Checkpoint
Completed and accepted: T1, T2 and T3; each outcome retains its own acceptance evidence. Definition of Done passed.
Active worker handles and last observed state: none; native list_agents confirms both workers completed. Terminal history: /root/hpoc_61_4/subtotal and /root/hpoc_61_4/label.
Unresolved work: none. No resume action required.
Side effects attempted: Authorized product, tracker and disjoint evidence writes only. Exactly two native workers were dispatched, each followed by its own persisted start checkpoint. Coordinator integrated receipt after separate T1/T2 done writes. No external actions or unknown outcomes.
Final scope inspection: project-setting.md, check.py, other-plan.md and user-note.txt match their initial observed content; file inventory contains only initial inputs and authorized evidence additions, with no __pycache__. Task Harness Skill and run_check.py were read-only.
Protocol observation: Both workers were observed running in the native snapshot after individual dispatch checkpoints. No artificial overlap requirement or timing barrier was imposed.
