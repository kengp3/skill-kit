# 重構：抽出命令統計責任

既有 `harness/evidence.py` 的公開 `summarize_events(paths, *, thread_id, turn_ids)` 混合事件整理與命令統計。請將命令統計抽成同模組的 `_command_metrics`，公開輸入、回傳欄位與錯誤／未知語義保持不變。

## 驗收契約

- `events.jsonl` 對 root 的 first／second／empty：已結束命令 3、非零 1、未知 0，coverage complete、final turn completed；重複及子對話仍排除。
- `conflict.jsonl` 對 root／first：已結束 0、非零 0、未知 1，coverage partial、final turn completed；help_requests／retries／repairs 仍為 null。
- 無效 turn IDs 仍拒絕；缺失來源仍產生 partial／unknown，不改為成功或拋出未處理例外。
- 統計 helper 必須擁有既有六個 metrics 欄位的建立責任，公開函式只呼叫一次並使用其回傳值，不保留重複的 inline metrics dict。不以新增未使用函式冒充完成。

行為 checker 對 before／after 都須通過；結構 checker 對 after 通過，未抽取的 before 應失敗。重構不需要先有 bug，也不要求舊版行為測試失敗。AST 只驗證上述明確結構要求，不能取代公開行為檢查。

## 範圍與材料

只改工作副本的 `harness/evidence.py`，不增加功能、改既有欄位或整理不相關邏輯。只讀 `control.py` 依賴與兩份 JSONL。維護者提供 `products/before/` 完整副本、task、輸入給實作者；after／checker 為驗收材料，不放入工作副本。

before 是 manifest 所列歷史原碼，after 是從同一基準衍生的案例專用參考，不是歷史或 production 版本。本輪不建立或執行模型工作副本，不宣稱答案隔離／公平比較；不修改全域設定、其他專案或現行 runtime，不建立 OS／watchdog，不要求人工觀察。

`check.py <product-root>` 執行三項行為檢查；加 `--structure` 改執行三項結構檢查，兩者都在全新目錄輸出 `TEST-command-metrics-refactor.xml`，重用既有 grader。資格需 before／after／structure 三份通過證據；另外保留 before 的結構負向對照。
