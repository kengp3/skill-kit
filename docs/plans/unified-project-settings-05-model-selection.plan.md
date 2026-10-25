# T05：模型設定與正常派工

**What to build:** 依任務、角色、階段與專案規則選擇模型，記錄請求與實際執行者。

**Blocked by:** T02

**Status:** done; native model and task lifecycle verified

依據：[實作規格](../specs/unified-project-settings.spec.md)。使用者已確認 T01–T08 拆分與依賴。

## 驗收條件

- [x] 四預設階段及自訂階段，無固定全階段或模型要求。
- [x] 支援分號模型清單與既定選擇優先序。
- [x] 主責不自動切換；後續繼承跟隨最新對話選擇，既有 agent 維持原設定。
- [x] 單次指定僅存合約，同任務恢復有效，新任務不沿用。

## 證據要求

F 正常派工的設定、來源、實際 agent／模型與任務範圍對照。

狀態更新只能依實際成果；調查、離線測試與真實行為驗收分別判定。

## 開發階段紀錄（後續結果見 T08）

已補齊模型選擇 reference 與派工入口，包含正常優先序、階段與角色對應、主責繼承、單次覆寫及請求／觀測結果紀錄。候選不可用流程保留獨立區段供 T06 補齊。

本地連結、空白與 diff 檢查通過。經實際建包與 manifest 驗證確認新 reference 及入口一同發行；這只驗證封裝邊界，不代表模型已依規則派工。F 正常派工、途中手動切換及跨任務範圍的真實 agent 驗收仍待整合驗證，以上驗收條件暫不勾選通過。

## T08 最終對帳

11 案真實模型政策判讀、角色優先於階段的原生派工與 host turn_context 已取證。最終候選的三回合案例證明覆寫只存合約、同任務恢復仍用 gpt-6-sol、新任務使用專案預設且長期設定不變。同一 native thread 由下一 user-turn 明確切換主責模型／強度，舊 worker 保留原 session 及設定，新 worker 省略參數後繼承新選擇；Desktop 模型選單 UI 本身未測。

詳見[實際 agent 與整合驗收](../research/unified-project-settings-acceptance.research.md)及其中來源、raw、產物與未驗證清單。
