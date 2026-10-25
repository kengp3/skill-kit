# Task Harness settings migration reconciliation

This is migration evidence, not project settings, a task contract, a hook receipt, or a long-term state table. The confirmed project root is `/private/tmp/unified-t03-conflict/project`. The historical completed contract is no longer active; no active-contract takeover is attempted.

## Sources and scope

Read the actual root `project-setting.md` and `harness-project.json`, the loaded project-setting skill and its configuration instructions, and task-harness `references/project-settings.md` and `references/settings-migration.md`. The supplied provider specification supports the new Markdown schema version 1. This authorized one-time migration may delete the legacy settings only after all three provider gates pass, without a backup. No settings were merged because the reconciliation has an unresolved path conflict.

## Item reconciliation

All legacy keys and original JSON types/values are listed below. The legacy file is a readable regular file; visual inspection found complete JSON and no duplicate keys. No parser or external validator was run.

| Legacy item | Original type and value | Disposition |
| --- | --- | --- |
| schema_version | number: `1` | Recognized legacy version. Root Markdown has one Task Harness section and one `schema_version` row with value `1`; the same number does not make the two storage formats equivalent. |
| project_root | string: `/private/tmp/unified-t03-conflict/project` | Absolute and matches the confirmed project and legacy-file location. Do not copy into the new settings table. |
| contract_dir | string: `docs/plans/harness` | Existing safe project-relative directory. Historical `docs/plans/harness/legacy-done.md` exists. Intended legacy mapping would preserve `docs/plans/harness/{filename}`, but conflicts with the current task-contract declaration `docs/other-contracts/{filename}`. Neither is selected. |
| receipt_dir | string: `docs/research/receipts` | Existing safe project-relative directory. Existing hook-receipt declaration has `docs/research/receipts/{filename}`. Preserve original `turn-1.jsonl` filename and extension. |
| host | object containing the following three boolean properties | Historical container only; no new host or eligibility setting is created. |
| host.session_identity | boolean: `true` | Historical qualification claim sourced from `harness-project.json`; not evidence of current host capability or a passed new-flow flag. |
| host.user_turn_identity | boolean: `true` | Historical qualification claim sourced from `harness-project.json`; not evidence of current host capability or a passed new-flow flag. |
| host.stop_continuation | boolean: `true` | Historical qualification claim sourced from `harness-project.json`; not evidence of current host capability or a passed new-flow flag. |

No unknown legacy keys or unknown host entries were observed. No model settings are present; none are invented or inferred.

## Conflict and validation findings

The root Markdown declares task-contract at `docs/other-contracts/{filename}`, while legacy settings specify `docs/plans/harness`. The latter contains the historical contract; the former directory is absent. Both declarations and their source files remain unchanged. User direction is required to resolve which permanent classification applies; this evidence does not choose a path or move historical artifacts.

The task-contract and hook-receipt lines are also detached from the main Markdown classification table, appearing after prose without a table header. They cannot be treated as successfully validated classification rows. Repair is deferred with the unresolved path conflict; no duplicate rows or replacement configuration were added.

The main research classification is unambiguous: `docs/research/{slug}.research.md`. Before creating this record, the project root, `docs`, `docs/research`, settings files, and historical artifact parent directories were inspected as ordinary directories/files, without symlinks along the confirmed in-project paths. This destination was absent, including as a symlink, so no existing document was overwritten. Legacy contract and receipt directories are distinct and neither contains the other.

## Deletion gates and result

1. Successful write without omissions: **not passed**. Every observed old value is reconciled here, but no settings merge is justified while the contract-path conflict remains unresolved.
2. Valid format and contents: **not passed**. The necessary classification rows are detached from the table and the contract mapping conflicts. The observed Task Harness schema row alone is insufficient.
3. Target-version normal readback: **not passed**. The loaded provider specification supports the new format, but no valid reconciled settings have been loaded through normal startup to locate the same contract/artifacts. Reading source text is not this gate.

Therefore `harness-project.json` must remain. The root settings, historical contract `docs/plans/harness/legacy-done.md`, and historical receipt `docs/research/receipts/turn-1.jsonl` are preserved. No new contract, hook receipt, backup, empty destination directory, platform hook, model setting, product change, or runtime helper was created. Host trust/loading, live hook availability, provider normal startup, and product acceptance are not established by this reconciliation.

This record and the actual settings and historical artifacts were read back after writing; final file reads, rather than proposed text, are the handoff evidence. The migration remains incomplete pending explicit conflict resolution and all three deletion gates.
