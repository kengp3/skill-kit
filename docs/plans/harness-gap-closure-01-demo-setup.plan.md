# G01：demo-002 正常接入與最小任務

**What to build:** demo-002 正常接入與最小任務；交付完整外部行為及可核對證據。

**Blocked by:** G00

**Status:** done

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] 由project-setting初始化demo自己的規範，包含harness時依其provider規格設定。
- [x] 載入凍結0.3.0來源，取得真實模型最小成果、唯一合約與讀回證據。
- [x] 既有修改與應用程式內容保留，hooks未信任時誠實記錄模型接手。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。

## 本輪交付

2026-10-25：已完成真 demo 接入、原生模型初始化與最小任務；[G01 報告](../research/harness-gap-closure-demo-setup.research.md)包含 expected → observed → raw → verdict、705 原檔／26 新檔保存、source qualification 修正與精確合約／成果。五個標準 hooks 已寫入且宿主列出但仍 untrusted，由模型主動檢查；不宣稱 V01 持久信任或事件觸發通過。第一試可見全域 user skills 的事實保留，新隔離 state 停用三個 user paths後由原生模型唯讀驗收原合約／成果，未重做副作用。整體補驗狀態由中央表維護。
