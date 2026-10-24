# N07 小功能與重構離線案例

日期：2026-10-24（Asia/Taipei）。基線：`c0c33d7ec99a1a48642da420f1fabbd77bf0e8bb`。

兩個案例已完成素材及離線資格驗證，完整 unittest 通過；獨立 Standards／Spec 審查尚待收尾。本輪依使用者後段「直接進行後續開發」授權實作，不包含新模型 trial。規格與任務追蹤見[規格](../specs/codex-coding-harness.spec.md)及[試行計畫第 24 節](../plans/codex-coding-harness-pilot.plan.md)。

## 範圍與順序

1. **先小功能：按 turn 計算命令數。**沿用事件摘要的公開 `summarize_events`，新增 `metrics.commands_by_turn`，保留原有總數、歸屬、去重與錯誤語義。這是既有契約上的小增量，因此先用它補足 feature 類型的離線素材。
2. **再局部重構：抽出命令統計責任。**採同一歷史基準的獨立副本，把原六欄位統計移入 `_command_metrics`，公開行為保持不變，另外驗證責任抽取。它不依賴前一案例的新功能，避免把功能改動混入重構。

每個任務均採 ask-matt → implement → tdd → code-review。實作時先以現有公開摘要介面建立失敗檢查，再只修改案例專用參考，分別取得新增功能／結構的紅綠結果；整合至既有 `tests/test_harness_case.py` 後執行完整回歸。沒有新增通用 runner、依賴、設定、hook 或日常啟用流程。

## 材料與來源

| 案例 | 開發材料 | 驗收方式 |
| --- | --- | --- |
| 小功能 | [task](../../tests/fixtures/harness-cases/command-counts-by-turn/task.md)、兩份 JSONL、缺功能／參考副本與 manifest | 同一 checker 驗新欄位、未知結果、既有統計及無效 turn IDs |
| 重構 | [task](../../tests/fixtures/harness-cases/command-metrics-refactor/task.md)、正常／衝突 JSONL、前後副本與 manifest | 前後相同行為 checker，另以 AST 驗明定的 helper 責任及公開函式使用關係 |

兩個基準皆逐位元對照 `0a94c63fb25257e0dd5c5fd35db073edaea3dd6b` 的 `tests/harness/evidence.py` 與必要 `control.py`。implemented／after 是本輪衍生的**案例專用參考**，manifest 明列 base_revision、derivation 與各檔 SHA-256；它們不是歷史 commit 或現行 production 修改。輸入為精簡的合成事件，重用既有事件格式；重構衝突輸入沿用已完成 bug 案例。

這些是已知開發案例。未建立模型工作副本或執行答案隔離測試，不能當成未見基準或公平比較證據。

## 直接驗證結果

所有 run 均透過既有 `case_inputs`／`regrade` 執行，限制沿用既有 `Limits`；每次使用獨立暫存目錄。收據記錄執行命令、環境、輸入指紋、測試計數及來源前後指紋。下列 failures 是有意保留的負向對照，errors 均為 0，沒有用環境或 import 失敗充當任務失敗。

| 案例／固定產物 | 檢查 | tests | failures | 結果 |
| --- | --- | ---: | ---: | --- |
| 小功能 missing_feature | 新需求與相容性 | 4 | 2 | 缺新功能；既有契約通過 |
| 小功能 implemented | 同一 checker | 4 | 0 | 通過 |
| 重構 before | 公開行為 | 3 | 0 | 通過 |
| 重構 after | 相同公開行為 | 3 | 0 | 通過 |
| 重構 after | 明定結構 | 3 | 0 | 通過 |
| 重構 before | 相同結構負向對照 | 3 | 3 | 能辨識未做重構 |

小功能與重構均為 `qualified`；以缺功能產物替換 implemented，或以未重構產物替換 structure，整合測試皆確認資格為 `unverified`。重構的 AST 檢查只證明明列的責任抽取，不能取代行為驗證；三項行為案例也不代表所有可能輸入的等價性證明。

逐項收據、XML、資格及歷史來源比對：

- [小功能證據](codex-harness-n07-feature-refactor-20261024-evidence/command-counts-by-turn/qualification.json)、[來源比對](codex-harness-n07-feature-refactor-20261024-evidence/command-counts-by-turn/provenance.json)。
- [重構證據](codex-harness-n07-feature-refactor-20261024-evidence/command-metrics-refactor/qualification.json)、[來源比對](codex-harness-n07-feature-refactor-20261024-evidence/command-metrics-refactor/provenance.json)。
- 完整回歸：`python3 -B -m unittest discover -s tests -p 'test_*.py' -v`，**73 項，72 通過、1 項原生 Windows 檢查略過**；[原始輸出](codex-harness-n07-feature-refactor-20261024-evidence/unittest.stderr.txt)、[命令及來源指紋](codex-harness-n07-feature-refactor-20261024-evidence/unittest.json)。

## 專案邊界核對

[保留核對](codex-harness-n07-feature-refactor-20261024-evidence/preservation.json)確認 136 個受保護檔案、1323 個原有未追蹤檔案內容未變，demo-002 的 Git 狀態與開始時一致。受保護範圍包含既有 bug 素材、grader／control／boundary／現行 evidence 模組、skills、封裝、已存在日常快取及 Codex config；這是本輪選定範圍的比較，不宣稱全機無任何背景變動。

只新增本 repo 離線素材、修改測試接入及必要文件。未變更現行 runtime、候選套件版本、全域設定、日常啟用版本／快取或其他專案；未擴展 OS／watchdog；不要求人工觀察。既有 boundary 測試使用其原有本機沙箱與程序檢查，沒有增加相關能力。

## Standards

待獨立審查；分別核對兩個案例與共同測試接入。

## Spec

待獨立審查；分別核對功能、重構與範圍限制。

尚未檢查 Desktop 實際任務／取消、新模型行為、流程負擔、人工效益或公平比較；本輪離線結果不能推論這些效果。
