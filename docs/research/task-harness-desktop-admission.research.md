# Desktop 有界接點驗證：接入預檢結果

日期：2026-10-25。結果：接入受阻，沒有啟動 trial。這次使用者已明確授權，不再把試行授權不足列為本次阻礙。

## 授權及實際用量

允許在可丟棄測試專案接入 0.2.0 候選，最多一個 Desktop 新對話、一個使用者工作回合及一次 hook 補救；不修改產品、不購買資源、不要求人工觀察。若接入不能保持全域設定、日常啟用版本及快取不變，停止該接入。

實際建立對話 0、模型回合 0、hook 補救 0；尚未建立測試專案或探針。沒有呼叫設定寫入、plugin 安裝、啟用或快取修改。已授權額度尚未使用。

## 直接證據

- 重新核對來源與已存在候選；0.2.0 manifest 指紋仍為 `3d7924929d77a659a7b67237e147f6d8150b5f10146da0e5086e8b08e348b9d5`。
- 原生 `list_projects` 可讀取既有專案。`create_thread` 能以既有 project ID 或 projectless directory name 建立對話，沒有公開的本次 session hook 信任／設定覆寫參數。不能假設建立對話本身會完成候選接入。
- 唯讀解析本機使用者設定，hooks 已啟用；現有精確 hook 定義的 `trusted_hash` 紀錄存於 `~/.codex/config.toml` 的 `hooks.state`。本次沒有寫入該檔，也沒有將其他 hook 的信任套用到候選。
- [官方信任規範](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks)要求非 managed hook 先審查並信任目前定義；新／變更的 hook 在信任前會跳過。[專案載入規範](https://learn.chatgpt.com/docs/hooks#where-codex-looks-for-hooks)另要求專案 `.codex/` layer 受信任。
- 嘗試以 Computer Use 唯讀確認 Desktop 入口時，工具直接回覆：`Computer Use is not allowed to use the app 'com.openai.codex' for safety reasons.` 沒有取得畫面或進行 UI 操作，亦未改用其他技術繞過此限制。

數量、候選指紋、觀察時設定指紋與工具拒絕文字保存在[預檢證據](task-harness-lifecycle-evidence/desktop-admission-preflight.json)。不保存使用者完整設定、其他專案清單或私人對話。設定指紋是本次觀察快照，不冒稱為整輪開始／結束的雙快照比對。

## 結論與停止條件

目前可用介面未能建立「只在測試專案接入、完成必要信任、保持使用者層設定與日常配置不變」的受支持路徑，符合使用者要求的接入停止條件。這不是候選 hook 行為測試失敗，也不是使用者未授權，更不能推論所有 Desktop 版本都沒有專案級信任能力。

不手填 trust hash、不使用 bypass-hook-trust、不借用 managed hook 身分、不改全域設定，也不以 CLI 測試冒充 Desktop。保留 H01–H04 成果；H05 的事件與原使用者回合鏈仍未取得證據。

要接續，需要可用且受支持的專案／session 級信任接入方式，或使用者另行改變目前接入限制。現有授權本身不會被重複詢問；若未改變範圍且接入條件成立，可使用尚未消耗的一個對話／回合額度。
