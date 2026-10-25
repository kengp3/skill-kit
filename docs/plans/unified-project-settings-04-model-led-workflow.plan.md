# T04：無腳本必要依賴與 hooks 接手

**What to build:** 模型依同一合約與規則推進任務，hooks 失效與恢復時連續執行。

**Blocked by:** T02

**Status:** implemented-pending-verification

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [ ] 所有 runtime script 與外部輔助工具停用後，核心仍完成任務。
- [ ] 標準 hooks 接入與四個檢查時點一致；修復不成功自動接手。
- [ ] 恢復不重播副作用或派工；未知先查明、條件改變才重驗。
- [ ] review helper 無間接必要依賴；維持停止、授權、唯一合約及實際驗收。

## 證據要求

D、E 的停用證據、真實軌跡、合約、操作次數與成果。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

## 實作與驗證紀錄

已更新主技能的四個共用檢查時點、失效接手與恢復規則、合約身分與證據界線，以及 review 的選配 hash checker。文件連結、範本 JSON 與 diff 檢查通過；真實 D／E 驗收由整合回合取證，尚不勾選已通過。
