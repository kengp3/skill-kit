# H05A 正常 CLI hook 接入與信任唯讀盤點

日期：2026-10-25。範圍：Codex CLI 0.164.0；只讀主 repo 規格／計畫與官方文件／公開原始碼。未啟動 Codex、app-server 或模型，未讀私人登入內容，未修改全域設定，未手填 trusted_hash、未 bypass。調查原稿位於暫存目錄；主責於實作階段封存本副本，內容仍只描述查證當時的唯讀結果。

## 結論

有正常的 CLI `/hooks` 審查／信任流程；原始碼支持以所選 user config 路徑保存信任。將獨立 CODEX_HOME 作為本次子程序的設定／狀態根目錄，是最小候選接入方式，不需另建信任框架。但「可在無私人憑證複製的測試目錄完成正常信任，再供 app-server 使用」尚未實測，不可標成已通過。

## 已確認事實

1. 官方 Hooks 文件要求審查並信任精確 hook 定義，CLI `/hooks` 是正式入口。plugin 已安裝／啟用不等於 hooks 已信任。
2. 公開版本 rust-v0.164.0 解參照為 commit `6aaac694803004a63c6f393d153c96d22521a6b9`。該版 TUI 有 Hooks slash command；hooks_rpc.rs 的原生 write_hook_trusts 動作呼叫 ConfigBatchWrite，file_path=None、reload_user_config=true。這是原生 UI 動作的實作證據，不是授權直接模仿該 RPC 寫入 trust hash。
3. 同版 ConfigManager 的 user_config_path 由 loader_overrides.user_config_path(codex_home) 決定；config_manager_service 的 file_path=None 使用該路徑。因此正常信任動作與選用的 user config 根目錄有直接關聯；實際路徑仍應於 admission 讀回確認，不能假定所有設定都已隔離。
4. 官方支持單次 `-c`／`--config` override，以及 CODEX_HOME 設定／狀態根目錄。Override 適合一般測試設定，不等於信任動作，也不取代系統／managed policy。
5. file credential storage 使用 CODEX_HOME/auth.json。公開原始碼的 direct keyring key 也衍生自 canonicalized codex_home 路徑；core AuthConfig 接收同一 codex_home。新目錄不能被假定會自動沿用日常登入。
6. 官方提供 file/keyring/auto/ephemeral credential store；ephemeral 僅當前 process 記憶體，不代表兩個不同程序可共享登入。本文沒有查詢或使用任何現有 token。

## 建議最小接入路徑（尚未執行）

1. 使用一個可丟棄父目錄，分開放測試專案、測試 Codex state 與證據。只寫入必要測試設定，不複製日常 config、auth.json、session、plugins cache 或 trust state；不使用 symlink 指向它們。
2. 對本次子程序傳入 CODEX_HOME；不變更 shell profile、全域環境或目前日常宿主。使用一般非持久 override 調整測試需要的參數。新目錄並不排除系統／managed config，須保留相關來源可觀測性。
3. 在允許啟動 CLI 的階段，先只做原生 `/hooks` admission：列出精確候選 handler／來源，走正常審查信任，讀回 native trust status 與寫入位置。不送模型任務；若登入／onboarding 阻止進入，當場記錄該單一阻礙，不改成偽造信任或 bypass。
4. 接著以同一測試 state 根目錄、相同候選／來源身份，讓 stdio app-server 讀回 hooks/list。只有實際顯示正確來源、hash 與 trusted，才算接入資格；TUI 信任成功不自動證明另一來源／路徑的候選受信任。
5. 模型執行前另處理正常認證。不讀取或複製私人 token，不將測試 keyring 指向既有 credential key。必要時使用正常、明確授權的登入流程；是否需要一次使用者登入／信任動作應如實揭露，不能把「不需人工監看 trial」誤解成可代替使用者接受安全信任。

## 尚需實測／不可宣稱

- 全新測試 CODEX_HOME 是否在未登入時就能進入 `/hooks`；onboarding 的實際前置條件。
- 原生信任後究竟寫哪些檔案，以及是否只寫本次測試範圍。
- TUI 審查的候選與後續 app-server 所見來源身份／hash 是否完全一致，含 session override 或 project layer 差異。
- 子程序 state 根目錄是否完整傳遞，managed policy 是否允許所選接入；一般 override 存在不能證明任何欄位都可覆寫。
- 測試認證如何在不複製私人憑證、不改日常登入狀態的限制下建立。新 state 與 ephemeral 不是自動認證解法。
- 正常信任由誰操作與可否在當前授權範圍完成。不可用 agent 自填 trusted_hash 或直接仿造 write_hook_trusts 代替審查。

## 最小下一步

只準備必要的 admission 接線與前後路徑／來源紀錄；待允許啟動 CLI 後，做一次不送模型任務的原生 `/hooks` admission，先回答「可進入、可正常審查、只寫測試 state、可由 hooks/list 讀回」四件事。任一不成立就留下具體阻礙，不拓展 Desktop、OS、daemon 或控制框架。C0 事件及補救驗證仍另計。

## 來源

- [官方 Hooks：正常審查信任](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks)
- [官方單次 overrides 與 CODEX_HOME](https://learn.chatgpt.com/docs/config-file/config-advanced#one-off-overrides-from-the-cli)
- [官方 credential storage](https://learn.chatgpt.com/docs/auth#credential-storage)
- [固定版本 TUI hooks_rpc.rs](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/tui/src/hooks_rpc.rs#L58-L99)
- [固定版本 ConfigManager 路徑](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/app-server/src/config_manager.rs#L164-L166)
- [固定版本 config 寫入路徑選擇](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/app-server/src/config_manager_service.rs#L219-L232)
- [固定版本 auth storage](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/login/src/auth/storage.rs#L258-L266)
- [固定版本 AuthConfig](https://github.com/openai/codex/blob/6aaac694803004a63c6f393d153c96d22521a6b9/codex-rs/core/src/config/auth_keyring.rs#L20-L28)

本盤點未執行接入或 trial；公開來源支持的是候選流程，並非本機實際資格通過。
