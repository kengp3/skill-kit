# G06：原生 hook 來源與重入資格

日期：2026-10-26（Asia/Taipei）。**狀態：部分；真 startup／resume／compact 的同合約行為通過，raw input source 與同事件 native redelivery 仍受阻，G06／V03 整體未完成。** 依[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[G06 ticket](../plans/harness-gap-closure-06-hook-reentry.plan.md)與[總計畫](../plans/harness-validation-gap-closure.plan.md)執行。固定候選 manifest SHA-256：`7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。

## 已核對邊界

受測專案為 demo-002 現行 AGENTS.md、project-setting.md 的自有暫存副本；應用程式不需複製或執行。本案只操作自有 case/state，不改 demo、產品、全域或 trust database。複製固定候選四個技能，省略選配 scripts；控制器 Python 是維護驗收工具，產品模型禁止使用 Python/Node/helper。PS 與 task-harness 的 canonical 定義完整保留，只有固定 echo 和被動 Stop `{}`，沒有 continuation 變體。

[官方 Hooks 文件](https://learn.chatgpt.com/docs/hooks)說明 SessionStart 可按 startup／resume／compact 等 source 匹配，stdout 可加入 developer context；[官方 App Server 文件](https://learn.chatgpt.com/docs/app-server)列出 thread/resume、thread/compact/start 與 hook/started、hook/completed。這些說明不代表本案已實測通過。

本機 CLI 0.164.0 的 experimental schema 已實際產生：[命令結果](harness-gap-closure-hook-sources-evidence/schema-command.stdout)、[help／版本](harness-gap-closure-hook-sources-evidence/host-help.json)、[schema 相關完整定義](harness-gap-closure-hook-sources-evidence/schema-excerpts.json)、[175 個公開 methods](harness-gap-closure-hook-sources-evidence/public-methods.json)。沒有找到 hook 同事件 redelivery 控制。`thread/start.sessionStartSource` 與 `turn/start.turnTrigger` 是 caller 可提供分類，本案不填兩者；不能用它們證明原生來源或人類授權。

`HookRunSummary.source` enum 是 project／user／plugin 等**設定來源層**，不是 SessionStart 輸入的 startup／resume／compact。通知 schema 沒有原始 hook stdin 或邏輯 event ID。實測若只取得方法時序、run ID、設定 sourcePath 及 developer context，僅能支持該層觀測，不能杜撰 raw-input source 或 redelivery 關聯。

## 單次 bypass 資格試驗

本案明確允許在核對 exact canonical／PS 靜態 echo 後使用單次 automation bypass；不代表 G03 正常持久信任通過。控制器在啟動前逐檔核對候選，完整讀回 handler bytes，檢查只有預期 prefix、timeout=5 且不存在 dynamic shell metacharacters；hooks/list 另比對唯一自有 sourcePath 和五個 handlers。專案信任與 hook 信任分開。

首個 preflight 的 app-server `-c bypass_hook_trust=true` 被宿主明確回報 ignored，hooks/list 全為 untrusted。這是資格失敗，不是 canonical hook 已執行。該次未建立任何 thread／turn／worker，controller 收到 SIGINT 後 exit 130；OS 查核 controller PID 4763、server PID 4772 均已退出。[原始紀錄與處置](harness-gap-closure-hook-sources-evidence/preflight-ignored-override/disposition.json)。保留該次 case/state，不把重建資格環境稱同任務恢復。

第二次在 thread/start.config 使用本機 binary 明確列出的 `bypass_hook_trust` boolean override，宿主實際回傳 configWarning「`--dangerously-bypass-hook-trust` is enabled」。這支持該 thread 的單次測試條件已被接受，仍須取得真實 hook run，才能證明執行。[第二次 preflight 核對](harness-gap-closure-hook-sources-evidence/preflight-check.json)。全域三個衝突 skills 在 isolated state 明確停用並 forceReload；其他 system／user skill 可見性如實記錄，不宣稱全機隔離。state=0700、auth=0600，認證不歸檔；runtimeWorkspaceRoots 只允許 case root。

## 驗收方式與實際結果

已確認 seam 為「明確啟用技能 → native model → 同合約／產品 → 直接讀回」。[獨立 checker](harness-gap-closure-hook-sources-evidence/check.py)先對缺失 canary 的新案例取得真 red：[red-check.json](harness-gap-closure-hook-sources-evidence/red-check.json)，不是手填 passed。控制器不寫產品合約或 canary；模型需完成一次 canary、一個唯讀 worker，resume／compact 保留相同合約、既有成果與原 handle，不重派或重驗未變條件。

預期 → 同合約經真生命週期仍只寫一次、不重派、canonical Stop 不自動續作。觀察 → 三個明確授權回合全部 completed，真正 compaction 也 completed；只有一個產品 worker，沒有恢復派工。原始依據 → [對帳與逐行位置](harness-gap-closure-hook-sources-evidence/native-verification.json)、[startup RPC](harness-gap-closure-hook-sources-evidence/rpc.jsonl)、[resume／compact RPC](harness-gap-closure-hook-sources-evidence/resume/rpc.jsonl)、[developer 原生逐字行 excerpt](harness-gap-closure-hook-sources-evidence/model-context.raw.jsonl)與[原檔 hash／行號](harness-gap-closure-hook-sources-evidence/model-context-source.json)。判定 → **本機本案的生命週期／合約／副作用行為通過；不是完整 V03 或 redelivery 通過。**

| 實際生命週期 | 同 thread 的原生 turn | 觀察與判定 |
| --- | --- | --- |
| thread/start 後首次授權 | `01a173da-e371-7841-9be9-a9fffbb30159` | 兩個 SessionStart、一個 UserPromptSubmit、一個空 entries Stop 皆 completed；模型完成 T1／T2，T3 pending |
| server 退出後真正 thread/resume | `01a173dc-741b-7701-888e-4e13581ad54c` | 相同四項 hooks completed；沿用 T1／T2、T3 pending，不派新 worker |
| thread/compact/start | `01a173dd-5412-7382-8270-e6e96837f420` | 真 contextCompaction item `01a173dd-5430-7163-be68-541a4a851fc8` completed；不是新任務或授權 |
| compaction 後明確續作 | `01a173dd-e548-7cc2-b65e-b758d04addc1` | 相同四項 hooks completed；同合約 T3 done、整份 done，沒有重寫 canary／重派 |

唯一主責 thread 為 `01a173cd-be30-7950-92b2-c494bdeb7f33`。server1 PID 5704、server2 PID 14406，controller PID 5695，外層 exec session 36240；全部已終止。controller 在 slot 放行前保留原 thread 等候；期間沒有模型回合。compaction 的觀測視窗曾逾時，持續讀相同 handle 後取得終態，沒有重開。此次三回合沒有 429。

唯一產品 worker `/root/g06_preserve`，native agentThreadId `01a173db-f8b7-7b41-86f2-d02e62de4764`，subAgentActivity 真 started／completed，開始 metadata 為 gpt-6.1-sol／low。恢復後原 worker 不在當前 list，但先前完成證據仍存在；模型如實沿用而沒有重啟。另有四個原生 auto_review guardian sessions，source 與產品 thread_spawn 明確不同；不把它們算成產品派工，也不隱藏其存在。[安全來源索引](harness-gap-closure-hook-sources-evidence/session-index.json)列出所有六個 session 的來源、原 hash、保留與省略行。

模型以原生 shell `noclobber` 寫入 9 bytes `G06_ONCE\n`；三階段 ledger bytes 和 mtime_ns 都相同，唯一合約沿用同 task_id。[canary 原生命令索引](harness-gap-closure-hook-sources-evidence/canary-command-index.json)保留所有含 ledger 的完整命令及 RPC 行號，可區分產品寫入與合約文字／ls。[最終合約快照](harness-gap-closure-hook-sources-evidence/final-artifacts/docs/plans/g06-lifecycle.task-contract.md)、[green checker](harness-gap-closure-hook-sources-evidence/green-check.json)與[總結](harness-gap-closure-hook-sources-evidence/summary.json)支持讀回；不是只看模型自述。原設定、AGENTS、preserve、hooks 與全域 auth/config hash 未變：[前後 hash](harness-gap-closure-hook-sources-evidence/preservation.json)。canonical Stop 皆空 entries，只有三個 caller turn/start，沒有自動 continuation。

根 session 保存 9 條與 canonical echo 完全相符的 developer messages：每階段 PS SessionStart、TH SessionStart、TH UserPromptSubmit 各一條。方法時序證明經過真正 start／resume／compact，但公開 hook/run notification 沒有原始 stdin `source`；因此 **raw startup／resume／compact 值仍未知**，不能將設定來源 `project` 或 caller 可填值冒充。run.id 會跨生命週期重複，需搭配 startedAt／turn／方法時序；相同 run.id 也不足以證明同邏輯 event redelivery。測試 input 由控制器承載既有使用者授權，native UserPromptSubmit 與 developer 角色可觀察，但宿主未提供「真人鍵盤輸入」來源證明；不把控制器訊息自稱正常人類輸入來源已驗證。

## 公開證據、維護與清理

完整含 creator identity 的 session 原檔保留在 repo 外 0700 私有 state，待獨立 review；Git 的 `.excerpt.jsonl` 只省完整 session_meta 行，其他所有 parent／worker tool calls、outputs、turn 與 hook context 行按 byte 保留，沒有取 head／tail。guardian 原檔亦留私有 state，Git 只保留安全來源索引。每份公開 excerpt 都有原 full-file SHA-256、原行號、精確省略索引與理由，不能當成完整 raw。產品／worker 全部 toolcall 的公開證據仍可供核對無重派。

plugin/list 的無關遠端 catalog 含簽名圖示 URLs，原完整 RPC／catalog 留私有 state；公開 startup RPC 僅將其 id=4 的唯一 response 明確改標 redacted，其餘行 byte 不變。[移除理由、原 hash／路徑](harness-gap-closure-hook-sources-evidence/catalog-redaction.json)與[最小 installed 摘要](harness-gap-closure-hook-sources-evidence/plugins-summary.json)保留來源。resume RPC 沒有 catalog response，保持原樣。第一個 ignored-override preflight 也有相同透明處理。

[封存 self-check](harness-gap-closure-hook-sources-evidence/archive-selfcheck.json)核對固定 native 行不變、catalog marker 只留私有原檔，以及所有非 metadata session 行與完整原檔一致。[現有案例重播拒絕](harness-gap-closure-hook-sources-evidence/replay-refusal.json)亦在任何新 server／模型建立前失敗。controller 新增的封存步驟只整理驗收輸出，不重跑模型；checker 可用 `python3 check.py final-artifacts /private/tmp/g06-native-puuxg0nl/project` 從公開快照驗證原 project_root，不必有私有 state 或認證。

兩個 native server 均 exit 0，OS exact PID 查核無列；worker completed，background terminal list 空。確認後刪除兩案 auth 複本，保留 case/state／原身分與私有 raw；[清理證據](harness-gap-closure-hook-sources-evidence/cleanup.json)。包含 tokens.account_id 實值比對的 [auth scan](harness-gap-closure-hook-sources-evidence/authscan.json)僅記 key/path，不保存值；公開證據無匹配。未跑 full suite、Desktop、Windows、shell replay 或 continuation 變體；沒有改產品／central／demo／歷史 driver，沒有 push／PR。

同事件 native re-entry 仍受阻：最小解鎖條件是宿主公開可用的重送控制，及兩次實際 hook runs 可關聯同一邏輯 event 的證據。兩個不同 handlers、同 payload、另一 prompt、新 resume 或 shell replay 都不足；本案不改 Codex 本體或外部服務換取此能力。Windows 已明確排除，沒有測試；不新增 continuation 或 replay 變體。
