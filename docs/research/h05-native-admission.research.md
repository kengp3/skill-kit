# H05A 原生 hook 接入驗證（無模型）

日期：2026-10-25；Codex CLI 0.164.0。本次只完成登入及原生信任讀回，不執行 C0 或其他模型案例。

## 結果

使用者授權測試目錄的 ChatGPT device login 後，原生登入程序回報 `Successfully logged in`，exit 0。登入資訊只由原生程序保存至本次 `CODEX_HOME`；未讀取、複製或封存 auth 內容／一次性代碼。

在該測試 state 下，以 CLI `--no-daemon --no-alt-screen` 進入正常 `/hooks`。逐一檢視精確來源、命令及 timeout，再透過原生介面信任 SessionStart、UserPromptSubmit、Stop。最終畫面三者均為 Installed 1／Active 1；正常 `/quit` 後程序 exit 0。

接著獨立啟動同一測試 state 的 stdio app-server，只送出 `initialize`、`initialized`、`hooks/list`。讀回三個指定 project hooks，全部 `enabled=true`、`trustStatus=trusted`，warnings／errors 為空；currentHash 與測試 config 的原生信任紀錄一致。結束自有 app-server 後 exit 0，沒有 `thread/start` 或 `turn/start`。

機械證據：[接入摘要](task-harness-lifecycle-evidence/h05-native-admission.json)。摘要只含測試路徑、hook 定義／雜湊、設定前後雜湊與有限觀測，沒有登入資料。

## 範圍與限制

- 測試根：`/private/tmp/h05-admission-5tpyvaik`。project、state、candidate 與 evidence 分開；沒有覆寫日常設定或啟用版本。信任由正常 UI 寫入測試 state，未手填 trust hash 或使用 bypass。
- 測試命令使用凍結 0.2.0 的 handler 複本；已確認 handler bytes 與 0.2.1 一致。這次是 project hooks 的正常接入，不是 plugin discovery、完整套件或 skill 載入驗收。
- `hooks/list` 證明載入及信任，尚不證明 Python handler 真正執行、三事件 payload、模型遵循、原始回合識別、一次補救或原生取消成立。
- 日常 `/Users/kengp3/.codex/config.toml` 前後 SHA-256 一致。這是單檔比對，不是所有全域寫入的完整監測證明。
- 測試 state 的 sessions 目錄沒有 JSONL 紀錄；不能用缺少紀錄反推模型零活動。沒有送出模型任務的依據是本次操作序列及 RPC method 範圍。
- 原生信任限於此次精確來源及命令；後續 probe／candidate 路徑不同時須重新正常審查，不能轉移本次 hash。

## 後續

登入與正常信任的接入阻礙已解除。下一階段仍須完成實際候選／probe 的精確接線與正常信任、固定輸入及控制準備；取得新模型執行授權後才可執行 C0。H05A 維持 in_progress，H05B／H05C 未開始。

使用者已決定先停在本次無模型成果。獨立 Spec 複核另讀取暫存原始 hooks/list 並比對 handler bytes，確認本報告與直接證據一致；沒有新增 findings。


## 完整 0.2.1 候選接入與停用（2026-10-25）

使用者解除第 1 項的唯讀限制後，在同一可丟棄測試範圍完成完整套件接入；沒有模型 trial。前述 handler 複本預檢是歷史階段，以下才是完整候選載入證據。

1. 將凍結 0.2.1 複製至測試專案，重用 repo 的 marketplace 格式，僅在測試副本指定候選路徑。先停用早期 project hook 定義以避免重複載入。
2. 原生 `plugin/read` 可辨識四個 skills 及三個 hooks；安裝前 `skills/list`、`hooks/list` 均沒有這個候選。
3. 使用原生 `plugin/install` 接入測試專用 CODEX_HOME，未要求其他 Apps 認證。`skills/list` 回傳四個啟用 skills，路徑全部位於 0.2.1 測試快取；三個 hooks 的命令也指向同一版本。
4. 安裝後快取經既有 package verifier 通過，manifest SHA-256 仍為 `210664eb7b5a478997dbc8c67b323131a5f9ed62bd51e23cdbaba8bdb7a8ae5a`。檢視三個精確定義後，透過原生 TUI 信任；重啟 app-server 讀回三者均 enabled／trusted，沒有 hook 載入警告／錯誤。
5. 只在測試 config 將該 plugin 的 enabled 設為 false；新 app-server 讀回 installed=true、enabled=false，啟用 skills 與 hooks 均為零。再透過原生 `plugin/uninstall` 收尾，確認 installed=false、enabled=false、兩份載入清單皆無候選，且該版本測試快取已移除。

原生 TUI 正常退出，所有本次自有 RPC 程序結束。使用者日常 config 前後雜湊一致；來源候選、日常啟用版本與其他專案未由本次操作修改。這不是所有全域檔案寫入的完整監測聲明。原生 TUI 另回報既有 xcodebuildmcp handshake 失敗；它不屬本候選，沒有擴展去修理該服務。

**接入範圍務必區分：** 原生 plugin install 的回傳 scope 是 user，位於本次測試專用 CODEX_HOME；不是原生「僅一個專案可見」的證明。產品任務啟用仍靠明確啟用及專案設定。此次測試不修改日常使用者 state，不把該安裝方式描述成可直接對日常全域無影響地安裝。

機械證據：[完整候選接入、停用與移除](task-harness-lifecycle-evidence/h05-full-package-admission.json)。原生結構依據重用 [Codex marketplace](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/marketplace.rs)；實際判定以本次 0.164.0 RPC、原生信任及套件內容驗證為準。

結論：收斂清單第 1 項「完整候選接入／停用」完成。未建立產品任務合約、未將 host 資格設為 true，C0 及後續實際 agent 行為仍未驗收；H05A／H05 不因此標 done。
