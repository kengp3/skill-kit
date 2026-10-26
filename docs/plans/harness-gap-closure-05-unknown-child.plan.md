# G05：V02 持久 child 查回與未知啟動

**2026-10-26 範圍修訂（使用者已核准）：** 已通過的 unknown 不重派／同約恢復仍為必要產品證據；真正 spawn 回應遺失、provider sampling 故障注入及跨 root 宿主查詢資格改列選配未驗證，不阻擋產品交付。下方 partial 與未勾項保留個別試驗判定，不改為 passed。 依據：[最新規格 S1](../specs/harness-validation-gap-closure.spec.md#s1-唯一驗收邊界與狀態)。

**What to build:** V02 持久 child 查回與未知啟動；交付完整外部行為及可核對證據。

**Blocked by:** G01; observable child and fault boundary

**Status:** partial（client 重連／新 server 歷史查回通過；真正未知 spawn 與 provider sampling 故障未通過）

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] 真child於client transport故障後以同state核對原身分、終態及成果，無重派。
- [ ] 真正spawn結果遺失與provider網路分支各自有目標邊界直接證據；不足保留受阻。
- [x] 不以外層通知遺失、timeout、idle／notLoaded或mock冒稱目標通過。

直接證據：[G05 分段報告](../research/harness-gap-closure-unknown-child.research.md)、[client 故障前真 active child](../research/harness-gap-closure-unknown-child-evidence/before-disconnect-child-turns.json)、[新 client 原 turn completed／字面成果](../research/harness-gap-closure-unknown-child-evidence/reconnect-child-turns.json)、[同 state 新 server 原 turn 歷史](../research/harness-gap-closure-unknown-child-evidence/new-server-child-turns.json)。新 server 查回只驗已終態歷史，不證 running worker 跨 server 存活。

新主責原生 `list_agents` 只見當前 root，對原 handle 前綴為空；這不證舊 worker 不存在或完成。第一回合 prompt 額外阻斷普通讀檔的結果保留；同 persisted thread 澄清後已成功讀取規則／原約／本地輸入與 gate，更新並讀回同約，保持原 child／turn／返回成果 unknown、T1 未核實，沒有重派。本地合約恢復通過，跨 root 原生 child 查回仍受阻，不以控制器 API readback 冒稱模型能力。

真正 spawn tool 結果交付遺失未找到公開可控邊界，保持資格受阻。自有程序 network-deny 已取得原生 `workspace routing discovery failed` 終態及原始錯誤，但未命中 provider sampling URL／中途斷線，不計該目標通過。Windows 按總計畫排除。沒有修改產品／central／demo／global，沒有 push／PR；維護用 driver 不加入產品 runtime。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
