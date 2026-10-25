# G03：V01 正常持久 hook 信任

日期：2026-10-26（Asia/Taipei）。**驗證狀態：通過。** 正常人工精確審閱／CLI 信任後，同一 state 的兩個全新 invocation 均完成真實模型任務、保留信任，且固定提醒實際進入 developer 訊息。

## 預期與目前觀察

預期：使用者在正常介面審閱精確 hook 定義；不 bypass、不改信任資料庫；同一專用 state 的兩個 invocation 各完成小任務，均保存持久信任、實際提醒與終態證據。

本案在 demo 現行語意的獨立 case，原樣保留 AGENTS、project-setting、專案 hooks/config，從凍結 0.3.0 候選複製四個 skills 的 21 個非 scripts 資源並核對。候選 manifest SHA-256 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`；exact hooks 檔案 SHA-256 `34ea12d470060c9a974d04efcbeca15dc9b97593731391282ea3b5afc681105f`。全部定義與原 currentHash 保持不變。

## 正常審閱、信任與生命週期

[人工審閱包](harness-gap-closure-persisted-trust-evidence/human-review.md) 是核准前的歷史快照，保留原 exact JSON／hash，不覆寫其中的待核准文字。使用者回覆「已審閱，同意正常信任這五項精確定義」，由 root 轉交此明確授權；[授權來源](harness-gap-closure-persisted-trust-evidence/human-approval.json) 限定本 state 的五個固定 echo 定義。

核准後先逐 byte 核對 exact 檔案並以原生 hooks/list 確認五個相同 currentHash 仍 untrusted；對原 PID `98889`／exec session `49562` 做無按鍵 redraw，確認正常 Hooks browser。才執行 `write_stdin` 的 `chars="t"`，UI 隨即移除 review 警告並顯示 active。輸入／實際 result chunk ID 與前後 raw 指紋見 [正常信任操作配對](harness-gap-closure-persisted-trust-evidence/normal-trust-operation.json)，不是派生摘要或 API 信任。隨後正常退出原預備 TUI（exit 0，PID 已不存在）；它不計入後續兩次 invocation。

project trust 只啟用專案設定 layer；hook trust 另由這次正常 UI 產生，並由 [正常信任後專用 config](harness-gap-closure-persisted-trust-evidence/isolated-config-after-normal-trust.toml) 及前後 hooks/list 佐證。全程沒有 bypass、直接寫信任資料庫、Desktop CUA 或 AppleScript。case `/private/tmp/g03-persisted-trust-case` 與 state `/private/tmp/g03-persisted-trust-state` 都保留；第二次 completed、全部命令項目及兩個 server 真正退出後才刪除本案 auth 副本，清除後仍可唯讀查得五項 trusted。全域 auth/config 指紋前後一致，demo 未操作。

## 兩次全新 invocation

兩次均透過原生 `app-server --stdio`、同一原 state、`ephemeral=false`、`gpt-6.1-sol/low`；沒有共享 daemon。三個 HOME user skills 仍 disabled，四個 candidate repo skills enabled；instructionSources 只有本 case 的 AGENTS.md。每次輸入明確 pin 本 case 的 task-harness；核心流程由模型及原生 shell 完成，維護者 Python 控制器只調度、存證及讀回。

| Invocation | PID／thread／turn | 成果與合約 | 實際注入與終態 |
| --- | --- | --- | --- |
| 1 | `32723`／`01a17442-8ea7-7173-8d1d-3a21b7321c70`／`01a17442-8ec5-7e30-ba57-2be524c80925` | 精確 `G03_INVOCATION_1_OK` 加一 LF，20 bytes；唯一 `g03-invocation-1` 合約 done | 原 session 第 12、13、16 行為三則 developer 提醒；RPC 第 27、28、30、513 行為兩個 SessionStart、UserPromptSubmit、Stop completed；turn completed、server exit 0 |
| 2 | `33015`／`01a17443-8f87-72b1-b14c-fb92c15907bc`／`01a17443-8fa3-7af2-b8be-465ebd5b4cd4` | 精確 `G03_INVOCATION_2_OK` 加一 LF，20 bytes；唯一 `g03-invocation-2` 合約 done | 原 session 第 12、13、16 行為三則 developer 提醒；RPC 第 27、28、30、452 行為同四個 hook completed；turn completed、server exit 0 |

每次前後的 hooks/list 都是五項 trusted、相同 currentHash 及唯一 case sourcePath；完整識別、對應行號與獨立核對見 [observed-check.json](harness-gap-closure-persisted-trust-evidence/observed-check.json)。兩次分別完成一個新小任務，各任務恰有一份合約，並非同任務重建 tracker。成果與合約 bytes 在 [final-artifacts](harness-gap-closure-persisted-trust-evidence/final-artifacts/docs/plans/g03-invocation-1.task-contract.md)，第二份 [合約](harness-gap-closure-persisted-trust-evidence/final-artifacts/docs/plans/g03-invocation-2.task-contract.md)；精確成果分別見 [1](harness-gap-closure-persisted-trust-evidence/final-artifacts/docs/research/g03-invocation-1.research.md)、[2](harness-gap-closure-persisted-trust-evidence/final-artifacts/docs/research/g03-invocation-2.research.md)。

## 證據與判定

| Expected | Observed | Raw | Verdict |
| --- | --- | --- | --- |
| 凍結候選與 demo 現行來源一致 | manifest 與 21 個非 scripts 資源逐檔核對；demo 四個基底檔 SHA 相同 | [preparation.json](harness-gap-closure-persisted-trust-evidence/preparation.json) | 前置通過 |
| 禁用 HOME 技能，原生載入本案四技能 | skills/list 確認三個 user disabled、四個 repo enabled | [skills-before.json](harness-gap-closure-persisted-trust-evidence/skills-before.json)、[plugins-before.json](harness-gap-closure-persisted-trust-evidence/plugins-before.json) | 前置通過 |
| 正常 exact-definition 人工信任 | 使用者明確核准；原 TUI 正常 `t` 信任；相同五 hash 從 untrusted 變 trusted | [核准前 native 狀態](harness-gap-closure-persisted-trust-evidence/pre-approved-trust/hooks-list.json)、[前後操作 raw 配對](harness-gap-closure-persisted-trust-evidence/normal-trust-operation.json)、[首次新 invocation 信任](harness-gap-closure-persisted-trust-evidence/invocation-1/hooks-before.json) | 通過 |
| 同 state 兩次全新 invocation 的提醒、hook events、成果與 completed | 新 PID／thread 各一次；五項信任持續；實際 developer 與 native events 可關聯，各自合約／精確成果驗收 | [兩次原生結果](harness-gap-closure-persisted-trust-evidence/run-result.json)、[獨立事件及完整私有來源比對](harness-gap-closure-persisted-trust-evidence/observed-check.json) | 通過 |
| 日常 auth/config、case 基底保留及 owned auth 收尾 | global／case 基底前後 hash 相同；全部程序／工具終態後刪除本案 auth；state 保留且仍 trusted | [cleanup.json](harness-gap-closure-persisted-trust-evidence/cleanup.json)、[清 auth 後 hooks/list](harness-gap-closure-persisted-trust-evidence/post-auth-cleanup/hooks-list.json) | 通過 |

## 離線核對、透明匯出與限制

[維護者 driver](harness-gap-closure-persisted-trust-evidence/native-persistence.py) 沿用已核准的 G01 原生 stdio seam；檢查在真實任務前因缺少成果而 [red](harness-gap-closure-persisted-trust-evidence/persistence-red.stderr)，取得兩次真實結果後 [green](harness-gap-closure-persisted-trust-evidence/persistence-green.json)。另以 [唯讀獨立核對器](harness-gap-closure-persisted-trust-evidence/verify-observed.py) 關聯 native hook／developer 訊息／turn ID、核對 public excerpt 逐 bytes 等於 private source，並用「移除 developer 提醒」「將 completed hook 改為 failed」兩個負向控制確認會拒絕。它不啟動模型或預填 observed。

完整 RPC 在各 invocation 的 rpc.jsonl；公開 session 只省略含帳號身分可能性的完整 session_meta 行，其他行原 bytes 保留：[invocation 1 index](harness-gap-closure-persisted-trust-evidence/invocation-1/session-excerpt-index.json)、[invocation 2 index](harness-gap-closure-persisted-trust-evidence/invocation-2/session-excerpt-index.json) 列出完整來源 hash、被省行 hash 與原行號。私有原始 session 留在本案 0700 state，完整維護 RPC 留在 `/private/tmp/g03-persistence-private`（0700），auth／account ID／credential token 值不進 Git。沒有歸檔整段協調 agent 對話。

兩個模型回合首次 sandbox-exec 在命令開始前失敗，依已明確授權使用 scoped require_escalated 完成必要原生命令；錯誤及重試均保留。兩個 stderr 各 827 bytes，記錄可選 xcodebuildmcp 啟動／關閉失敗與 sandbox violation；在這兩份實際 stderr 檔未見 429／retry／reconnect 行，不能外推服務沒有遇過 429。沒有呼叫這個可選 MCP。Stop 僅正常 `{}`，無阻擋或新授權；SubagentStart 未觸發（任務禁止子代理），本案只證明其定義信任持久，不宣稱其事件已執行。Windows、Desktop、跨 state／帳號信任與其他缺口不由 V01 外推。

官方依據：[Hooks — Review and trust](https://learn.chatgpt.com/docs/hooks)（本次已讀取）：非 managed 定義需審閱，信任綁定目前 hash，`/hooks` 提供正常信任介面。此說明支持試驗方法，不替代本案實際信任證據。

未執行額外模型試跑或完整 suite；本案 auth 副本已刪除，保留無 auth 的信任 state 與私有完整 raw 供覆核。
