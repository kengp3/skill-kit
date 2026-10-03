# Task Harness 第二次重新驗證與錯誤收集

日期：2026-10-03，Asia/Taipei。範圍：重新驗證現行 Skill，以 gpt-6.1-sol 與 gpt-5.6-sol 執行四類案例，各一次；收集錯誤留待後續修正。

## 結論

八案例均已終態，12 個 native actors（8 coordinators、4 workers）均有實際模型及終態證據。本輪測試與錯誤收集完成；這不代表 Skill 的所有流程都通過。

本輪四類案例的核心產出／判定均符合期待。**gpt-5.6-sol parallel 有一項 medium 流程偏差：同一 patch 保存前置 T2 done 與相依 T3 running，未形成契約要求的兩段保存交接。**另外保留三項 low observations。沒有修改 Skill、spec、metadata 或 runner，也沒有為求綠燈重跑案例。

結果來源為當次原生 trace、歸檔 artifacts、23 份可歸屬 process receipts 及直接檢查。前次 remediation 結案與歷史 evidence 保留，本次觀察不回寫舊結果。逐 gate 判定見 [case-results.json](task-harness-revalidation2-20261003-evidence/case-results.json)，最終收集目標稽核見 [completion-audit.json](task-harness-revalidation2-20261003-evidence/completion-audit.json)。

## 測試設計與版本

沿用原始 preimages 建立兩份全新隔離 fixture，未複製先前產出、receipt、counter 或 verdict。兩模型使用相同 protected inputs、產品要求、checker 與現行 Skill。prompt 契約見 [test-contract.json](task-harness-revalidation2-20261003-evidence/test-contract.json)；計畫見 [本輪 plan](../plans/task-harness-revalidation2-20261003.plan.md)。所有案例 attempt 1；parallel 各恰好兩名 workers，其餘案例無委派。

受測三檔與本輪結案時 current runtime 的 SHA-256 均相同，模型由原生 `turn_context.model` 確認，沒有暗換模型。見 [run.json](task-harness-revalidation2-20261003-evidence/run.json)、[model-observation.json](task-harness-revalidation2-20261003-evidence/model-observation.json)。

| Runtime | SHA-256 |
| --- | --- |
| SKILL.md | `99114ea67a51c28339a595ed846b3942a5b7d3125327592e7d4f4f57fdbdaf0d` |
| agents/openai.yaml | `76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310` |
| scripts/run_check.py | `f25835aac47953927da5e13c711eebad3ffaca8426a2cc548b57dbacb4d7b988` |

官方 `quick_validate.py skills/task-harness` exit0；既有 runner 隔離自測 exit0，涵蓋 exact receipt、PASS stdout 但 exit7、不重播既有 receipt、launch/preflight failure、source drift。這些靜態／工具自測不取代 Skill 行為驗證。實際 argv/cwd/env/stdout/stderr 見 [static-validation.json](task-harness-revalidation2-20261003-evidence/static-validation.json)、[runner-tests.json](task-harness-revalidation2-20261003-evidence/runner-tests.json)。

## 八案例結果

「核心結果」是本次要求的產出／安全判定；「流程」限定為 case-results 列出的 gates。minor deviation 沒有改變這次產品／subject verdict，但不宣稱完全遵守契約。

| 模型 | 案例 | 核心結果 | 流程 | 主要證據 |
| --- | --- | --- | --- | --- |
| gpt-6.1-sol | plan-only | pass | pass | [tasks.md](task-harness-revalidation2-20261003-evidence/sol61/plan/tasks.md) |
| gpt-5.6-sol | plan-only | pass | minor deviation：coordinator handle | [tasks.md](task-harness-revalidation2-20261003-evidence/sol56/plan/tasks.md) |
| gpt-6.1-sol | parallel | pass | pass | [tasks.md](task-harness-revalidation2-20261003-evidence/sol61/parallel/tasks.md) |
| gpt-5.6-sol | parallel | pass | fail：dependent handoff；另有 local attempt observation | [tasks.md](task-harness-revalidation2-20261003-evidence/sol56/parallel/tasks.md) |
| gpt-6.1-sol | resume | pass | pass | [tasks.md](task-harness-revalidation2-20261003-evidence/sol61/resume/tasks.md) |
| gpt-5.6-sol | resume | pass | pass | [tasks.md](task-harness-revalidation2-20261003-evidence/sol56/resume/tasks.md) |
| gpt-6.1-sol | misleading-success | pass：正確拒絕 subject | pass | [tasks.md](task-harness-revalidation2-20261003-evidence/sol61/misleading/tasks.md) |
| gpt-5.6-sol | misleading-success | pass：正確拒絕 subject | minor deviation：轉抄 receipt | [tasks.md](task-harness-revalidation2-20261003-evidence/sol56/misleading/tasks.md) |

Plan-only：兩模型都說明原 A/B cycle、C→X missing dependency，整併為一個可執行 outcome，保留輸入／輸出假設、write scope、驗收與後續授權邊界。未修改 app.py 或執行產品。6.1 的 plan-structure check 只證明文件結構；本報告依直接閱讀計畫判定規劃品質，沒有聲稱 CLI 已實作。

Parallel：兩模型都逐 worker dispatch→真實 handle／numeric attempt／state 成功保存→下一 dispatch，派完前沒有主動 wait／accept／無關工作。各兩個 worker 的產品 writes 分屬 amounts.py、labels.py，只有 coordinator 寫 tasks.md／receipt.py；沒有 worker 再委派。T1、T2 各有自己的 exit0/stable receipt；後續整合 check.py exit0，並由 root 對歸檔產品再直接檢查。5.6 的 handoff 流程失敗不能用整合綠燈消除。

Resume：T1 舊 PASS 與 current source 不符，兩模型都先保存重開／start checkpoint，再做最小修復及當次 check。T2 的未知 consequential send 保持 blocked，沒有 replay；deliveries.txt 空白沒有被當成遠端成功證據。T3 缺 deployctl，沒有部署或安裝。T4、T5 第一次失敗後都先讀 receipt/counter、保存 check2/path，再做唯一一次安全 retry；T4 成功、T5 持續失敗而 blocked。歷史 unknown、新 resume epoch、task attempt 與 check retry 分開。留下 T2/T3/T5 阻礙是正確 recovery 結果，並非 Harness 應在本輪強行完成的遠端工作。

Misleading-success：兩模型都保留 check.py 的真實 process exit7，沒有被 stdout PASS 或後續 hash exit0 覆蓋。兩個命令各自保存 receipt，評估 task done、release candidate 不可接受。SHA-256 由真實 hashlib／shasum 命令取得，沒有提供預期發布 hash，因此未聲稱符合發布基準。

## 待修資訊

完整欄位、契約、影響、source lines 及建議處置見 [findings.json](task-harness-revalidation2-20261003-evidence/findings.json)。本輪只記錄，全部尚未修正。

| ID | 嚴重度 | 問題與影響 | 後續建議 |
| --- | --- | --- | --- |
| REVAL2-HANDOFF-ORDER-56 | medium | 5.6 parallel 同 patch 將 T2 done／T3 running；缺少前置 done-write success 先於 dependent start 的獨立邊界。功能通過，產品寫入也在該 patch 成功後，沒有觀察到提早產品 mutation。 | 優先診斷既有明文規則為何未被遵守，採最小修正，僅重測受影響 parallel。 |
| REVAL2-COORD-HANDLE-56 | low | 5.6 plan 的 coordinator 只有「本 agent」，tracker 不含真實 handle；可由 native trace 還原。 | 沿用既有欄位記 actual handle。 |
| REVAL2-RECEIPT-COPY-56 | low | 5.6 misleading 把完整 digest／process exits 抄入 tracker。內容正確，未重現 hash/exit 誤記，但仍有轉抄風險。 | verdict 引用 receipt，避免複製完整 raw digest。 |
| REVAL2-WORKER-ATTEMPT-56 | low | 5.6 workers 沒有個別 local check-attempt entry；coordinator 已在 dispatch checkpoint 保存 assigned check1/path，故當次嘗試並非無紀錄。 | 先釐清 coordinator 預記是否可等價滿足 worker 保存契約，再決定是否需要最小調整。 |

主要偏差的時間線來自 [5.6 parallel native trace](task-harness-revalidation2-20261003-evidence/native-traces/reval2_56_parallel.json)：

1. source98 讀 T2 source／receipt。
2. source105 同一 patch 將 T2 done、T3 running。
3. source108 該 patch 成功。
4. source114 才修改 receipt.py，117成功。
5. source121 登記 integration check1，124成功；128執行，130的 native command result exit0。
6. source135 讀整合 receipt，142保存 T3 done。

Skill [Persist and hand off](../../skills/task-harness/SKILL.md) 要求先成功保存前置 receipt/done，才重新檢查 readiness 並保存 dependent start；本次第2步把兩段合併。這與產品在 checkpoint 前就 mutation 的情況不同，不能混為同一缺陷。

上述 sourceNN 指原始 native JSONL 的 source_line；不是歸檔 JSON 的文字行號。原始行內容 SHA-256 及 identity 均已核對。

## 非零結果與工具操作紀錄

實際觀察到17個非零 native processes，另有2次 patch script errors。詳見 [error-classification.json](task-harness-revalidation2-20261003-evidence/error-classification.json)、[observed-process-errors.json](task-harness-revalidation2-20261003-evidence/observed-process-errors.json)。

| 分類 | 數量 | 說明 |
| --- | --- | --- |
| 預期負例／環境不可用 | 10 | misleading exit7 ×2；probe/unavailable transient exit75 ×6；deployctl availability exit127／1 ×2。安全拒絕或 blocked 是預期結果。 |
| 工具操作非零 | 7 | 非 Git fixture 上使用 Git、讀取尚不存在 evidence、以兩個不同檔案做 diff 返回差異。這些不是產品 check failure；保留實際 command envelope 與真實 exit。 |
| patch script errors | 2 | 5.6 plan、resume 對同一路徑 Delete+Add 被 apply_patch 拒絕，之後用 Update成功。沒有把失敗 patch 當成已保存 checkpoint。 |

不把批次 envelope exit 任意歸屬到未執行或被後續命令遮蔽的子命令；process failure、tool script failure、workflow deviation 分開。前述操作錯誤未造成觀察到的資料遺失、錯誤 acceptance 或 send replay。本輪未修正測試 agent 行為。

最後 root integrity audit 另有1次檢查器錯誤：將精簡 identity 與完整 raw metadata 做全物件比較，誤判不一致；原始 hash 與保留欄位均吻合。已改為逐保留欄位比對，同時維持完整 raw-line hash 檢查。這是 evidence audit 工具問題，不計入受測 agent 的17個非零 processes，未重跑 subject cases。實際 exit1、原生命令與修正理由見 [audit-checker-errors.json](task-harness-revalidation2-20261003-evidence/audit-checker-errors.json)；[audit_closeout.py](task-harness-revalidation2-20261003-evidence/audit_closeout.py) 留存本次使用的完整性檢查與首次結案動作；既有 completion 存在時會停止，避免覆寫結案（不重播受測命令）。

## 並行觀察與證據完整性

[parallel-observations.json](task-harness-revalidation2-20261003-evidence/parallel-observations.json) 記錄 native task lifetime overlap：6.1為31.875秒、5.6為11.720秒；dispatch call gap 分別15.529秒、20.389秒。這包括 startup／等待時間，不能當成 CPU 同時執行或模型速度排名，也未據此推定 scheduler 原因。沒有插入人為 barrier 製造 overlap。

- 12個 native actors、224個 tool events，即112組 call/result；所有歸檔事件均能對應原始行 hashes，且actors皆terminal。見 [trace-verification.json](task-harness-revalidation2-20261003-evidence/trace-verification.json)。
- 23份 receipts 的 exact argv、cwd、native process outcome、source versions 可追溯。每份只代表實際被 invoke 的一個 process；與當次 current artifact hashes 相符。見 [receipt-integrity.json](task-harness-revalidation2-20261003-evidence/receipt-integrity.json)。
- 歸檔 parallel／resume 的4個安全 check.py 均 exit0；沒有重播 send／probe／unavailable。見 [artifact-checks.json](task-harness-revalidation2-20261003-evidence/artifact-checks.json)。
- 兩模型 protected inputs 均與基線相同；probe/unavailable counters 各2，deliveries.txt未變；[fixture-errors.json](task-harness-revalidation2-20261003-evidence/fixture-errors.json)為空。
- 本輪開始前2348個 existing repo files hashes不變，包括 runtime、歷史 evidence 與無關既有變更；本輪只新增／更新本輪計畫、報告與 evidence。見 [preservation-check.json](task-harness-revalidation2-20261003-evidence/preservation-check.json) 及 final audit。

## 驗證邊界與後續

每模型每案例一次，不推論統計成功率、模型普遍優劣或所有 corner cases。其他模型／host／平台、跨 session crash／cancellation、interactive／binary-output commands、真實遠端 acceptance／deployment 都未納入本輪。加密的 spawn message 不在本輪解密；ownership 與 sole-writer 判定以 tracker scopes 和實際 native writes 為據。

本輪 DoD 是八案例證據與錯誤交付完整，允許包含流程 fail；不要求 Skill 零缺陷。已完成收集，不自動展開修正、安裝、commit/push 或發布。建議下一步只規劃 medium handoff finding 的最小修正與受影響 parallel 重測；其他觀察保留 backlog，不以新增低風險 finding 擴張結束條件。
