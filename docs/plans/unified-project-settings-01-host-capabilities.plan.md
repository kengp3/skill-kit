# T01：宿主 hooks 與模型派工能力驗證

**What to build:** 辨識無必要腳本接入、事件與子 agent 模型指定能力，產生可用性與限制的直接證據。

**Blocked by:** None (can start immediately)

**Status:** investigation-complete; host limits documented

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [ ] 在隔離環境查核載入、信任、真實觸發、續作與使用者停止。載入與信任狀態已取得；T08 補得靜態提醒真實注入，正常持久信任、條件續作與 UI 停止仍未驗證。
- [ ] 查核模型／強度、角色優先序、可觀測結果與未知啟動查核能力。已取得原生模型及子 agent 的回合、上下文、角色／強度及真實回退證據；手動切換與未知啟動的完整生命週期仍未驗證。
- [x] 可用、不可用、未驗證分列；調查完成不等於未驗證能力通過。

## 證據要求

宿主版本、原始事件／派工結果、agent 身分、H1–H8 能力表。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

調查結果：[宿主能力報告](../research/unified-project-settings-host-capabilities.research.md)。初次隔離 state 缺認證，主責補充已認證原生 smoke 成功；hooks 仍為 untrusted；H1–H8 的剩餘實際行為驗收由後續 tickets 保留，不因 T01 調查完成而標成通過。

## T08 最終對帳

後續整合已取得固定提醒的真實注入、原生模型角色與強度、候選拒絕及回退證據；正常信任、UI interrupt／手動模型切換仍未驗證。T01 是能力調查完成，不把未測的宿主能力改成通過。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
