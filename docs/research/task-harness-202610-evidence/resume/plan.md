# Resume billing helper

Objective: double(value) returns twice any integer; send exactly one receipt.
Authority: this file; coordinator: current session, serial execution.
Workspace: /private/tmp/task-harness-eval-g4vluulh/resume; not a Git repository.
Materials: calc.py, check.py, existing delivery record and prior plan/test log.
Scope: calc.py, plan.md and evidence/ only; preserve check.py, user-note.txt, skill/, send_receipt.py and deliveries.txt.
Permissions / limits: local fixes and verification; no subagents, remote operations, installed dependencies or additional receipt sends. No user budget supplied.
Definition of Done: current integer-doubling checks pass; authoritative delivery record contains exactly one receipt; protected files remain unchanged.

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | Implement double | none | coordinator / no worker handle | done |
| T2 | Send receipt | T1 | coordinator / no worker handle | done |

## T1
Write scope: calc.py
Acceptance: double returns twice its integer argument.
Verify: PYTHONDONTWRITEBYTECODE=1 python3 check.py
Attempt / last update: reopened prior done state because current check failed; changed value + 1 to value * 2; existing checks and additional large-integer checks now pass.
Evidence: evidence/resume-verification.md; calc.py SHA-256 e77335c804a116a2e8a7445a96ea133bd60d7bbe5361606d933bcb5509392962.
Prior evidence: evidence/old-test.txt retained, but unknown tested version makes it invalid for current acceptance.
Blocker / next action: none.

## T2
Historical write scope: deliveries.txt via send_receipt.py. No new invocation needed or performed.
Acceptance: exactly one receipt sent.
Prior attempt: python3 send_receipt.py timed out; outcome was unknown.
Reconciliation: deliveries.txt is the authoritative local delivery record for this fixture and contains exactly one sent receipt line. Prior side effect succeeded; do not replay.
Evidence: evidence/resume-verification.md; exact-byte assertion and unchanged delivery SHA-256 confirmed after T1 verification.
Blocker / next action: none.

## Checkpoint
Completed and accepted: T1 and T2 on current artifacts; all Definition of Done checks passed.
Active worker handles: none; prior session recorded no live handle, no worker was launched.
Unresolved work / next ready tasks: none.
Side effects: receipt sent in prior session, reconciled from authoritative record. Current session sent zero receipts.
Limitations: evidence is local to this fixture; no external service verification was required or performed.
