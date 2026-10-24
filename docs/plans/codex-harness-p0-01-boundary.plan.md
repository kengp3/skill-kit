# 01: 開發測試的寫入與程序邊界

**What to build:** 開發測試的寫入與程序邊界，以直接證據支援 Desktop 日常入口與 CLI 開發評測分工。

**Blocked by:** None (can start immediately).

**Status:** done

- [x] 測試子程序只能寫入專屬工作目錄；設定、plugin cache、宿主持久狀態與其他日常資料不因測試被覆寫；未知／symlink 逃逸路徑拒絕。
- [x] 以可執行方式限制 wall time、CPU／記憶體與並行程序；本輪模型／網路額度為零，不能呼叫模型或連線；限制無法成立則停止相依程序。
- [x] 正常、錯誤、取消與失聯均收尾自有父子程序；無關檔案與負向 worker 不變；不要求人工監看。
- [x] 以真實隔離 canary 及負向對照驗證，不修改 Desktop、全域配置、快取、記憶或原 demo-002。

依據：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫 N01–N03](codex-coding-harness-pilot.plan.md#202-具體待改檔案接入及完成條件)。本輪僅實作 P0；P1、Desktop 模型試用、其他宿主與第二專案不在本票。

驗收：`python3 -B -m unittest discover -s tests -p test_harness_boundary.py`，13 tests，全部通過，3.264 秒。先觀察到缺少模組的 red，以及輸出 symlink 覆寫的 red；修正後 green。真實 canary 覆蓋直接／symlink 外部寫入拒絕、loopback 拒絕、隔離環境、CPU／RSS／程序數／wall 限制、檔案大小限制、正常／失敗／取消收尾與無關 worker 保護。外層執行 sandbox 不允許嵌套 sandbox-exec，測試以已授權的本機 escalation 執行，沒有模型或原生 app-server 呼叫。

界線：只接受系統暫存區內的空白真實工作目錄，既有輸出不覆寫；CPU 使用 kernel limit 及 group watchdog，單檔 16 MiB kernel limit。RSS 與自有程序數以 20ms 取樣，閾值可能短暫超出；不是 kernel 硬記憶體上限。只支援保留自有 process group 的後代，不宣稱可收容任意 detached 程式；單工作互斥範圍是同一 Python interpreter。限制未成立或收尾未確認即拋出 BoundaryUnavailable，不降級執行。
