# 文件規範

| 類型 | 文件用途 | 目的地與檔名 |
| --- | --- | --- |
| research | 證據 | docs/research/{slug}.research.md |
| task-contract | 合約 | docs/plans/{slug}.task-contract.md |
| hook-receipt | 收據 | docs/research/{slug}.hook-receipt.md |

## Task Harness

| 設定項目 | 值 |
| --- | --- |
| schema_version | 1 |
| model.default | [gpt-6.1-sol;low] |
| model.stage.研究 | [gpt-6-sol;medium] |
| model.role.analyst | [gpt-6.1-sol;high] |
