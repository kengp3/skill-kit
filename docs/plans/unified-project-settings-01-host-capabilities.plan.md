# T01：宿主 hooks 與模型派工能力驗證

**What to build:** 辨識無必要腳本接入、事件與子 agent 模型指定能力，產生可用性與限制的直接證據。

**Blocked by:** None (can start immediately)

**Status:** done; capability investigation and native evidence reconciled

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] 在隔離環境查核載入、信任、真實觸發、續作與使用者停止。已分別記錄載入／信任狀態、真實提醒、被動 Stop 限制及 native API 停止／明確續作；正常持久信任與 Desktop UI 未測，調查結果不冒充能力通過。
- [x] 查核模型／強度、角色優先序、可觀測結果與未知啟動查核能力。已取得原生回合、角色／強度、真實回退／耗盡及 API 模型切換生命週期；已知 handle 先查終態，真正未知 child 網路故障保留 H7 未驗證。
- [x] 可用、不可用、未驗證分列；調查完成不等於未驗證能力通過。

## 證據要求

宿主版本、原始事件／派工結果、agent 身分、H1–H8 能力表。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

調查結果：[宿主能力報告](../research/unified-project-settings-host-capabilities.research.md)。初次隔離 state 缺認證，主責補充已認證原生 smoke 成功；hooks 仍為 untrusted；H1–H8 的剩餘實際行為驗收由後續 tickets 保留，不因 T01 調查完成而標成通過。

## T08 最終對帳

原生載入／信任狀態、固定提醒真實注入、模型／強度／角色、候選拒絕／耗盡與回退已核對。補充驗收另證明 native API 使用者 Stop、同合約續作及主責模型切換後舊新 worker 的行為。正常持久信任、Desktop UI、native hook 重入與真正未知 child 跨網路斷線仍分列未驗證；調查完成不代表這些能力通過。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
