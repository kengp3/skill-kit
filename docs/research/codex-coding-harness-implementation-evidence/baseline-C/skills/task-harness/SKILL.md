---
name: task-harness
description: Deliver bug fixes, features, and refactors in existing projects using risk-based verification, direct evidence, and progress-based recovery. Use for implementation, multi-step coordination, or resuming interrupted coding work. Planning alone does not authorize implementation.
---

# Coding Harness

Own the requested outcome through verified delivery. Use the host's tools and the project's existing rules. Match the user's language.

## Establish the contract

1. Identify planning, execution, or resume and the authorized scope. Read project instructions, affected code, callers, current changes and available checks. Preserve unrelated work.
2. Reuse the approved brief and spec. If material requirements are missing, use [define-task](../define-task/SKILL.md). Ask only the unresolved question that changes the result; continue independent work.
3. Before implementation, state concrete expected behavior and its source, verification, relevant risks and allowed side effects. Check that acceptance expectations represent the requirement rather than copying the existing implementation. Inspect uncertain or high-risk expectations against independent evidence.
4. Confirm minimum execution and observation: working directory, available runtime/check commands, final result retrieval and source attribution. Record actual permissions and limits; unknown budgets stay unknown. A missing necessary capability blocks its dependent operation.

## Choose the smallest verifiable slice

- Small work stays one complete change. Medium and large work proceeds through observable behavior slices, with explicit dependencies and final integration verification.
- Keep one owner. Delegate only for a clear parallel benefit or independent review, within host authorization. Assign inputs, product/evidence ownership, output and acceptance; preserve other workers' edits.
- Before parallel writes, isolate files and mutable resources such as databases, ports and generated output. Check previous worker liveness before replacement; elapsed time does not prove a worker stopped.
- Use the existing tracker when coordination needs it. A simple task needs no new task document, role, checkpoint or receipt for each read. Persist only what later continuation requires.

## Implement and verify

1. Trace the affected flow and select verification by impact and risk. Explain the choice briefly. A local fix may need one regression check; shared contracts need consumer/integration coverage; permissions, money, migration, public compatibility or poorly verified core behavior trigger independent review. These examples do not exclude other material risks.
2. Establish behavior and acceptance before choosing test-first or another suitable approach. Run relevant baseline checks before modifying affected behavior; distinguish existing failures and environment faults from regressions. If a baseline is unavailable, retain that limitation. For a bug, reproduce the target failure where practical. Features test intended behavior; refactors preserve agreed behavior. A checker defect is diagnosed separately from a product defect.
3. Implement the smallest complete slice. Reuse project commands, tests and native controls. Mechanize reliable, necessary conditions at the existing boundary; add a tool or hook only for a demonstrated gap.
4. Inspect actual changes and run the chosen checks. Read the inner check's final result, not just the orchestration success or a running-session response. Review the integrated product; slice success alone is insufficient.
5. With new diagnostic evidence or a testable hypothesis, repair within scope autonomously. When repeated failure yields no progress, change strategy or report the concrete blocker. Respect real limits; do not weaken acceptance to pass.
6. When independent review is triggered, give the reviewer requirements, current artifacts and original evidence. Use the internal review mode of [ai-code-review](../ai-code-review/SKILL.md). Findings need a reachable trigger, impact and evidence. Review approval does not replace necessary checks.

## Controls and evidence

Use native permissions, sandbox and project gates first. For each necessary control identify its condition, enforcement point, covered tool paths and failure behavior before the dependent operation. A reminder is advisory. A post-operation check cannot replace a required pre-operation control. An untrusted, failed or uncovered hook provides no enforcement guarantee. Stop the dependent operation until control is repaired or a verified equivalent exists; continue unrelated safe work.

Prefer retrievable native inputs/results with cwd, relevant output, final status and source identity including dirty content. Retain a resolvable reference; a summary is not original evidence. Reopen affected acceptance after source changes. Missing or stale evidence means unverified, not complete.

If native evidence cannot retain a small noninteractive process check, Python 3 users may use [run_check.py](scripts/run_check.py):

```sh
python3 <skill-dir>/scripts/run_check.py --output <new-receipt.json> --source <source> --source <test> -- <checker> <args>
```

It records argv, cwd, separated output and before/after fingerprints. It has no timeout or durable process tracking; use the host for long-lived processes. Read the receipt and helper exit status. An existing receipt must be reconciled before another attempt. The helper is optional and does not install runtimes or prove that acceptance criteria are correct.

## Unknown outcomes and continuation

Keep operation result separate from task progress and worker liveness:

| Result | Next action |
| --- | --- |
| Confirmed complete | Inspect resulting artifact and current evidence, then continue |
| Confirmed failed or not started | Diagnose and repair or safely retry within scope |
| Unknown | Query actual state, original result, operation ID or idempotency support before deciding whether replay is safe |

Timeout, disconnect or cancellation does not prove a mutation did not happen. If duplicate effects cannot be excluded, stop dependent operations. Respect cancellation; confirm prior writers stopped before assigning overlapping work.

For cross-session or dependent continuation, use host persistence first. Retain goal, scope, decisions, completed/pending work, evidence references, blockers, active worker handles and unknown side effects. On resume, reconcile artifacts, versions, permissions and liveness against current truth. A failed auxiliary statistic can be disclosed and skipped; missing necessary control or evidence cannot.

## Deliver

Map acceptance to current results and evidence; explain verification choices, remaining risks and blockers. Planning delivers a plan and stops. An assessment can conclude failure; a repair is complete only after applicable acceptance passes. Do not claim success from agent statements, wrappers or old checkpoints.

Measure improvement by total human active time, including clarification, review, manual verification, rescue, recordkeeping and later rework; interruptions are secondary. Label measured, estimated and unavailable values. Keep unfinished outcomes and costs visible. Configuration/maintenance costs and agent waiting time are separate. Do not claim savings before comparable delivery quality and observation are available.
