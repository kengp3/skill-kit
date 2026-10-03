# Task Harness 修正分析與執行計畫

日期：2026-10-02。狀態：**F1–F4 完成；四項既有 findings 在本輪範圍內 closed**。

## Objective

處理不同模型驗證發現的 OBS-01、GAP-01、GAP-02、GAP-03：讓計畫可交接、驗收條件有對應檢查，並讓派工與狀態變更的結論有相稱證據。這份文件是後續執行的單一任務清單。

## Background

現有結果沒有證實功能或授權缺陷；四項發現不能全部當成 skill 的程式錯誤。SKILL 已要求 coordinator、baseline、工具與權限，也已要求單一 coordinator 寫入。直接新增更多相同規則，不一定能改善模型的漏寫，更不能補回缺失的歷史觀測。

規劃階段已讀取現存 skill、spec、錯誤清單、生成計畫、dispatch 記錄與 verify.py，當時未執行修正。使用者後续授權後已進入執行；以下原始分析保留，實際狀態見任務表與 checkpoint。

規劃依三個指定 skills 複核：skill-creator 要求只針對已觀察行為做小幅修正；using-agent-skills 要求明確範圍、依賴與直接驗證；ponytail 要求先沿用原生能力與既有 verifier。空姓名案例只屬於本次 fixture，不寫成通用 skill 的固定需求。

## Materials

- [現行 skill](../../skills/task-harness/SKILL.md) 與 [規格](../specs/task-harness.spec.md)。
- [不同模型報告](../research/task-harness-cross-model-202610.research.md)、[結構化清單](../research/task-harness-cross-model-202610-evidence/findings.json)。
- [規劃產物](../research/task-harness-cross-model-202610-evidence/plan/tasks.md)、[dispatch 證據](../research/task-harness-cross-model-202610-evidence/parallel/evidence/dispatch.txt)、[既有 verifier](../research/task-harness-cross-model-202610-evidence/verify.py)。
- [原始輸入](../research/task-harness-cross-model-202610-evidence/original-inputs.json) 與該 evidence 目錄內的 baseline、protected inputs、skill copy。

## Boundaries

- 初始階段僅規劃；使用者後續明確指示「開始修正」，本輪執行 F1–F4。
- 後續優先修改 `skills/task-harness/SKILL.md` 的兩處說明；metadata、runtime、其他 skills 沒有已證實的修改需求。
- 新驗證資料放在 `docs/research/task-harness-remediation-202610-evidence/`，結案報告為 `docs/research/task-harness-remediation-202610.research.md`；建立時重新確認路徑與是否已有內容。本輪按此位置保存新產物。
- 舊報告與舊 fixture 保留為歷史證據；不得直接修好舊測試產物再宣稱修正有效。
- 不新增 scheduler、鎖服務、常駐監控或 skill runtime dependency；不全域安裝、commit、push 或發布。

## Baseline 與權限

- 確認根目錄：`/Users/kengp3/Workspaces/mine/simple-skills`。
- Authority：本檔；coordinator：`/root`；實際 owner 見任務表。
- Skill 為未追蹤的新目錄；以內容指紋辨識本次基準，不用 HEAD 冒充已提交版本。
- SKILL.md SHA-256：`d64660c2e4aa67d33dd3d98c7fbe846d03254ccfb0e3b2697671eba7a44d7701`。
- agents/openai.yaml SHA-256：`76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310`。
- 本輪可用能力：本機檔案與工具 metadata 檢查、skill／計畫／evidence 寫入、隔離 Python checks、原生 subagents 及狀態查詢。未指定時間、成本或 token 預算。
- 其他未追蹤的既有報告、計畫及 README 既有修改，不屬於此次修正目標。

## 分析與處置

| ID | 已知事實與可能原因 | 建議修改位置 | 通過條件 |
| --- | --- | --- | --- |
| OBS-01 | 生成計畫漏 coordinator、workspace/baseline、available tools。現行模板有欄位，但「只保留影響決策的細節」可能被解讀為可略去；這是待驗證的原因推論 | SKILL 的模板引導句：分清最低交接資訊與可省略細節 | Fresh plan 能辨識實際根目錄、協調者、相關材料版本、可用工具及權限；無法取得者明示原因，不編造 |
| GAP-03 | 計畫自行要求非空姓名，卻沒有對應檢查；目前沒有可判定錯誤的 CLI 實作 | SKILL 的 acceptance/verification 說明，加一句逐項對應檢查；測試驗收清單補同一條件 | 每個 acceptance 都有具體檢查；非空姓名對應空字串失敗情境。Plan-only 只列出，不執行 CLI |
| GAP-01 | 有真實 handles 與完成成果，缺執行時間重疊觀測。不能判為「未平行」 | 隔離驗證方法及證據收集，不優先改 skill | 同一次原生狀態查詢顯示兩個相關 handles 都 running；或有可信、可對齊的 host 生命週期事件證明區間重疊 |
| GAP-02 | 最終文件與整理後敘述不能還原每次狀態變更或寫入作者；尚無 ownership 反例 | 驗證時保存 host 原始 tool events 與狀態文件快照 | 能把每個受測狀態寫入對應到實際 actor、tool call/result 及前後狀態；有未覆蓋寫入途徑時不得聲稱完整證明 |

OBS-01、GAP-03 共用一次小幅文字調整與一次 fresh plan 測試。GAP-01、GAP-02 共用一次受控派工測試與證據保存，避免各自建立新工具。

原 A/B/C 重組成 T1 的對照，可在實際重組紀錄補一行原因與映射；目前沒有 stable-ID bug 的證據，不新增禁止重新編組的規則。

## 證據能力與限制

已確認本機存在本對話的 host session JSONL：

`/Users/kengp3/.codex/sessions/2026/10/02/rollout-2026-10-02T14-59-53-01a0fb69-8abc-7660-9bdc-e9e39fbde9b5.jsonl`

本次唯讀檢查確認包含 timestamp、tool name、namespace、call_id，以及對應的 tool outputs。**執行時已確認子 agent 各自有 session JSONL，session_meta.agent_path / id / parent_thread_id 可對應 actor，工具呼叫保留 call_id 與結果。**主對話 log、完成訊息與 `list_agents` 的 terminal 狀態不能代替完整子 agent audit。

後續只抽取本輪 fixture 相關且可歸因的事件，不封存整段私人對話。若 host 無法提供某項原始事件，該項維持 evidence gap，阻止「四項全部結案」，但不妨礙其他獨立工作。手填 actor、worker 自述、檔案 mtime 或最終 hash 不能單獨證明唯一寫入者。

## 建議流程與任務清單

先做 F1 的觀測能力核對，再做 F2；F3 整合本輪證據，最後 F4 結案。F1 與 F2 沒有硬性資料相依，但先確認證據能否取得，可降低返工。

| ID | 成果 | Depends on | Owner | State |
| --- | --- | --- | --- | --- |
| F1 | 建立可行且有界的觀測／歸因方法，列明無法取得的證據 | none | /root | done |
| F2 | 釐清最低交接資訊與 acceptance 對應檢查，通過 fresh plan 驗證 | none | /root + /root/remediation_plan | done |
| F3 | 在最終版本完成派工、狀態與續作驗證，逐項判定 findings | F1, F2 | /root/remediation_parallel + /root/remediation_resume | done |
| F4 | 獨立證據複核與修正結案 | F3 | /root/remediation_audit (gpt-6-astra) | done |

### F1：先確認觀測方法

- 寫入範圍：新的 remediation evidence 目錄；不改 skill。
- 檢查原生 host log 是否能取得本輪 coordinator 與兩個 worker 的 actor、tool calls/results。以實際 schema 核對，不能假設存在 export API 或把子 agent 當成 user-visible chat。
- GAP-01 的測試安排：兩個 worker 各有獨立檔案 scope；先用原生 `collaboration.list_agents` 與本輪的 path prefix 保存狀態。若任務太快而捕捉不到，再使用僅限 fixture 的有界 ready/release 同步點，保存兩個 handles 同時 running 的原始回應後釋放工作。設定明確等待上限、逾時清理並核對原 handles；不得因等待逾時就重派 live writer。
- 此觀測證明原生 worker 生命週期重疊，不證明 CPU/GPU 在同一瞬間運算，也不作效能或壓力測試結論。同步點只用來驗證協調，不加入 skill 的正常派工流程。
- GAP-02：利用現有 host tool trace，保存每次 task-state 寫入前後快照、call/result ID、實際 actor 與必要時間資訊。不得只新增一份由 coordinator 自填的 event log 就視為解決。
- Acceptance／驗證：確認可取得哪些原始事件、如何核對 writer 與狀態順序，並對最小樣本實際核對；或明確證實某項能力缺失、留下 blocker。F1 的能力調查可以完成，但缺證據的 GAP-02 仍保持 open。

### F2：最小 skill 調整與規劃驗證

- 寫入範圍：`skills/task-harness/SKILL.md`；新 plan-only fixture 與其 evidence。只有一名作者修改 skill。
- 調整 A：在現有模板引導段，明確指出 plan-only 仍保留 coordinator、workspace/材料基準、相關工具與權限。其餘細節依情境精簡；非軟體任務可用材料版本；未知或不適用者明示，不強制虛構 Git revision 或 worker handle。
- 調整 B：交付前核對 acceptance 與 verification 的對應，加入影響該 acceptance 的錯誤／邊界輸入。保持 plan-only 不執行實作檢查的限制。
- 使用乾淨 fixture 重建原本的草案、原始 app.py、保留文件與指紋。交給 `gpt-6-sol` 的 fresh evaluator，僅提供現實需求、受測 skill、必要材料與範圍，不提供期望答案或 suspected bug。
- 驗收時對照每個條件：姓名／整數清單／總額／錯誤退出；若保留非空姓名 acceptance，至少列出 `python3 app.py '' 10` 及非零退出、不輸出收據的預期。純空白姓名是否無效取決於實際契約，不自行新增。
- Acceptance／驗證：官方 skill validator 通過；fresh plan 保留最低交接資訊、無 acceptance cycle、每項條件有相稱檢查；原始程式及其他計畫不變。規劃 coordinator 可已知，但實作任務應維持 pending／未指派，不能把保存協調者資訊當成啟動 worker。
- 若一輪仍漏寫，保存原始失敗與差異，再定位問題；不連續加入重複泛用規則。F2 含自身的直接驗收，不等待 F3 才能完成。

### F3：最終版本派工／續作驗證

- 寫入範圍：新的隔離 fixtures 及 remediation evidence；不修改舊歷史資料。
- 在 F2 受測版本上執行派工測試，兩名 worker 範圍互斥，coordinator 整合 receipt 並驗證原始 checker；以 F1 方法捕捉 runtime overlap 與狀態／writer 證據。
- 重新核對舊成果失效、unknown send 不重播、缺少工具保持 blocked、安全暫時錯誤一次 retry、持續錯誤有界停止；保持 counters／保護檔案可直接查驗。
- 沿用並按需調整既有 evidence verifier；新增的檢查驗證實際 artifacts、tool events、轉移與 fingerprints，不比對 prose headings 冒充行為驗收。少量事件可直接人工核對，不先做通用 trace parser。若確需新增解析邏輯，至少檢查一個正確 trace 與一個缺事件／錯誤 actor 的負例；不得只因 log 非空就通過。
- F2 的 fresh plan 若與最終 skill 指紋一致即可沿用，避免重跑同一案例；若 skill 又改動，重驗受影響條件並記錄版本。
- Acceptance／驗證：OBS-01、GAP-03 的規劃輸出通過；GAP-01、GAP-02 有各自所需的直接證據；整合函式 checks 與保護檔案檢查通過。缺乏 actor trace 或並行觀測時明列未通過項目，不能由功能 assertions 代替。

### F4：獨立複核與交接

- 寫入範圍：新的 remediation report、本計畫的狀態；不改受測 skill。
- 由 `gpt-6-astra` 讀需求、最終 skill、原始輸入、直接證據與最終產物，逐項核對四個 IDs；不先提供作者希望獲得的 verdict。
- Acceptance／驗證：每項標示 closed、仍 open 或待外部能力解除；closed 必須有對應證據。檢查報告連結、最終 source hash、歷史證據未被改寫，以及驗證宣稱的範圍。
- 若 F3 受阻，先在 checkpoint 報告已完成部分與精確 blocker；F4 的全部結案仍 pending。不得把「證據不足已揭露」改標成「證據缺口已修復」。

## Definition of Done

規劃階段驗收：四項都有分類、最小處置、負責範圍、依賴、驗收方式與證據門檻；當時未開始修正。

後續修正：

1. OBS-01 與 GAP-03 在 final skill 的 fresh plan 中實際通過，保留 plan-only 權限邊界。
2. GAP-01 有可信的 worker 存活時間重疊觀測；GAP-02 有足夠的狀態／writer 原始證據。任一缺失時，整體修正不得標為完成。
3. 受影響情境在最終版本通過；無需因不相關文件改動重跑全部測試。
4. Skill 維持可獨立使用；新增驗證工具不成為 runtime dependency。
5. 各項修正、通過／失敗與限制都保存於新報告，無尚未處理卻被隱藏的 findings。

## Checkpoint

執行 checkpoint：F1 已確認原生 child session trace 可取得；F2 的兩處文字修改通過官方 validator 與 fresh plan 驗證。F3 已取得兩名 worker 原生 running 重疊、四次 coordinator tracker 寫入與完整工具事件；整合、保護檔案與 retry counters 通過。F4 獨立核對五份 session 的 92 筆工具事件、重跑安全 verifier 並確認四項 closed。所有本輪 agents 已完成，沒有未結案修正任務；續作 fixture 正確留下三項預設 blocked。

最終 SKILL SHA-256：`948713f0c0720334b7c4ab355a78c11c162a4a14a19b683289a37e14abeec5be`。Fresh workspace：`/private/tmp/task-harness-remediation-w5zjr1sb`；完整封存、判定與邊界見 [修正報告](../research/task-harness-remediation-202610.research.md) 及 [獨立複核](../research/task-harness-remediation-202610-evidence/review-final.md)。Writer 結論限受測 actors 的原生工具事件，非 OS 全域排除。未安裝、commit、push 或發布。
