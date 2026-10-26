# G06：V03 真實來源與原生重入

**2026-10-26 範圍修訂（使用者已核准）：** 已通過的同約恢復、一次成果及被動 Stop 仍為必要產品證據；raw input source 與同事件 native redelivery 改列選配未驗證，不阻擋產品交付。下方 partial／blocked 與未勾項保留個別試驗判定。 依據：[最新規格 S1](../specs/harness-validation-gap-closure.spec.md#s1-唯一驗收邊界與狀態)。

**What to build:** V03 真實來源與原生重入；交付完整外部行為及可核對證據。

**Blocked by:** G01; observable native events

**Status:** partial / blocked（同合約真 start／resume／compact 行為通過；raw input source 與同事件 redelivery 未關閉）

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] 同合約經真startup／resume／compact保持一次寫入及無重複產品派工；來源判定限方法時序、native hook runs 與 developer context，原始 stdin source 未公開。
- [ ] 同事件redelivery須有宿主關聯證據；replay／新prompt不能代替。
- [x] canonical passive Stop不授權續作；三明確回合外沒有自動續作，無可用重入控制已明確保留受阻。

執行入口：[G06 原生來源研究與證據](../research/harness-gap-closure-hook-sources.research.md)。G01 正常接入已完成；本案 canonical echo／passive Stop 不變，單次 bypass 與正常持久信任分開。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
