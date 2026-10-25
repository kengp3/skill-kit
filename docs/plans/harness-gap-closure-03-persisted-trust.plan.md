# G03：V01 正常審閱及跨啟動持久信任

**What to build:** V01 正常審閱及跨啟動持久信任；交付完整外部行為及可核對證據。

**Blocked by:** G01; normal human review interface

**Status:** blocked — 正常文字審閱介面已備妥；等待使用者審閱精確定義並明確核准正常信任操作

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 不使用bypass或改寫trust資料庫，正常審閱exact hook定義且保留過程。
- [ ] 同state兩次invocation均有信任狀態及實際提醒證據。
- [ ] project trust與hook trust分開，人工待完成時保持受阻。

## 本次進度與最小解鎖條件

已完成獨立 case／state、凍結候選與 demo 現行基底指紋、原生 skills／hooks 來源核對，正常 CLI 文字介面可審閱。五個 hook 仍 `untrusted`，未使用 bypass 或寫 trust 資料庫；沒有開始模型任務。

交付 [驗證研究](../research/harness-gap-closure-persisted-trust.research.md) 與 [人工審閱包](../research/harness-gap-closure-persisted-trust-evidence/human-review.md)。既有 exec session `49562`、TUI PID `98889` 與專用 state 保留，未執行 `t trust all`。使用者完成精確 JSON／來源／hash 審閱並明確核准後，才操作正常 CLI 信任並驗證同 state 兩次 invocation。其他案例繼續；本 ticket 不標 done。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
