# G05：V02 持久 child 查回與未知啟動

**What to build:** V02 持久 child 查回與未知啟動；交付完整外部行為及可核對證據。

**Blocked by:** G01; observable child and fault boundary

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 真child於client transport故障後以同state核對原身分、終態及成果，無重派。
- [ ] 真正spawn結果遺失與provider網路分支各自有目標邊界直接證據；不足保留受阻。
- [ ] 不以外層通知遺失、timeout、idle／notLoaded或mock冒稱目標通過。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
