# G04：V07 strict 與 provider 強度負例

**What to build:** V07 strict 與 provider 強度負例；交付完整外部行為及可核對證據。

**Blocked by:** G01; current account model metadata

**Status:** done — 三個指定 V07 分支已通過；整體補驗另由 G09 彙整

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] 兩個strict範圍案有實際派工或blocked且無違規派工，無相依成果繼續。
- [x] provider負例按實際request與error判別upstream／host／schema／認證，不能混算。
- [x] 無法抵達目標拒絕層維持受阻，模型與設定不擅自降級。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。


## 本次結果

2026-10-25–26（Asia/Taipei）。[G04 直接證據報告](../research/harness-gap-closure-strict-effort.research.md)：A 真派出合格後續 `gpt-6-sol/low` child 並完成唯一合約；B 所有子 agent 限 `minimal` 時 T1 blocked、零 spawn，主責完成獨立 T2；獨立 probe 的同一請求經 429 退避後取得 upstream HTTP 400 `reasoning.effort/unsupported_value`，其 failed turn 是負例預期結果。各案已退出自有 native server、移除認證複本且全域設定指紋未變。產品及歷史證據未改；Windows 排除，未把此 ticket done 寫成全案完成。
