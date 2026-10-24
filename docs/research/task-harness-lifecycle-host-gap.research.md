# 必要 hook 的宿主資格缺口

日期：2026-10-25。唯讀查核；沒有模型 trial、app-server 對話、私人對話記錄或全域設定變更。

## 結論

原始使用者工作回合與 Stop 自動續作的識別仍未有直接證據，H05 未完成。Hook 為必要組件，不降為可選。此缺口不阻止來源與離線驗證開發，但阻止整套 Desktop harness 的完成宣告及自動補救資格啟用。

## 已取得的證據

- 受委派唯讀查核回報本機 npm CLI 為 0.164.0；這不是 Desktop 版本證據。已安裝內容主要是 JS launcher/native binary，未取得可直接閱讀的 hook 實作或 schema。
- [官方 UserPromptSubmit](https://learn.chatgpt.com/docs/hooks#userpromptsubmit) 列出 turn_id、prompt。
- [官方 Stop](https://learn.chatgpt.com/docs/hooks#stop) 列出 turn_id、stop_hook_active，並說明 block 產生 acts as a new user prompt 的續作提示。
- 文件未在本輪查閱內容中明確保證自動提示是否再觸發 UserPromptSubmit、是否沿用 turn_id、boolean 是否跨新 turn 保持 true，以及如何辨識真正使用者輸入。

## 設計影響

1. 不在 UserPromptSubmit 重置補救額度。
2. stop_hook_active=true 是拒絕再次補救的依據，不單獨宣稱整條鏈已受保護。
3. 收據以合約內的原始 user_turn_id 為識別；agent 不能因 hook 提示改寫成新使用者授權。資格必須另驗，合成設定不構成證據。
4. 三個 host 資格預設 false。缺乏可靠識別時，Stop 提供未就緒資訊而不要求自動實作，不稱為完整可用。

## 後續最小驗證（本輪不執行）

H04 通過後，取得有界 Desktop 試行授權與可用專案接入，只記錄一次合成任務的事件名稱、session/turn ID、stop_hook_active 及續作次數；驗證討論/取消/人工Stop不重啟。不得借此改全域設定或建立OS監控。若事件不提供可靠鏈路，記錄實際缺口並修訂 adapter，不能提高推測信心取代證據。
