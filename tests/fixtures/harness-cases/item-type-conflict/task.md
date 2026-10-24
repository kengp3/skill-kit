# 單一 bug：started／completed 類型衝突

目的：修復 `harness/evidence.py` 的 `summarize_events(paths, *, thread_id, turn_ids)`，使相同 `(thread, turn, item)` 的類型衝突保持未確認，不被當成完整證據。這是已知開發案例，不是未見或公平模型比較案例。

## 提供給實作者的材料

使用 `products/defect/` 的完整副本作為工作目錄，只提供本任務與 `conflict.jsonl`、`consistent.jsonl`。副本包含原始 `harness/evidence.py` 及 import 所需的 `harness/control.py`；兩者保留原版完整內容。修正版、checker、來源答案與研究紀錄屬維護者驗收材料，不放入實作者工作副本。此配置說明不代表已執行模型 trial 或取得公平比較資格。

## 行為契約

- 相同 identity 的 started 是 `commandExecution`，completed 卻是 `agentMessage`：摘要 `coverage` 為 `partial`、`commands_completed` 為 0、`command_outcomes_unknown` 為 1，並列出未確認證據。
- 即使兩個 item 事件顛倒順序，仍得到上述結果。
- 同一 identity 的正常 command started／completed：`coverage` 為 `complete`、`commands_completed` 為 1、`command_outcomes_unknown` 為 0。
- 三種輸入的 root turn 均有獨立的 completed 事件，所以 `final_turn_status` 維持 `completed`；回合結束與 item 證據完整性分開判定。

## 修改與交付範圍

只修上述行為，保留公開介面與正常摘要。不安裝套件、改全域設定或其他專案，不建立 OS 隔離、watchdog 或模型執行器。交付修改、直接驗證結果與未驗證項目；不要求人工觀察。

## 維護者離線驗收

`case.json` 固定錯誤／修正版來源及 hash。`check.py <product-root>` 以同一份獨立契約檢查兩版，輸出 `TEST-item-type-conflict.xml`；必須從新的可丟棄執行目錄執行。它只處理本案例，不是通用 runner。缺依賴或 import 失敗不當成已重現 bug。

Repo 驗證入口：`python3 -B -m unittest discover -s tests -p 'test_harness_case.py' -v`，重用既有 `case_inputs`、`regrade`、`qualify`。錯誤版必須 graded／false，修正版 graded／true，且來源不變；既有 macOS checker 執行上下文需允許 ps／sandbox-exec。
