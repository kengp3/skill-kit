# Task Harness 並行驗收修訂與既有 trace 判讀

日期：2026-10-03（Asia/Taipei）。範圍：修訂並行 protocol 與判定邊界，重新檢視既有兩模型 trace；沒有執行新的模型案例。本次結果不代表修改後 Skill 已完成新的雙模型行為測試。

## 結論與契約

並行派工的 blocking gate 是：本輪選定、已 ready、互不衝突且符合授權及可用容量的任務，逐一 dispatch 並保存各自 checkpoint，派完前不得主動等待、收集／驗收結果或插入無關工作。若 readiness、容量或安全條件改變，需記錄縮減或停止原因並處理失敗。保留逐次 checkpoint，不改成多次派工後一次補寫。

自然完成通知與 worker 提早完成不構成違規。執行區間是否重疊、派工間隔屬獨立觀測；不能以 `last dispatch < first completion` 當通用必要條件，也不能從零重疊直接推論 coordinator 主動等待或 scheduler 序列化。使用者明確要求實際重疊時，仍需另驗收此成果，不以本修訂免除。不得用人工等待製造重疊。

權威現行規則：[Skill](../../skills/task-harness/SKILL.md)、[規格](../specs/task-harness.spec.md)。本次不新增 scheduler、runtime helper 或新 timestamp 欄位；現有 native trace 已能提供派工時間。

## 證據與重新判讀

來源：[6.1 coordinator](task-harness-revalidation-20261003-evidence/native-traces/reval03_61_parallel.json)、[5.6 coordinator](task-harness-revalidation-20261003-evidence/native-traces/reval03_56_parallel.json)、[worker lifecycle](task-harness-revalidation-20261003-evidence/parallel-overlap.json)。以下行號為匯出事件的 `source_line`，不是 JSON 檔案行號。時間均轉為臺北時間 2026-10-03。

| 事件 | 6.1 Sol | 5.6 Sol |
| --- | --- | --- |
| dispatch A | 00:32:31.895（30） | 00:32:55.707（48） |
| A checkpoint 成功 | 00:32:38.374（39） | 00:33:00.818（59） |
| dispatch B | 00:33:36.802（42） | 00:33:08.788（61） |
| B checkpoint 呼叫／成功 | 00:33:52.052／52.204（50／53） | 00:33:14.664／14.763（69／72） |
| 首次 wait_agent | 00:34:03.923（60） | 00:33:21.381（83） |
| 實際 overlap | 無；A 結束到 B 開始相隔約 29.007 秒 | 約 22.002 秒 |

兩個 coordinator 的第一次至第二次 dispatch 之間，各只有 A 的 checkpoint 工具呼叫及成功回覆，沒有主動 wait、收集／驗收或其他工作。6.1 的 B checkpoint 與 A receipt 讀取在同一 shell invocation 內，但 checkpoint 寫入位於讀取之前，且兩名 workers 已派出。5.6 在 B checkpoint 成功後才讀 runner 並 wait。因此，依修訂後的 **dispatch-order gate，兩者既有 trace 均通過**；這只判定派工順序，不包含 checkpoint 欄位完整性或 acceptance provenance。

6.1 的 A checkpoint 回覆到 B dispatch 間隔 58.428 秒，A 在 00:33:07.844 已完成。這可解釋本次沒有執行重疊，但間隔的根因仍未確定；沒有據此認定模型能力不足、刻意等待或 scheduler 故障。

## 歷史結果及其餘問題

保留原始 [test contract](task-harness-revalidation-20261003-evidence/test-contract.json)、[findings](task-harness-revalidation-20261003-evidence/findings.json) 與[報告](task-harness-revalidation-20261003.research.md)，不將當時 `REVAL-PAR-61` 的 `observed_failure` 改寫成歷史通過。零重疊觀察仍成立；在新契約下分類為 runtime-overlap 觀測，不能單獨阻塞 dispatch correctness。

`REVAL-ATTEMPT-56` 與 `REVAL-HANDOFF-56` 維持未修正；派工順序通過不關閉這兩項。未因契約調整重啟已結案的 remediation、建立 attempt6 或重跑八案例。

## 驗證與限制

本次驗證包含官方 Skill validator、兩份既有 coordinator 工具序列的直接檢視，以及檔案變更範圍核對。沒有新執行程式邏輯；`run_check.py` 與 UI metadata 維持原樣。既有 trace 是舊 candidate 的執行證據，只能依新契約重新判讀，不能用作修改後 candidate 的新行為證據。

官方 validator 實際命令（專案根目錄執行；使用既有 PyYAML，未安裝套件）：

```sh
PYTHONPATH=/private/tmp/cathay-login-uv-cache/archive-v0/WoB8JVx6xRoQMAty/lib/python3.13/site-packages python3 /Users/kengp3/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-harness
```

結果：exit 0，`Skill is valid!`（工具 chunk `8e9a39`）。修改後 SKILL.md SHA-256：`3635695f1cf027aa5c362b8379fe10ed4726d85ac7789243daab7028f742b732`。這是新版本，不冒用先前八案例的 candidate hash。

變更核對：兩個既有檔案（SKILL.md、規格）修改，新增本報告；其餘 2,141 個既有檔案 hash 保持一致，包括歷史 evidence、runner、UI metadata 及無關工作。三個交付檔案的相對連結均可解析。
