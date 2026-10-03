# T3 assessment: native evidence completeness

## Question

Can native evidence be marked as passing when it lacks either an attributable source/artifact version or the checked command's final exit status?

## Basis

The controlling rules are `skill/SKILL.md`, especially **Check and retain receipts**, **Accept the tested version**, and **Recover without replaying blindly**:

- acceptance must bind the result to the actual artifact version, including relevant dirty content;
- acceptance must use the individual checked command's final exit status;
- running, missing, or unknown results are not passes;
- successful file readback, output text such as `PASS`, or another low-level command's success cannot substitute for the required evidence;
- missing required verification keeps acceptance `verifying` or `blocked`.

## Verdicts and affected states

| Assessed evidence condition | May the assessed object be marked passed? | Reason | Affected acceptance state |
| --- | --- | --- | --- |
| Attributable source/artifact version is missing | **No** | The result cannot be tied to the artifact currently being accepted. A readable receipt or successful command does not establish that the tested bytes are the current bytes. | `verifying` while a safe version observation can still be obtained; `blocked` when the required capability/input/permission is unavailable. Never `done` solely from this incomplete evidence. |
| Individual checked command's final exit status is missing | **No** | Output text and orchestration/readback success do not establish the checked process outcome. A running, absent, or unknown final result is not a pass. | `verifying` while the original operation can be reconciled; `blocked` when its outcome cannot be recovered safely. Do not replay an unknown consequential side effect merely to fill the receipt. |
| Either required field is missing, even if a file read succeeds or a fingerprint/readback helper exits 0 | **No** | That low-level success proves only the low-level operation, not the subject criterion or the overall Task Harness workflow. | The affected subject acceptance remains `verifying` or `blocked` as above. |

## Separate decisions

- **T3 assessment task completion:** may be `done` after this artifact is read back and confirmed to contain supported verdicts for both cases. A negative verdict is a valid completed assessment.
- **Assessed incomplete evidence:** **FAIL / not acceptable as a pass** in both cases.
- **Overall run or Skill pass:** not established by T3 completion, by reading this file successfully, or by any low-level tool exit 0. Current overall state must continue to reflect every task, including T1's changed input version and T2's synthetic unknown side effect.

## Application to this resume

`evidence/T1-resume-version-1.md` shows that current `inputs/prices.txt` is stable during readback but differs from the version bound to `evidence/T1-check-1.md`. Therefore the old C1 evidence is not applicable to the current input. Its historical negative verdict remains attributable only to the old version; it cannot accept or reject the changed current version without new subject-check evidence. The explicit prohibition on rerunning C1 leaves current T1 acceptance `blocked`, not passed.
