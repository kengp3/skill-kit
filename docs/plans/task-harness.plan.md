# Task Harness 建立計畫

權威任務清單：本文件。規格：[task-harness.spec.md](../specs/task-harness.spec.md)。

| ID | 成果 | 依賴 | Owner | 狀態 |
| --- | --- | --- | --- | --- |
| H1 | 截至 2026-10-02 的研究與設計取捨 | 無 | 主 agent | done |
| H2 | 可獨立使用的 task-harness skill | H1 | 主 agent | done |
| H3 | 隔離情境的獨立行為驗證 | H2 | eval_plan、eval_execute、eval_resume；主 agent 驗收 | done |
| H4 | 修正、格式檢查與交付 | H3 | 主 agent | done |

## H1

範圍：`docs/research/task-harness-202610.research.md`。
驗收：六項研究問題皆有一手依據或明示推論；交代資料時間、相反案例及證據限制。
證據：報告逐項引用已開啟的一手頁面；research validator 已通過。

## H2

範圍：`skills/task-harness/`、README 技能索引。
驗收：覆蓋規劃、分派、執行、驗收、續作；無必需外部 skill 或新增 dependency。
驗證：已讀回整份 skill、官方 validator 通過；三份隔離 SKILL.md 複本 SHA-256 均與本次 source 相符。具體命令與指紋將保留於 H4 驗證報告。

## H3

範圍：`/private/tmp/` 的隔離 fixtures；結果保存在研究驗證文件。
驗收：規劃不執行、實際執行留證據、resume 不盲信既有 done 或重送未知副作用；包含授權的 subagent 分派。
驗證：使用 skill-creator 的 independent forward-testing；測試 agent 不接收作者預期答案。
結果：三個情境均已完成；主 agent 重跑保留快照的 verify.py 與 extended integration checks，皆 exit 0。實際分派使用一名 worker，未測多 writer 壓力。

## H4

範圍：本次新增檔案、必要修正與 `docs/research/task-harness-validation-202610.research.md`。
驗收：修正已觀察問題，重驗受影響情境，格式通過，交付明示未測界線。
限制：測試通過只代表此次 fixtures，不是長期成功率或所有 runtime 的保證。
證據：[驗證報告](../research/task-harness-validation-202610.research.md)；skill 與兩份 research validators 通過，連結與受測版本指紋相符。沒有修改受測 skill 的行為、沒有新增 runtime dependency；無 commit、push、全域安裝或發布。
