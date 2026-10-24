這是同一個 Desktop 控制預檢的第二項診斷，改由使用者在主視窗直接送出此任務，驗證 UI 原生 Stop 是否能中斷這種回合；不是 smoke。

只用 exec_command，在 cwd=/private/var/folders/76/hd61cw513zbdlr0y7_h27dx80000gn/T/harness-smoke-0vwf4lur/C 執行：
/opt/homebrew/opt/python@3.15/bin/python3.15 -I -B .harness-control/manual-stop-2/worker.py
設定 login=false、yield_time_ms=1000。腳本只寫此 canary 目錄，120 秒自限。

看到 MANUAL_STOP_READY 後，立即 commentary 回報「測試已開始，請現在按這個對話的 Stop」，然後只以 write_stdin 空字串持續觀察同一 session，不自行送 Ctrl-C、不重啟、不委派。使用者將按原生 Stop，尊重中斷。若自行到期就如實回報，不能算 Stop 成功。

不要修改任何來源、設定、腳本；不要讀 TASK.md、答案、研究或其他組。不要執行正式 bug 任務、build 或 tests。Controller 將另行查核原生回合與父子程序狀態。
