# H03：低負擔的任務生命週期

Status: done（來源與離線範本驗證；實際 agent 行為驗收仍由 H05 處理）
Blocked by: None
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：使用者啟用後由主責 agent 維護唯一合約，推進、驗收、取消、接手、恢復及範圍調整都有明確且精簡規則。

- [x] 恢復舊 skill 任務閉環，保留新版風險/修復原則與已確認簡化。
- [x] 合約與專案設定範本跟 runtime schema 一致，host 資格預設未驗證。
- [x] Hook 必要、Python 依賴、專案 opt-in/信任/驗收指引、未知能力不假通過。
- [x] README 回到非侵入式任務管理，舊評測僅保留開發參考。

## 交付與查核

- `skills/task-harness/SKILL.md` 恢復以 `8ae9cda` 為基線的開始、依賴、委派、驗收、保存、恢復及收尾生命週期；移除固定兩次寫入、每次檢查計數及整組派完限制，保留自主修復與依風險驗證。
- [合約指南](../../skills/task-harness/references/task-contract.md) 提供完整專案 JSON 與 Markdown 合約範本；三項 host 資格預設 `false`，初始未綁定且僅討論，不授權產品操作。
- README 與技能入口同步；歷史規格／試行計畫只新增優先規格提示，原正文逐字保留。[用語](../specs/task-harness-glossary.spec.md)沿用專案來源。
- 2026-10-25：`git diff --check` 通過；Python 標準函式庫離線查核兩份 JSON 可解析、必填欄位、保守預設、17 個本地引用可達，並比對兩份歷史文件正文與 Git 基線完全一致。
- 用 H01 公開 CLI `task_harness.py --project-config <臨時設定>` 讀取本指南擷取的範本：保留 host 預設值時回傳 `required host identity/continuation qualification is unverified`；只在 TemporaryDirectory 將 `session_identity` 設為合成 `true` 後，`SessionStart` 回傳 `No active task is bound` 的條件式提醒；合約 bytes 不變、未產生收據。H01 實作者另獨立確認範本相容。

本 ticket 只有文件／skill 指示變更，未新增機械行為；採既定公開 CLI seam 驗證範本，不新增鏡射文字內容的測試。未安裝、啟用或刷新候選，未修改全域／其他專案／實際宿主設定，未執行新模型 trial。Python 3.10 相容性、Desktop 真實 hook 與模型遵循尚未由此驗證。
