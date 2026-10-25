# G09：證據對帳、獨立審查與入口更新

**What to build:** 證據對帳、獨立審查與入口更新；交付完整外部行為及可核對證據。

**Blocked by:** G00, G01, G02, G03, G04, G05, G06, G07 have explicit verdicts

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] Standards／Spec獨立審查完成且required findings已修正。
- [ ] 中央報告、實作票及摘要與直接證據一致，必要受阻時整體仍未完成。
- [ ] 補上README當前證據入口及最小開發端檢查；日常安裝入口與全域狀態單獨回報。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
