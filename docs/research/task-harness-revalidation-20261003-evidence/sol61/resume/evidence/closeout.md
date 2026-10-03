# 接續結果
已完成目前可安全完成工作；整體任務尚未完成。

- T1：double 修正為 2*value；目前版本通過 [receipt](T1-after.json)，原始失敗見 [receipt](T1-before.json)。
- T4：初次 transient failure，核對結果後僅重試一次成功；見 [receipt](T4-2.json)。
- T2：先前 send timeout 的遠端結果未知；缺少 authoritative receipt、query API、idempotency，不重送。需取得遠端結果或由使用者明確決策。
- T3：deployctl 缺少，見 [工具查核](T3-tool.json)；目前禁止安裝。需提供工具及部署驗證指令。
- T5：兩次都不可用，見 [首次](T5-1.json)、[重試](T5-2.json)；重試額度耗盡，需服務恢復或診斷材料。

單一任務狀態為 ../tasks.md。無 active worker，沒有 safe ready work；counter 各 2，通知未重播，唯讀材料與其他使用者文件保留。
