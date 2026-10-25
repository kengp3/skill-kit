# G01：demo-002 正常接入與最小任務

**What to build:** demo-002 正常接入與最小任務；交付完整外部行為及可核對證據。

**Blocked by:** G00

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 由project-setting初始化demo自己的規範，包含harness時依其provider規格設定。
- [ ] 載入凍結0.3.0來源，取得真實模型最小成果、唯一合約與讀回證據。
- [ ] 既有修改與應用程式內容保留，hooks未信任時誠實記錄模型接手。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
