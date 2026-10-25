# G06：V03 真實來源與原生重入

**What to build:** V03 真實來源與原生重入；交付完整外部行為及可核對證據。

**Blocked by:** G01; observable native events

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 同合約經真startup／resume／compact保持一次寫入及無重複派工。
- [ ] 同事件redelivery須有宿主關聯證據；replay／新prompt不能代替。
- [ ] canonical passive Stop不授權續作，無可用重入控制則保留受阻。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
