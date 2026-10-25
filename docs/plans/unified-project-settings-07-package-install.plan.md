# T07：封裝與隔離安裝升級

**What to build:** 同步技能、Codex plugin 與指南，以隔離環境驗證全新安裝與舊版升級。

**Blocked by:** T03, T04, T06

**Status:** implemented-and-package-validated (full behavior acceptance remains T08)

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] 封裝及實際載入符合新設定與流程，不再必要依賴舊 JSON 或 Python handler。
- [x] 指南涵蓋首次設定、移轉、模型分工與失效接手。
- [x] 僅改隔離測試環境，保留其他既有專案及全域安裝。

## 證據要求

封裝驗證、載入來源／版本、安裝升級軌跡與環境前後對照。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

實際結果：[T07 封裝與隔離安裝報告](../research/unified-project-settings-package.research.md)。0.3.0 全新安裝與 0.2.1→0.3.0 升級均讀回正確來源；111 維護測試通過、略過 1。hooks 仍 untrusted，未把載入當作真實行為驗收。
