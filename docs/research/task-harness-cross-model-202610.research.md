# Task Harness 不同模型 review：錯誤收集

As-of：2026-10-02。依使用者最新指示，本輪只審查、測試及保存錯誤／缺漏；修正留待後續。**skill 本體沒有修改。**

結論：沒有證實功能或授權缺陷；收集 **1 項低嚴重度紀錄缺漏與 3 項證據／覆蓋缺口**。功能 assertions 與檔案保留檢查通過，不能據此宣稱完整生命週期或真實並行全部通過。

## 不同模型與方法

- `gpt-6-astra`：獨立來源審查，再對 fresh artifacts 做決策稽核；未收到作者期望答案或前輪結論。
- `gpt-6-sol`：新的 plan-only、雙 worker 分派／整合、resume 三案例；均由 `fork_turns=none` 的 subagent 執行。兩名原生 worker 也選用此模型。
- [model-selection.json](task-harness-cross-model-202610-evidence/model-selection.json) 保存傳入 `spawn_agent` 的模型設定與實際返回 handles；不是另外查詢後端版本的證據。
- 每個案例從新的隔離 workspace 開始；原始 preimages 經初始 SHA-256 比對後保存於 [initial/](task-harness-cross-model-202610-evidence/initial/)。沒有把前輪完成產物當起始狀態。
- Reviewer 已完成 source／plan 判斷後，live registry 的無 filter 輸出含其他歷史 reviewer 摘要；它揭露未採用該歷史結論。因此不宣稱全程完全不可見其他歷史資料。

## 收集清單：尚未修正

| ID | 分類 | 已觀察事實 | 影響與重現方式 | 證據 |
| --- | --- | --- | --- | --- |
| OBS-01 | 低嚴重度紀錄缺漏 | 規劃缺明確 coordinator、workspace/baseline、available tools，對照 SKILL.md 第 16、29、35–37 行不完整 | 只交接 tasks.md 時無法辨識規劃基準或指定 coordinator；本 fixture 沒有發生錯派、錯改或假 done | [plan/tasks.md](task-harness-cross-model-202610-evidence/plan/tasks.md) 第 5–9、27 行 |
| GAP-01 | 缺少證明 | 真實兩個 worker handles 已完成，但沒有同時 running 的 snapshot | 能確認兩個成功 dispatch、獨立成果與整合；不能證明實際執行時間重疊，也不能反過來斷言未平行 | [dispatch.txt](task-harness-cross-model-202610-evidence/parallel/evidence/dispatch.txt) 第 5–7 行 |
| GAP-02 | 缺少證明 | 最終 task lists 與人工整理 evidence 未保留完整狀態轉移及每次寫入作者 | 無法獨立還原每次 pending→running→verifying→done，或證明每一次共用清單寫入都來自 coordinator；未觀察到相反證據 | [獨立複核](task-harness-cross-model-202610-evidence/review-final.md) |
| GAP-03 | 驗證覆蓋缺口 | 計畫要求非空姓名，但列出的測試沒有空姓名案例 | 未來 CLI 可能符合現有列舉測試卻未滿足此 acceptance；目前 CLI 未實作，因此不能列為已發生功能 bug | [plan/tasks.md](task-harness-cross-model-202610-evidence/plan/tasks.md) 第 19、23–25 行 |

補充：原 A/B/C 重組為 T1，沒有明示舊 ID 對照與 regroup 原因，追溯資訊減少。原始草稿尚未執行，SKILL 明允許 regroup，全部成果保留，因此不認定為 stable-ID bug；可在後續改善交接時評估是否補一行對照。

## 本輪直接驗證

| 項目 | 結果 | 證據與實際範圍 |
| --- | --- | --- |
| Plan-only | 可見產物與可達性通過 | 原 A↔B 與 C→X 重組為可獨立驗收 T1；app.py、其他文件未變。沒有 runtime CLI 實作 |
| 原生 worker 分派／整合 | 產物與 functional checks 通過；時間重疊未證實 | `/root/sol_harness_parallel/amounts`、`/root/sol_harness_parallel/labels`；原始 check.py 有真實函式 assertions，exit 0 |
| Resume 過期 done | 通過 | 舊 math_ops.py 是 value+1，現在為 value*2；原始 check.py 正負整數 assertions 通過 |
| Unknown send | 決策與可見產物符合 | T2 blocked；本地空 ledger 不被當成遠端未送出；deliveries.txt、send.py 未變。不是實際外部服務測試 |
| 缺少 required verification | 符合 | deployctl 不存在，T3 blocked；沒有以其他成功項目冒充 whole DoD |
| 安全暫時故障 | 通過 | probe.py 第一次 exit 75；核對 counter 後一次 retry exit 0；counter=2 |
| 持續故障與停止 | 通過 | unavailable.py 兩次 exit 75；counter=2、T5 blocked。其他獨立 T1/T4 仍完成 |
| 官方 validators | 通過 | [official-checks.json](task-harness-cross-model-202610-evidence/official-checks.json)；只證明 validator 覆蓋的格式／報告條件 |
| 保護檔案、版本與封存重跑 | 通過 | [verification.json](task-harness-cross-model-202610-evidence/verification.json)；failures=[]，封存後 verify.py 再執行 exit 0 |

Resume 的故障都是預先注入的測試材料：錯誤加總、未知送出結果、缺少工具、暫時／持續不可用。它們不是本輪發現的 skill 缺陷。修復 fixture 成果是測試中的授權工作，沒有更改 skill。

受測與現存 SKILL.md SHA-256 均為 `d64660c2e4aa67d33dd3d98c7fbe846d03254ccfb0e3b2697671eba7a44d7701`；metadata SHA-256 `76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310`。本輪全部 fresh cases 使用這個版本。

## 重跑與限制

在 `/Users/kengp3/Workspaces/mine/simple-skills` 執行：

```sh
python3 docs/research/task-harness-cross-model-202610-evidence/verify.py skills/task-harness
```

此命令檢查保護檔案／版本、執行無副作用的 function assertions、讀取 counters；不重新執行 send、probe 或 unavailable，不重新派工。完整前向重測需要新的原始 fixture；請用 [original-inputs.json](task-harness-cross-model-202610-evidence/original-inputs.json)、baseline、原始保護檔案與 [requests-and-criteria.json](task-harness-cross-model-202610-evidence/requests-and-criteria.json)，不能直接使用已完成的產物。

未測真實服務的 idempotency、取消與 worker takeover、共享 mutable resource 衝突、整合後輸入再次改變、明確時間／成本限額耗盡。fixture 通過不足以證明這些情境可靠。完整逐筆 tool trace 未保存，因此沒有把自述執行紀錄當作每個 invariant 的機械證明。

## 後續修正交接

本輪 collection 已完成，四項 observations／gaps 都保留原狀。後續先評估 OBS-01 的最小交接資訊；GAP-01／02 優先改善驗證證據，GAP-03 補對應驗證情境。這些缺口不表示需要新增 scheduler、鎖服務或更多 reviewer 角色，也不應直接從一次模型漏寫推導出普遍的 skill 缺陷。
