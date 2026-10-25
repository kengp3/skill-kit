# G02：V04 真實移轉中斷與同任務恢復

**What to build:** V04 真實移轉中斷與同任務恢復；交付完整外部行為及可核對證據。

**Blocked by:** G01

**Status:** ready-for-agent

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 僅在自有副本施加中斷，原命令開始、自有PID／token及磁碟現況有原始證據。
- [ ] 查明退出後明確續作，三門檻全過才刪舊檔，歷史產物與已完成操作保留。
- [ ] checkpoint／自然命令及syscall crash界線明確，未命中窗口不算通過。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
