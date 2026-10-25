# G03：V01 正常審閱及跨啟動持久信任

**What to build:** V01 正常審閱及跨啟動持久信任；交付完整外部行為及可核對證據。

**Blocked by:** G01; normal human review interface

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 不使用bypass或改寫trust資料庫，正常審閱exact hook定義且保留過程。
- [ ] 同state兩次invocation均有信任狀態及實際提醒證據。
- [ ] project trust與hook trust分開，人工待完成時保持受阻。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
