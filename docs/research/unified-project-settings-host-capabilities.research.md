# 統一設定改版：宿主能力調查

日期：2026-10-25。T01 調查範圍完成；本報告不是新版產品或 A–G 行為驗收通過證明。

## 本次直接觀測

- 本機為 Codex CLI `0.164.0`。原生 protocol schema 成功產生，包含 thread 的 model／reasoningEffort 回應、turn 的 model／effort 覆寫欄位及 hook 事件通知介面。這證明可用介面，不證明 provider 已按指定模型完成運算。
- 在全新隔離 state 建立唯讀的靜態 SessionStart handler：`echo UNIFIED_T01_STATIC_SESSIONSTART`。原生 hooks/list 列為 enabled、command、untrusted，無 warnings／errors；本次沒有觀測到 hook/started 或 hook/completed。不得把載入列舉當成真正觸發。
- 原生 thread/start 成功建立 ephemeral thread，回傳模型設定 `gpt-6.1-sol`、強度 `low`、session／thread 身分與 read-only sandbox。這是解析後設定，不是模型實際執行證明。
- 隔離 account/read 為 account=null、requiresOpenaiAuth=true。未複製登入資料，移除顯式認證環境變數。最小 turn/start 收到 turn ID 後，provider 回報 HTTP 401 Missing bearer/basic authentication；沒有成功模型輸出。回合終態未於觀測窗內出現，不將 inProgress 當作完成。關閉 stdin 後，自有 app-server exit 0。
- 主責 agent 補充一個隔離、已認證的原生最小回合：請求 gpt-6.1-sol／low，不要求工具；取得 thread.started、agent_message `CAPABILITY_PROBE_OK`、turn.completed，exit 0。這證明原生模型回合可成功，不證明子 agent、hooks 或新版任務流程；輸出未回傳實際 provider 模型／強度標籤，仍須區分請求與實際身分。此 probe 記錄全域 auth 未改變且暫存認證已清除；本報告保留主責提供的去識別輸出。
- 本次 thread/read 使用 includeTurns=true，宿主拒絕 ephemeral thread 的該選項。這是 protocol 使用限制，不是執行失敗的第二次派工理由；後續應使用支援的讀回方式。

## H1–H8 能力對帳

| ID | 目前判定 | 直接證據與後續處理 |
| --- | --- | --- |
| H1 | 部分可用；信任與觸發未驗證 | 靜態內建命令可列舉，原生狀態為 untrusted。正常信任及實際觸發留待 T08；不可用時走模型接手，不自動宣告信任 |
| H2 | 文件支援；本次實際注入／阻擋／續作／Stop 未驗證 | Stop 必須合法 JSON；固定提醒不能取代條件式判斷。補充的成功回合未接入候選 hooks，仍不能驗證 Stop |
| H3 | 部分可觀測；語意未驗證 | thread/start 與 turn/start 回傳各自身分；未驗證 hook 續作與真正使用者輸入的區分、去重或恢復 |
| H4 | 原生介面存在；實際子 agent 派工未驗證 | schema 支援模型與強度設定，thread/start 可回報解析值；沒有子 agent/provider 成功執行證據 |
| H5 | thread 層解析值可觀測；本次主對話手動切換未驗證 | 回應含 model／reasoningEffort；不從子程序設定推定目前 Desktop 對話或已運算模型 |
| H6 | 真實未認證失敗已觀測；模型不可用／強度不支援未驗證 | 初次 HTTP401 是認證問題，不得誤判模型不可用；補充認證後回合成功。模型／強度失敗類型仍留待 T08 |
| H7 | turn ID 可取得；未知啟動的完整查核未驗證 | 已知 turn ID、未觀測終態；不盲目重派。ephemeral/includeTurns 限制須納入後續 probe 設計 |
| H8 | 本次新隔離 state 原生讀回成立；新版安裝與升級未驗證 | state、project 均為暫存目錄，未操作全域安裝。候選尚未完成，安裝與升級須由 T07／T08 取證 |

## 對實作的結論

可先實作以模型為主的流程、單一合約及 hook 不可用時的自動接手，不必等待所有宿主能力皆可用。標準 hook 接入應保留，但須如實標示能力：SessionStart／UserPromptSubmit 的靜態內建命令可作上下文傳輸候選，不等同合約解析或機械攔截；本次列舉成功也未證明觸發。

固定 Stop 回應若無條件 block，沒有依輸入辨識既有補救回合的能力，不能宣稱有界一次續作。固定 `{}` 只可作合法的被動回應，不提供條件補救；主責模型仍必須主動執行收尾檢查。不得用換語言的 handler、MCP server 或外部 validator 補成必要依賴。

模型指派應保留請求設定與實際宿主結果。只有回應中的設定或模型自行宣稱不足以證明 provider 實際採用；無可觀測資料時記未核實。角色設定也可能優先於 spawn 參數，須以實際宿主結果判定。

## 原始證據與可重現邊界

- [版本](unified-project-settings-host-capabilities-evidence/version.json)、[原生 schema 摘要](unified-project-settings-host-capabilities-evidence/native-schema-excerpt.json)、[schema 產生結果](unified-project-settings-host-capabilities-evidence/schema-generation.json)。
- [已認證原生回合 smoke](unified-project-settings-host-capabilities-evidence/native-authenticated-smoke.json)；主責提供的補充證據，不是子 agent 或新版候選行為驗收。
- [完整 RPC](unified-project-settings-host-capabilities-evidence/native-rpc.json)、[摘要](unified-project-settings-host-capabilities-evidence/native-summary.json)、[server stderr](unified-project-settings-host-capabilities-evidence/native-server.stderr)、[開發端 probe](unified-project-settings-host-capabilities-evidence/probe.py)。
- probe 僅供維護者調查，不是技能日常依賴。每次產生新的暫存 state/project，不複製 auth、不變更全域設定或安裝。這是本次操作範圍說明，未執行所有全域檔案的前後 hash 稽核。
- RPC 紀錄包含此次真實失敗與未知終態；未修改原始輸出，未把失敗改寫為通過。已認證 smoke 有原生模型輸出，但尚無新版真實 agent 產物驗收結果。

## 官方資料核對

本次已搜尋並讀取 [Hooks](https://learn.chatgpt.com/docs/hooks)：目前 command／mcp_tool 可用，prompt／agent handler 解析後略過；非 managed hook 須信任精確定義。Stop 的 exit 0 stdout 要求 JSON，block 會建立續作回合，不能以固定純文字或無條件 block 宣稱安全的一次性補救。

[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) 說明模型與強度的繼承／指定，以及 custom agent 檔案的優先設定。這是文件能力，不是本帳號每個模型都可用的證據。

[App-server](https://learn.chatgpt.com/docs/app-server) 提供 thread、turn 與 hook 事件介面。本次本機產生的 schema 與 RPC 另行保存；文件、schema、載入、實際模型運算及產品成果分開判定。
