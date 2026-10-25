# Task Harness settings migration reconciliation

This is migration evidence, not active settings, a task contract, or a hook receipt. Confirmed project root: `/private/tmp/unified-t03-positive/project`. Sources read before changes: root `project-setting.md`, root `harness-project.json`, and the installed task-harness specifications `references/project-settings.md` and `references/settings-migration.md`.

## Field-by-field reconciliation before settings changes

| Legacy field | Raw value and type | Disposition |
| --- | --- | --- |
| schema_version | `1` (number) | Recognized legacy version; new Markdown Task Harness table uses `schema_version` value `1`. |
| project_root | `/private/tmp/unified-t03-positive/project` (string) | Absolute path equals the confirmed physical project root and the legacy file's project; no duplicate root setting is added. |
| contract_dir | `docs/plans/harness` (string) | Add task-contract category destination `docs/plans/harness/{filename}`; retain complete original filenames. |
| receipt_dir | `docs/research/receipts` (string) | Add hook-receipt category destination `docs/research/receipts/{filename}`; retain complete original filenames and extensions. |
| host | Object containing exactly the following three boolean fields | Historical environment information only; no active host settings are added. |
| host.session_identity | `true` (boolean), root harness-project.json | Historical source value only; not evidence of current host capability or qualification. |
| host.user_turn_identity | `true` (boolean), root harness-project.json | Historical source value only; not evidence of current host capability or qualification. |
| host.stop_continuation | `true` (boolean), root harness-project.json | Historical source value only; not evidence of current host capability or qualification. |

The entire legacy file was read as data. There are no duplicate JSON keys, unknown fields, missing required fields, ambiguous types, or unresolved conflicts. Existing project-setting.md has five category rows, no task-contract or hook-receipt row, and no Task Harness section or model preference. The existing text and rows will be preserved.

## Paths and existing artifacts

The root and destination parent directories are actual directories; root settings and legacy settings are regular files. No project symlinks or applicable nested AGENTS.md/CLAUDE.md were found. Both legacy directories already exist, are distinct, neither contains the other, and are relative project paths without `..` or internal/third-party locations. They do not resolve to the same artifact.

Read existing regular artifacts in place:

- `docs/plans/harness/legacy-done.md`: `# Historical completed contract`, blank line, `Kept at its original location.`
- `docs/research/receipts/turn-1.jsonl`: `{"fixture":"historical-receipt-keep"}`

Neither artifact will be edited, moved, copied, or renamed. No new contract, receipt, empty directory, model default, hook, or product change is needed for this settings-only task.

## Migration status

Reconciliation was saved before modifying settings. Next: minimally merge the two category rows and the unique Task Harness table, read the actual file back, and return it to task-harness for validation. Keep harness-project.json until all three required deletion gates have explicit evidence, including task-harness normal startup readback. No settings backup will be created.

Settings write/readback completed: both categories were added at the reconciled original directories, with one `## Task Harness` section and one `設定項目 | 值` table containing only `schema_version | 1`. Five original categories and all original instructions remain. No model or host setting was added. Root legacy settings and both original artifacts were reread and remain unchanged. Gate 1 (complete write and reconciliation) is evidenced; provider checks for gates 2 and 3 are pending. Legacy deletion has not occurred.

## Provider validation and final deletion

The parent task-harness independently reread the actual disk settings and both historical artifacts through its normal startup flow and explicitly confirmed all three gates:

1. All typed legacy fields are mapped or preserved as history; unrelated content and original artifacts remain intact; no unknown field or conflict exists.
2. Exactly two required classification rows, one Task Harness section/table, and schema_version 1 are valid; no candidate rows require validation. The actual directory paths are safe and distinct.
3. The actually loaded installed task-harness Markdown specification supports this format. Normal root project-setting.md readback resolved and reread the same `docs/plans/harness/legacy-done.md` and `docs/research/receipts/turn-1.jsonl` with unchanged contents. The historical completed contract is not an active contract and was not rewritten.

Following that explicit confirmation, project-setting is authorized to delete only the same-root legacy harness-project.json without a backup. Host trust, hook loading and present environment qualification remain unverified and outside this migration's scope.

Final observed outcome: deletion succeeded; explicit existence and symlink checks confirm root harness-project.json is absent. Actual project-setting.md was reread after deletion and retains the reconciled categories and schema_version 1. Both original artifacts were reread after deletion with exactly their original contents. No backup or replacement legacy file was made. The earlier pending status above records the sequence before provider validation; this final section supersedes that status. Migration completed.
