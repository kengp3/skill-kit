# G04：V07 strict 與 provider 強度負例

**What to build:** V07 strict 與 provider 強度負例；交付完整外部行為及可核對證據。

**Blocked by:** G01; current account model metadata

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 兩個strict範圍案有實際派工或blocked且無違規派工，無相依成果繼續。
- [ ] provider負例按實際request與error判別upstream／host／schema／認證，不能混算。
- [ ] 無法抵達目標拒絕層維持受阻，模型與設定不擅自降級。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
