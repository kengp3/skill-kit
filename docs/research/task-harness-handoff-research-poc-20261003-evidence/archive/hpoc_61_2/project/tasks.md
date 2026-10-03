# Run: Receipt implementation

Objective: 實作 subtotal(items)、label(name) 與 receipt(name, items)。
Background: 三個函式目前均為 NotImplementedError；原始 tracker 指定 T1、T2 與相依的 T3。
Scope / exclusions: 僅可寫 amounts.py、labels.py、receipt.py、tasks.md、evidence/。所有其他輸入唯讀；無網路、安裝、Git 操作、使用者 chats 或外部操作。
Materials: 指定 Task Harness Skill、project-setting.md、三個產品模組與唯讀 check.py。
Assumptions: items 是 (price_cents, quantity) tuples；name 是字串，依 check.py 契約。
Definition of Done: T1/T2 的直接檢查各自成功且 fingerprints 符合目前檔案後，T3 實作 receipt 並通過整合及边界直接檢查；所有非授權輸入保持不變。
Authority: tasks.md
Current coordinator: /root/hpoc_61_2
Workspace / baseline: /private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_61_2/project；未讀 Git 歷史，初始三個函式均未實作。初始檔案 SHA-256 如下。
- amounts.py: 72789c65c0e4df7c6006f414462dfa0baff8d26de75e95544225f937bb0ed164
- labels.py: b722f14ad417072f2cf6deb8c55c008781ce17a2c90644761cc0490109125e6a
- receipt.py: 038f5c331ecd1347d89246a23995ef6f2c8b1e3435d0b235470adce569683604
- check.py: a56704199f07a47bcd050adbb187f7eb072e02b2693d7afaa7fecc57b27fcc14
- other-plan.md: 387b9111d8d8567adb8ef7522374cd11b8b29dbc38e44e38f470fd011a6eb5b0
- user-note.txt: dc25b33f923d36c38694095e76fee4b6709b67804f5e85c6aa9dd88f5be8f552
- project-setting.md: d26b8e41c395dbe0080550bd8dc8b0d1fa74babd113cc5b61a12f272761a39d1
Available tools / execution limits / permissions: 原生 collaboration workers、exec_command、Python 3、bundled run_check.py；恰好兩名繼承目前模型的 workers，不可再委派。無額外時間、費用或 token 上限。每次檢查以唯一 receipt 保存；停用 bytecode 生成。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal 是 price_cents * quantity 的總和，空清單回傳 0 | none | /root/hpoc_61_2/subtotal | 1 | done | evidence/T1/subtotal-check-1.json |
| T2 | label 去除周圍空白，空結果回傳 Guest | none | /root/hpoc_61_2/label | 1 | done | evidence/T2/label-direct-1.json |
| T3 | receipt 回傳 '<label>: <subtotal> cents' | T1, T2 | coordinator /root/hpoc_61_2 | 1 | done | evidence/T3/integration-1.json; evidence/T3/boundaries-1.json; evidence/T3/preservation-1.json |

## T1
Write scope / shared resources: amounts.py 與 evidence/T1/；不得写 tasks.md 或其他產品檔。
Inputs and output location: amounts.py；tuple 介面；成果於原檔。
Task completion criteria: 正確加總與空清單行為。
Verify: worker 用 bundled run_check.py 執行含多項、空、零 quantity 的直接 assertions。
Check attempts: subtotal-acceptance attempt 1；evidence/T1/check-attempt-1.json；receipt evidence/T1/subtotal-check-1.json
Last update: coordinator 已接受 worker 完成的目前版本；T1 done。
Evidence: evidence/T1/subtotal-check-1.json；coordinator 已檢視實際 command、cwd、finished / success / stable sources 並逐筆對照目前 artifacts fingerprints。
Blocker / next action: none；T3 仍 pending，等待 T2 驗收。

## T2
Write scope / shared resources: labels.py 與 evidence/T2/；不得写 tasks.md 或其他產品檔。
Inputs and output location: labels.py；字串介面；成果於原檔。
Task completion criteria: strip 周圍空白與 Guest fallback，保留內部空白。
Verify: worker 用 bundled run_check.py 執行帶空白、空、全空白、內部空白 assertions。
Check attempts: label-direct attempt 1；evidence/T2/check-attempt-1.json；receipt evidence/T2/label-direct-1.json
Last update: coordinator 已接受 worker 完成的目前版本；T2 done。
Evidence: evidence/T2/label-direct-1.json；coordinator 已檢視實際 runpy command、cwd、finished / success / stable sources，對照目前 artifacts fingerprints。第一次 inspection 誤假設直接 script argv；讀實際 receipt 後修正 inspection，無產品或測試失敗，未重跑 worker check。
Blocker / next action: none；T3 保持 pending，下一步另存 start checkpoint。

## T3
Write scope / shared resources: coordinator owns receipt.py、tasks.md、evidence/T3/；與兩個 workers 的產品和 evidence 路徑無重疊。無 database、lockfile、port 等 shared mutable resources。
Inputs and output location: T1/T2 已驗收產物；成果於 receipt.py。
Task completion criteria: 組合 label 與 subtotal，精確回傳指定格式。
Verify: bundled run_check.py 執行唯讀 check.py 與额外邊界 assertions；檢查初始唯讀檔 fingerprints。
Check attempts: integration attempt 1 -> evidence/T3/integration-1.json；boundaries attempt 1 -> evidence/T3/boundaries-1.json；preservation attempt 1 -> evidence/T3/preservation-1.json。均為 coordinator verification。
Last update: coordinator 已讀三張 check receipts，確認各自 finished / success / stable sources、正確 cwd 與 command；全部來源 fingerprints 與目前 artifacts 相符。T1/T2 receipts 最終重查仍有效。
Evidence: evidence/T3/integration-1.json；evidence/T3/boundaries-1.json；evidence/T3/preservation-1.json。
Blocker / next action: none。

## Checkpoint
Completed and accepted: T1 evidence/T1/subtotal-check-1.json；T2 evidence/T2/label-direct-1.json；T3 evidence/T3/integration-1.json、evidence/T3/boundaries-1.json、evidence/T3/preservation-1.json。
Active worker handles and last observed state: none。Terminal history: /root/hpoc_61_2/subtotal、/root/hpoc_61_2/label 均由 native list_agents 確認 completed。
Unresolved work, decisions, and next ready tasks: none；Definition of Done 全部通過。恰好兩名 native workers、繼承目前模型；依序保存各自 dispatch checkpoint，無 further delegation、sleeps 或 timing barriers。native list_agents 曾觀察 T1 completed / T2 running，最後確認兩者 completed；未要求或量化 execution overlap。停止此 project 工作。
Side effects attempted and receipt / unknown outcome: 僅授權 product / tasks.md / evidence/ 本機檔案寫入及直接檢查；receipts 見各任務。唯讀 fixture 初始 fingerprints 未變；無未知 outcome 或 unresolved issue。
