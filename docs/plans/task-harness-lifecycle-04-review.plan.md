# H04：整合驗證與證據對帳

Status: ready-for-agent
Blocked by: H01、H02、H03
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：對最終整合來源執行適用回歸與獨立 Standards/Spec review，修正後再驗受影響範圍；交付可稽核證據而非僅回報測試數量。

- [ ] 合約/事件/封裝公共接口與既有適用回歸通過，證據指向固定來源。
- [ ] Standards、Spec 分開審查並處理 findings。
- [ ] 範本、skill、接入指南與runtime schema一致；保留歷史結果與無關變更。
- [ ] 紀錄 Desktop/模型未驗證項目，不將必要 hooks 降為可選。
