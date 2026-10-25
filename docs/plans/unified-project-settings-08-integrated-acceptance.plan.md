# T08：完整行為驗收與收尾

**What to build:** 對整合候選完成 A–G 真實驗收、H1–H8 能力對帳與整合審查。

**Blocked by:** T07

**Status:** done; native acceptance and explicit validation limits recorded

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] 七組最低情境均有真實 agent 與產物證據；未驗證不冒充通過。
- [x] 停止、唯讀、恢復、未知副作用、獨立審查邊界保留。
- [x] 修復整合問題並完成 code-review，必要缺口保持未完成。

## 證據要求

版本化預期→觀察→證據→判定、檢查原始結果、review 與未驗證清單。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

## T08 最終對帳

A–G 各組有真實案例與產物，另補驗 B 格式修復／matcher、C 真實 I/O 失敗、F 任務覆寫生命週期／主責 API 切換／全候選耗盡，以及已開始工具的 native Stop／同合約續作。重跑既有證據核對原 39、模型 60、設定 59 項皆通過，Stop 另依 verification 與 raw 讀回。停止、唯讀、恢復、未知副作用與獨立審查邊界均有直接證據；H1–H8 保留正常信任、Windows、Desktop UI、真正未知 child 網路故障與 native hook re-entry 等未驗證範圍。三項 Spec P2 已修正並經原 reviewer 複查解除，Standards 無剩餘 finding。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
