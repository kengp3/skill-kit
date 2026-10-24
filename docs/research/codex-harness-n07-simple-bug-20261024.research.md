# N07 單一簡單 bug 離線案例

日期：2026-10-24。狀態：案例及必要驗證完成，Standards／Spec 獨立複核中。範圍限本 repo 的單一離線開發案例及規格／計畫邊界修訂。

## 結果

案例 `item-type-conflict-v1` 以同一 checker 驗證歷史錯誤版與修正版。三項契約檢查為類型衝突、事件顛倒順序、正常 command。錯誤版前兩項 assertion 失敗，正常情境通過；修正版三項全過。兩版皆無 import／執行錯誤，來源前後指紋一致，既有 `qualify` 判為 qualified。

| 固定產物 | 原始 commit | Tests／failures／errors／skipped | 結果 |
| --- | --- | --- | --- |
| defect | c786ad3139f7fafcf19ca569666607cdd9dc03eb | 3／2／0／0 | graded／false，重現目標缺陷 |
| correct | 0a94c63fb25257e0dd5c5fd35db073edaea3dd6b | 3／0／0／0 | graded／true |

完整維護 unittest：71 項，70 通過、1 項 Windows cmd.exe 專用測試略過；returncode 0，受測素材與程式前後 hash 相同。本輪沿用既有 ps／sandbox-exec 執行上下文，不新增 OS 控制或 watchdog。

## 案例與驗證邊界

[任務與契約](../../tests/fixtures/harness-cases/item-type-conflict/task.md)、[來源 manifest](../../tests/fixtures/harness-cases/item-type-conflict/case.json)、[單案例 checker](../../tests/fixtures/harness-cases/item-type-conflict/check.py)、[資格回歸](../../tests/test_harness_case.py)。兩份 JSONL 是合成的最小重現輸入，不是新增 Desktop／模型事件。

- 保留原始完整 `evidence.py` 與 import 所需的 `control.py`，逐 byte 比對固定 Git 版本，沒有手寫壞實作替代歷史缺陷。這些是測試資料，未修改現行 `tests/harness/evidence.py`。
- 沿用公開 `summarize_events`、既有 `case_inputs`／`regrade`／`qualify` 及 unittest；checker 只把這一個案例的三項結果轉成既有 XML 格式，不是通用 runner，沒有新依賴。
- task 明確區分實作者工作副本與維護者 fixed／checker 材料；本輪沒有啟動 agent、建立 trial 工作副本或宣稱答案讀取隔離已實測。
- 先觀察缺少 manifest、task／checker 的測試失敗，再逐切片建立素材與 checker，確認紅轉綠。此案例已有實作參照與已知答案，只具開發回歸資格；不作未見或公平模型比較，也不推論 agent 流程負擔或人工效益。

## 專案範圍修訂

[設計規格](../specs/codex-coding-harness.spec.md)與[試行計畫](../plans/codex-coding-harness-pilot.plan.md)同步：共用元件集中維護，由各專案明確啟用。開發測試只修改本 repo 授權素材與自有暫存資源；禁止自動變更全域設定、日常啟用版本／快取或其他專案。必要控制仍按實際操作確認，缺口只限制相依操作；OS 隔離、watchdog、全機盤查與 D01／D02 支線不列通用前置。

本輪 skills、package metadata、既有候選、全域設定及日常快取未變，因此不升 runtime 版本或重建候選。123 個保護檔案及1322個原有無關未追蹤檔內容不變，demo-002 的原有 Git 狀態完全相同；不執行新模型 trial，也不要求人工觀察。

## 證據與重現

- [錯誤版收據](codex-harness-n07-simple-bug-20261024-evidence/defect-receipt.json)、[XML](codex-harness-n07-simple-bug-20261024-evidence/defect-tests.xml)
- [修正版收據](codex-harness-n07-simple-bug-20261024-evidence/correct-receipt.json)、[XML](codex-harness-n07-simple-bug-20261024-evidence/correct-tests.xml)
- [Bug 資格](codex-harness-n07-simple-bug-20261024-evidence/qualification.json)、[來源逐 byte 核對](codex-harness-n07-simple-bug-20261024-evidence/provenance.json)
- [完整測試輸出與指紋](codex-harness-n07-simple-bug-20261024-evidence/python-tests.json)、[專案／日常保護核對](codex-harness-n07-simple-bug-20261024-evidence/protected-after.json)

從 repo 根目錄執行 `python3 -B -m unittest discover -s tests -p 'test_harness_case.py' -v` 可重驗兩版與資格，僅產生自有暫存檔。完整回歸仍用 `python3 -B -m unittest discover -s tests -p 'test_*.py' -v`；沿用現有 macOS checker 的 ps／sandbox-exec 需求。

## Standards

待獨立複核固定基線 `1c506d8613eb05dea901311f6eb2399075c4a5c8` 之後的本輪差異。

## Spec

待獨立複核本輪單一案例、錯誤／修正版驗證與跨專案範圍邊界；不將整個 N07 或 Desktop 驗收標為完成。

## 限制與回顧

尚未驗證小功能／重構案例、模型實際遵循、Desktop 交付／取消或人工效益。本次直接重用已確認缺陷與既有 grader，以任務素材補上開發案例，不再擴大控制平台；舊 smoke、P0、P1 報告保留其歷史事實。
