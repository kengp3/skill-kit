# T07：封裝與隔離安裝升級

**What to build:** 同步技能、Codex plugin 與指南，以隔離環境驗證全新安裝與舊版升級。

**Blocked by:** T03, T04, T06

**Status:** done; exact final candidate fresh and upgrade verified

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] 封裝及實際載入符合新設定與流程，不再必要依賴舊 JSON 或 Python handler。
- [x] 指南涵蓋首次設定、移轉、模型分工與失效接手。
- [x] 僅改隔離測試環境，保留其他既有專案及全域安裝。

## 證據要求

封裝驗證、載入來源／版本、安裝升級軌跡與環境前後對照。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

實際結果：[T07 封裝與隔離安裝報告](../research/unified-project-settings-package.research.md)。0.3.0 全新安裝與 0.2.1→0.3.0 升級均讀回正確來源；111 維護測試通過、略過 1。hooks 仍 untrusted，未把載入當作真實行為驗收。

## T08 最終對帳

最終 7e37d7… 候選另做原生全新安裝及 0.2.1→0.3.0 升級，四 skills／三 hooks 與 installed manifest 一致；canonical asset 與 plugin hooks 相同。後續三組補充亦核對同一最終 manifest，未改產品來源。112 維護測試通過、原生 Windows 1 項略過，正常持久信任不冒稱通過。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
