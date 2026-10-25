# T02：新專案統一設定與基本任務

**What to build:** 獨立使用 project-setting，或明確包含 task-harness，依提供規格建立單一 Markdown 設定並完成基本任務。

**Blocked by:** T01

**Status:** done

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] project-setting 無 task-harness 專用邏輯，依通用規格介面操作。
- [x] 提供 task-harness 設定規格與範本；分類表為合約與收據的唯一路徑來源。
- [x] 初始化後正常讀回並完成小任務，保留無關內容與寫入邊界。

## 證據要求

A、B 實際 agent 紀錄、規格來源、設定前後對照、合約與成果。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

## T08 最終對帳

A standalone、B 基本任務及 repaired copied-skill 接線都有真實 agent／產物。最終候選補驗缺 schema_version 自動修復，保留分類列空白／順序、自訂區塊與模型預設；受限 matcher 唯讀診斷不擴大範圍。generic project-setting 無專屬 harness 邏輯；單一設定、兩列路徑、唯一合約及無關內容保留已核對。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
