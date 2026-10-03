# Run: receipt CLI

Scope / exclusions: Plan only. Implement a CLI that accepts a name and one or more integer amounts, then prints the name and sum. Do not change source code or run implementation checks in this planning pass. Preserve unrelated files.

Materials and Definition of Done: `app.py` currently contains only `total(values)`. Implementation is done when the CLI accepts valid input, rejects an empty name and invalid input with a nonzero exit status, and the checks below pass.

Authority: this `tasks.md`; coordinator: current planning agent. The prior A/B cycle and C's missing X dependency are replaced by one end-to-end task.

Workspace / baseline: `/private/tmp/task-harness-remediation-w5zjr1sb/plan`; no Git repository. At planning time, SHA-256: `app.py` 3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad; prior `tasks.md` c18dbdcb4e5dbcf61c6fe144281798d1e16bcd49c88cceb2d8cb4ba714f6fede.

Execution limits / permissions: This pass authorizes only updating `tasks.md` and, if needed, `evidence/`. No implementation, delegation, network, or installation. Future implementation requires a separate authorization. Python standard library and shell are available for the planned checks; no runtime checks have been run.

Assumptions: Use positional arguments `NAME AMOUNT [AMOUNT ...]`. Require at least one amount. An empty string is invalid; whitespace-only names are outside the stated restriction. Print one line as `NAME: TOTAL`. These choices make the otherwise unspecified invocation and format testable.

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | Implement and verify the receipt CLI in `app.py` | none | unassigned / none | pending |

## T1

Write scope / shared resources: `app.py` and one minimal runnable check if needed; preserve all other files. Reuse the existing `total(values)` function and Python standard library argument parsing.

Inputs and output location: Current `app.py`; CLI output on stdout, invalid-input diagnostics on stderr.

Acceptance: `python app.py 小明 10 20` prints exactly `小明: 30` and exits 0. `python app.py "" 10`, `python app.py 小明 abc`, and `python app.py 小明` each exit nonzero without printing a successful receipt. Integer amounts include zero and negative values; `python app.py 小明 -5 2` prints `小明: -3` and exits 0.

Verify: Run the valid and invalid CLI scenarios above and check exact stdout and exit status. Keep one small runnable regression check covering these cases with the implementation. Recheck against the final `app.py` fingerprint.

Attempt / last update: No implementation attempt; plan created 2026-10-02.

Evidence: Planning baseline only; no implementation command or test result claimed.

Blocker / next action: Await explicit authorization to implement; then confirm current files and execute T1.

## Checkpoint

Completed and accepted: Plan only; implementation has not started.

Active worker handles and last observed state: None.

Unresolved work, decisions, and next ready tasks: T1 is dependency-ready once implementation is authorized. Confirm assumptions about invocation and output if the user supplies a different contract.

Side effects attempted and receipt / unknown outcome: `tasks.md` updated in place. No external side effects.
