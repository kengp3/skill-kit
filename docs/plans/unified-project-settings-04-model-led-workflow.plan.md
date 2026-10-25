# T04：無腳本必要依賴與 hooks 接手

**What to build:** 模型依同一合約與規則推進任務，hooks 失效與恢復時連續執行。

**Blocked by:** T02

**Status:** implemented; core and recovery cases passed; UI stop unverified

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] 所有 runtime script 與外部輔助工具停用後，核心仍完成任務。
- [x] 標準 hooks 接入與四個檢查時點一致；修復不成功自動接手。
- [x] 恢復不重播副作用或派工；未知先查明、條件改變才重驗。
- [ ] review helper 無間接必要依賴；維持停止、授權、唯一合約及實際驗收。

## 證據要求

D、E 的停用證據、真實軌跡、合約、操作次數與成果。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

## 開發階段紀錄（後續結果見 T08）

已更新主技能的四個共用檢查時點、失效接手與恢復規則、合約身分與證據界線，以及 review 的選配 hash checker。文件連結、範本 JSON 與 diff 檢查通過；真實 D／E 驗收由整合回合取證，尚不勾選已通過。

## T08 最終對帳

核心無 helper 小任務、已安裝候選提醒注入、未知副作用先核對、修復後兩回合相同合約／一次寫入通過。選配 scripts 實際省略；不宣稱整台機器 interpreter 都移除。review helper 改選配有來源審查及無 helper 獨立審查；原生 UI Stop 未測，最後一項保留未完整驗證。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
