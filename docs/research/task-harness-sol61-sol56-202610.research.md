# Task Harness：6.1 sol / 5.6 sol 重測與錯誤收集

日期：2026-10-02。狀態：**六個 fresh 案例已執行並封存；錯誤收集完成，修正留待後續。**

兩個指定模型均實際執行，包含各自兩名 helper workers。兩模型的 receipt 整合與安全續作檢查通過；5.6 sol 的 plan-only 仍漏最低交接資訊。另收集狀態紀錄、版本證據及退出碼紀錄問題，不能把功能 assertions 全綠理解為所有 harness 行為通過。

本輪沒有修改 skill、metadata 或既有證據。它驗證的是目前版本在指定案例的表現，不是模型效能排名、缺陷率估計，亦不能隔離證明先前兩段修改的因果效果。

## 版本、模型與方法

- 根目錄：`/Users/kengp3/Workspaces/mine/simple-skills`。
- [受測 skill](../../skills/task-harness/SKILL.md) SHA-256：`948713f0c0720334b7c4ab355a78c11c162a4a14a19b683289a37e14abeec5be`。
- 由 `skill-creator` 的獨立 forward-testing 流程建立隔離 fixture；`using-agent-skills` 用於範圍與驗證核對；`ponytail` 沿用既有原始 inputs、verifier 與 trace exporter，沒有新增 runtime 套件。
- 原始 workspace：`/private/tmp/task-harness-solmatrix-mc_zeld9/sol61`、`/private/tmp/task-harness-solmatrix-mc_zeld9/sol56`。封存於本報告旁的 [evidence](task-harness-sol61-sol56-202610-evidence/run.json)。
- 每個模型分別從原始 stub、循環／缺失依賴草案及中斷狀態開始；不複製已完成輸出。相同 skill、原始檔案、checker 與請求，詳見 [test-contract.json](task-harness-sol61-sol56-202610-evidence/test-contract.json)。未提供預期答案或舊 findings。
- 原生 `turn_context.model` 已核對六名 coordinator 與四名 workers：五名 `gpt-6.1-sol`、五名 `gpt-5.6-sol`，非僅依 requested model 判定。見 [model-observation.json](task-harness-sol61-sol56-202610-evidence/model-observation.json)。
- 原生工具紀錄共 10 名 actor、142 筆 call/result。逐筆對照原始 session identity、行號、payload 與 SHA-256，完整投影無遺漏；見 [trace-verification.json](task-harness-sol61-sol56-202610-evidence/trace-verification.json)。只保存受測 actors 的工具資料及必要派工／狀態事件。

## 六案例結果

| 模型 | 情境 | 實際結果 | 保留問題 |
| --- | --- | --- | --- |
| 6.1 sol | plan-only | A/B/C 改為有效 A→B→C；B 自帶直接驗收，不等待 C；保留根目錄、指紋、工具與權限，空姓名有明確命令與失敗預期；未實作或派工 | coordinator 用相對名稱，未宣稱穩定 handle |
| 6.1 sol | parallel | 恰好兩名原生 worker、scope 互斥、coordinator 唯一 tracker writer；helpers 實際檢視，原始 checker 通過 | STATE-01：整合與狀態更新順序、完成後仍列 active/running |
| 6.1 sol | resume | 當前 checker 發現 stale done；修復後通過；unknown send 沒有重播；T1/T4 done，T2/T3/T5 blocked；兩 counter 都為 2 | EVID-61-01：retry 的個別退出碼被合併 shell 結果遮蔽 |
| 5.6 sol | plan-only | A↔B、C→X 重組成單一端到端 T1；空姓名、非整數、缺金額均有失敗驗收；未實作或派工 | REC-56-01：coordinator unassigned、工具漏列 |
| 5.6 sol | parallel | 恰好兩名原生 worker、scope 互斥、coordinator 唯一 tracker writer；helpers 實際檢視，原始 checker 通過 | STATE-01、EVID-56-01：進度紀錄落後，缺 tested-version 指紋 |
| 5.6 sol | resume | 由來源碼辨識 stale done；修復後 checker 通過；unknown send 沒有重播；T1/T4 done，T2/T3/T5 blocked；兩 counter 都為 2 | 工具 patch 錯誤已恢復，無新的安全續作行為缺陷 |

兩模型的 verifier 均 exit 0、`failures: []`：[6.1 sol](task-harness-sol61-sol56-202610-evidence/sol61/verification.json)、[5.6 sol](task-harness-sol61-sol56-202610-evidence/sol56/verification.json)。它檢查原始 checker、保護檔案、retry counters、final skill 副本及產物指紋；不自動驗收語意、tracker 更新時序或資料完整度，這些由下列工具紀錄與產物核對。

## 待後續處理的觀察

四項均保留為 `recorded; fixes deferred`，見 [findings.json](task-harness-sol61-sol56-202610-evidence/findings.json)。尚未證實功能或外部授權缺陷；以下是實際紀錄與證據不足。

| ID | 事實與影響 | 證據 |
| --- | --- | --- |
| REC-56-01 | 5.6 sol 計畫 coordinator 寫成 unassigned；Execution limits 只有限制，沒有可用工具。實作 owner 未指派是合理的，但不能替代已有規劃 actor 的交接資訊；與舊 OBS-01 同類 | [plan/tasks.md](task-harness-sol61-sol56-202610-evidence/sol56/plan/tasks.md)、同檔第 11 行 |
| STATE-01 | 兩模型在 tracker 尚列 helpers running 時就寫 receipt。6.1 sol 在同一 shell call 寫 receipt 後才將 helpers 改 done、T3 改 verifying；5.6 sol 在整合 checker 通過後才一次將 T1/T2/T3 改 done，T3 過程仍 pending。6.1 sol 結案又留下 active/running 舊文字。實際 helpers 已檢視且驗證通過，未觀察到 deadlock 或寫入衝突；問題是權威清單無法準確反映當時進度 | [behavior-audit.json](task-harness-sol61-sol56-202610-evidence/behavior-audit.json)、[6.1 sol final tracker](task-harness-sol61-sol56-202610-evidence/sol61/parallel/tasks.md) 第 25 行 |
| EVID-56-01 | 5.6 sol parallel 的兩份 worker evidence、integration.txt 與 final tasks.md 有命令與結果，沒有 tested source 指紋。主 coordinator 後來的 verifier 保存 final hashes，讓這次收集可審查，但不回填模型產物本身的版本證據 | [integration.txt](task-harness-sol61-sol56-202610-evidence/sol56/parallel/evidence/integration.txt)、同目錄兩份 worker evidence |
| EVID-61-01 | 6.1 sol retry 將 probe、unavailable、check、shasum 用 `;` 合在 shell；工具顯示的 exit 0 是最後 shasum 的結果。第二次 unavailable 的個別 exit 75 沒有獨立 receipt；只能由固定腳本、stderr 及 counter 推得，不把整段 exit 0 當作各子命令成功 | [resume trace](task-harness-sol61-sol56-202610-evidence/native-traces/solmatrix_61_resume.json)，`call_7gAHMQa9GZBMiwbjtVz6I2WL`，原始行 33→37 |

另有未決契約差異：6.1 sol 假設空金額清單為 0；5.6 sol 選擇至少一筆金額，並 trim 後拒絕純空白姓名。原始請求未完整界定這些情境，因此記錄差異，未判為已證實功能 bug。未修改生成計畫讓兩者事後一致。

## 實際工具錯誤

四次 patch 失敗均保留原生錯誤及恢復呼叫。Agent 可在本次 fixture 任務中恢復工具操作；這不代表對 harness 做了修正。

| 模型／案例 | 原生錯誤 | 恢復方式 |
| --- | --- | --- |
| 6.1 sol / plan | `invalid patch: multiple operations target .../tasks.md` | 改為 shell 寫入已讀取的 plan artifact |
| 5.6 sol / plan | 同一路徑 Delete + Add 被拒絕 | 改為 Update File |
| 6.1 sol / resume | `Failed to find expected lines ...` | 改為追加明確 current checkpoint；同一 exec 中前面的 evidence 寫入已成功，沒有重播服務 checks |
| 5.6 sol / resume | 同一路徑 Delete + Add 被拒絕 | 改為 Update File |

錯誤與 call/result IDs 詳見 findings.json 的 `incidental_tool_errors`。此外，5.6 sol resume 與 labels worker 曾在 non-Git fixture 呼叫 Git，得到 `not a git repository`；這是環境訊息，不是來源碼回歸。預設 seeded checker failure、缺少 deployctl、service exit 75 也與工具使用錯誤分開保留。

## 證據邊界與保存

兩模型都由一次實際 `list_agents` 回應確認兩個 workers 同時 running：6.1 sol 在 12:57:55 UTC、5.6 sol 在 12:59:24 UTC。原生回應與模型保存的 overlap.json 相符。這只證明原生 worker 生命週期重疊，不代表 CPU/GPU 同時計算或速度提升。

全部受測工具輸入均已檢視，workers 只寫自己的 source 與互斥 evidence；tasks.md 只有各案例 coordinator 寫入。這是受測 actors 的完整工具事件範圍，不是 OS 全域 writer 排除證明。這次未要求逐次 before/after snapshot，故狀態順序同時參照可見寫入程式／patch、工具結果與 final artifact；不將它描述成逐次 filesystem forensic snapshot。

官方 skill validator 通過；沿用的 exporter 僅替換本輪 actor prefixes，完整 pair／缺結果／無關 actor self-check 通過。[preservation.json](task-harness-sol61-sol56-202610-evidence/preservation.json) 確認 skill 與 192 份既有相關檔案指紋不變。安全重驗只執行 check.py，沒有再次執行 send/probe/unavailable，也沒有安裝、commit、push 或發布。

[任務清單](../plans/task-harness-sol61-sol56.plan.md) 的 done 表示重測與收集工作結束；不是宣稱本表所有品質觀察已修好。四項觀察與工具錯誤保留供後續分析，當前 goal 的錯誤收集要求已完成。
