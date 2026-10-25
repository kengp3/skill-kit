# G08：V06 Windows（使用者明確排除）

**What to build:** V06 Windows（使用者明確排除）；交付完整外部行為及可核對證據。

**Blocked by:** None

**Status:** cancelled

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] 2026-10-25使用者明確指示『不考慮 windows 情境』；本票不執行、不計通過，也不阻擋本輪驗收。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
