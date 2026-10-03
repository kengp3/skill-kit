# Task Harness 修正與重測

日期：2026-10-02。狀態：**修正、重測與獨立複核完成；四項既有 findings 在本輪驗證範圍內 closed。**

## 結果與變更

受測版本已處理 OBS-01、GAP-01、GAP-02、GAP-03。Skill 本體只改兩段：plan-only 仍須保留最低交接資訊；每項驗收條件須對應具體檢查，包含相關錯誤與邊界輸入。沒有把 receipt 範例的姓名規則寫成通用要求。

Skill 仍只有 `SKILL.md` 與原有 `agents/openai.yaml`，沒有新增 runtime dependency。原生派工、觀測與 evidence 匯出都在驗證工作內，未加入正常使用流程。未安裝、commit、push 或發布。

- [最終 skill](../../skills/task-harness/SKILL.md)
- [權威任務清單](../plans/task-harness-remediation.plan.md)
- [修改前內容](task-harness-remediation-202610-evidence/SKILL.before.md)
- [原始請求與驗收範圍](task-harness-remediation-202610-evidence/requests-and-criteria.json)

## 逐項證據

| ID | 本輪判定 | 直接證據與限制 |
| --- | --- | --- |
| OBS-01 | closed | Fresh [plan/tasks.md](task-harness-remediation-202610-evidence/plan/tasks.md) 保留 coordinator、實際根目錄、app.py／草案指紋、工具與權限。實作 owner 仍 unassigned，狀態 pending；原始 app.py 與保護檔案不變。 |
| GAP-03 | closed | 同一計畫明列 `python app.py "" 10` 須非零退出且不輸出成功收據，也列出非整數與缺少金額情境。這次請求明確包含非空姓名，評分更直接；不將單次結果宣稱為漏項機率的統計改善。 |
| GAP-01 | closed（生命週期重疊） | 原生 `list_agents` 呼叫 `call_au3X7UdEuNsXUBAQ0b4Gxdke` 在 10:32:00 UTC 同時回傳兩名 helper 為 running。見 [coordinator trace](task-harness-remediation-202610-evidence/native-traces/remediation_parallel.json) 與 [快照](task-harness-remediation-202610-evidence/parallel/evidence/overlap.json)。沒有使用同步 barrier；不代表同時使用 CPU/GPU，也不代表效能提升。 |
| GAP-02 | closed（受測 agents 的工具事件範圍） | Coordinator 與兩名 worker 的所有 tool calls/results 均已保存，actor 由原生 session_meta 對應。四次 tasks.md 寫入具 call/result、時間及前後內容，均由 coordinator 執行；兩 worker 的來源碼修改各限 amounts.py、labels.py。見 [逐次寫入索引](task-harness-remediation-202610-evidence/state-audit.json) 及 [原生 trace 清單](task-harness-remediation-202610-evidence/native-traces/manifest.json)。不宣稱 OS 層級排除所有其他程序。 |

判定針對本輪 fresh fixtures，不回填舊測試缺失的證據，也不把舊報告改成通過。

## 狀態與整合驗證

Parallel coordinator 的 task-list 寫入順序如下。每次寫入均有原生 call/result 和完整讀回；前次讀回作為下次 preimage，中間全部工具動作均可查驗。

| UTC | tasks.md 寫入後 T1 / T2 / T3 | 原生 call_id |
| --- | --- | --- |
| 10:31:33 | pending / pending / pending | `call_WiYDGMaOrXTw6G86pCVlBTHx` |
| 10:32:24 | running / running / pending | `call_TySoEl9gIYYZcG86W7rYmSM4` |
| 10:33:14 | done / done / running | `call_GrXAVOBzk0BoLfuI4iBGOB5r` |
| 10:33:57 | done / done / done | `call_hwY8tnnlGpZCjiWjEgb2J0vE` |

T1/T2 在 coordinator 的直接 assertions 通過後才標 done，之後才實作 T3。最終 `check.py` 通過後才將 T3 標 done，沒有以成功訊息代替驗收。沒有另存短暫 verifying 狀態；直接檢查的發生順序仍可由 trace 確認。

續作案例重新檢查來源碼，辨識舊 done 的 `value+1` 已不符合 double 契約，修復後 `check.py` 通過。未知 send 沒有重播；缺 `deployctl` 保持 blocked；安全暫時錯誤在檢查 counter 後重試一次成功，持續錯誤重試一次後停止。最終 T1/T4 done、T2/T3/T5 blocked，正確保留整體未完成狀態。這些 blocked 是 fixture 的預設驗收情境，不是本次修正尚未完成的工作。

## 驗證紀錄

- 官方 `quick_validate.py`：`Skill is valid!`，exit 0；[紀錄](task-harness-remediation-202610-evidence/official-checks.json)。
- 沿用舊 verifier，fresh archived fixtures 上的整合、修復後 math、保護檔案、兩個 retry counters、skill 指紋全部通過；[verification.json](task-harness-remediation-202610-evidence/verification.json)。重播只執行無副作用的 check.py，沒有再執行 send/probe/unavailable。
- [export_traces.py](task-harness-remediation-202610-evidence/export_traces.py) 只匯出指定五名 actor 的原生工具資料；完整 call/result 正例、缺結果負例、無關 actor 排除檢查通過。它不自動判斷任務正確性，人工索引也不充當原始 log。
- [preservation.json](task-harness-remediation-202610-evidence/preservation.json)：134 份歷史檔案雜湊一致，現行 skill 與受測副本一致，metadata 不變。
- Fresh behavioral evaluators 指定 `gpt-6-sol`；獨立複核指定 `gpt-6-astra`。評估者僅取得真實任務、skill 與原始 fixture，未取得作者預期答案。Parallel 測試額外指定可觀測寫入方法，因此 writer 結論限於該受控案例。

最終 `SKILL.md` SHA-256：`948713f0c0720334b7c4ab355a78c11c162a4a14a19b683289a37e14abeec5be`。

`agents/openai.yaml` SHA-256：`76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310`。

## 執行中額外錯誤

保留三次、兩種類型的工具使用錯誤及實際恢復呼叫：parallel 第一次 JS 結果輸出式語法錯誤；plan 與 resume 各一次 patch 同時 Delete/Add 同一路徑被拒絕。前者修正語法後重跑唯讀檢查，後兩者改為 Update File，沒有重播服務操作。詳見 [incidental-errors.json](task-harness-remediation-202610-evidence/incidental-errors.json)。未觀察到需要擴充本 skill 的通用缺陷。

## 獨立複核

[review-final.md](task-harness-remediation-202610-evidence/review-final.md) 判定四項均可在本輪範圍內 closed，無阻擋 finding。Reviewer 直接核對五份原始 session 的全部 92 筆 tool events、身分與原始行指紋，獨立重跑安全 artifact verifier，並重驗 134 份歷史檔案。

另保留兩項非阻擋改善觀察：生成計畫的 coordinator 使用「current planning agent」而非穩定 handle；金額可為零的文字尚無獨立零值範例。它們已列於 review，不代表本輪已證明所有輸入與所有模型均無遺漏；未為此追加通用規則或修改受測產物。
