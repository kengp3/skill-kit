# 小功能：按 turn 統計已結束命令

在提供的 `harness/evidence.py` 的公開 `summarize_events(paths, *, thread_id, turn_ids)` 新增 `metrics.commands_by_turn`。目前版本已有整體命令計數；此任務是增加明確的新契約，不是修復歷史 bug。

## 新契約

- 回傳每個指定 turn 的命令數。只計符合指定 root thread、該 turn、已結束且 exit code 為整數的 command；非零 exit 也算已結束。
- 同一 identity 的重複完成事件只算一次，子對話不算。
- 指定 turn 沒有可確認完成的命令時為 0；未知結果不計入，仍保留原本的 unknown 計數與 partial 語義。
- `events.jsonl` 的 `turn_ids=['first','second','empty']` 應得到 `{'first':2,'second':1,'empty':0}`。`unknown.jsonl` 的 `['first']` 應得到 `{'first':0}`。
- 保留現有欄位與歸屬／錯誤處理：events 的整體命令數仍為 3、非零為 1、未知為 0；無效或重複的 turn IDs 仍拒絕。

## 範圍與材料

只修改工作副本的 `harness/evidence.py`，不改現行 repo runtime、全域設定或其他專案，不建立 OS／watchdog，不執行模型 trial，也不要求人工觀察。

維護者提供 `products/missing_feature/` 的完整副本及本 task、兩份 JSONL 給實作者；checker／參考實作只供外部驗收，不放入工作副本。本輪尚未建立或執行模型工作副本，不宣稱答案讀取隔離或公平比較成立。

`case.json` 的 missing_feature 是歷史原碼，implemented 明示為從同一基準衍生的案例專用參考，非歷史或 production 版本。`check.py <product-root>` 在全新執行目錄產生 4 項檢查的 `TEST-command-counts-by-turn.xml`，沿用既有 grader。缺新欄位應為功能契約 assertion 失敗，不能用 import／環境錯誤充當缺功能證據。
