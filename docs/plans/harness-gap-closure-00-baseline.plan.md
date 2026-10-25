# G00：狀態分流、候選與現況基準

**What to build:** 狀態分流、候選與現況基準；交付完整外部行為及可核對證據。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 中央報告逐項分開實作、驗證、安裝與資格狀態；Windows依最新指示排除。
- [ ] 記錄兩個repo與候選的當前基準及既有修改，保留無關內容。
- [ ] 實際核對候選manifest與環境，必要資格缺失有明確狀態。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
