# P1 離線交付：N04、候選封裝與 N06

日期：2026-10-24。狀態：本輪離線實作與必要驗證完成，獨立 Standards／Spec 複核通過。

本輪套用 ask-matt → implement → tdd → code-review，沿用核准規格與本地計畫，不新增訪談或日常控制機制。固定 review 基線為 `205ca091bee6bdaaea2819d44bc6b0feb9ac84f7`。完成範圍僅 N04、候選離線封裝與 N06 舊資料回放；Desktop 是日常入口，CLI 仍是開發評測路徑。

## 已交付內容

- N04：task-harness／ai-code-review 的既有風險段落補鎖順序、callback／重入、背景 worker 所有權及關閉時序，要求有限時間的專案驗證與按風險獨立 review。不新增固定角色、hook、人工核准或通用測試清單。task-harness 交付改由 agent 整理可取得證據，缺值保留，不要求計時／填表／人工觀察。
- 候選 `0.1.2`：沿用既有 package builder，輸出至 `dist/candidates/personal-harness-0.1.2`。19 個 runtime 檔案、18 個本地引用、內容 manifest 及 checkout 外獨立執行均核對；沒有安裝、修改 marketplace 指向或刷新快取。`0.1.1` 是曾用於歷史更新／回退的版本，因此候選另用新版本。
- N06：schema v2 將原始來源／指紋、觀測、事件摘要與判讀分開；human_takeover 預設 null，移除 observation_window。`tests/harness/evidence.py` 提供只讀的保存事件整理與首輪 smoke 回放，`tests/test_harness_evidence.py` 驗證主子歸屬、跨 turn、去重、衝突、缺失與 malformed 輸入。程式不連線、不執行事件內容、不啟動模型，不放入 runtime 套件。

## 舊資料回放

| 組別 | 主對話已結束命令／非零 exit | 凍結 V2 | 後續 factory-close 診斷 | 判讀 |
| --- | --- | --- | --- | --- |
| A | 16／3 | 通過 | 通過 | 原生回合完成；不推論人工效益 |
| B | 18／3 | 通過 | 失敗 | 流程完成但有已知缺陷；保留原交付，不修復或重跑 |
| C | 26／1 | 通過 | 通過 | 兩段 turn、同一次 trial；首段 stream 缺 root terminal，覆蓋仍為 partial，另有 readback 中斷證據 |

C 原摘要的 29 個命令含 reviewer 子回合，本輪摘要只計 root thread 的明確 turn，因此為 26；不覆寫或更正原始檔案。已結束命令含正常與非零 exit，不代表驗收通過，也不等於重試或修復次數。求助、重試、修復、人工接手、打斷與人工 active time 缺乏可靠完整觀測，均保留未知；既有 controller recovery 是另一項紀錄，不換算成人工救援。configured model 不證明供應端實際模型版本。

## 驗證與證據

- TDD 逐切片觀察缺模組／API、衝突狀態、缺事件等失敗後轉綠；9 項 N06 測試通過，真實 A／B／C 保存資料皆回放。5 項既有 package 測試通過，含不覆寫舊 release、拒絕 linked／缺失來源、驗包與獨立執行。
- 初次原生環境完整 unittest：67 項、66 通過、1 項原生 Windows cmd.exe 略過；review 修正後最終 69 項、68 通過、1 項 Windows 略過，受測來源前後指紋相同。首次執行因外層 sandbox 禁止 `/bin/ps`，既有 P0 程序監測失效；保留失敗原始紀錄，於允許 ps／nested sandbox-exec 的執行環境重跑後通過，測試自己的隔離及控制不變，未修改 P0 程式或降低斷言。
- 582 個受保護檔案與 1322 個原有無關未追蹤檔案內容未變，日常設定／啟用套件／快取及原 smoke／P0 證據無非預期新增。此核對不是 Desktop 所有動態狀態的隔離資格驗證。

證據：[完整測試](codex-harness-p1-offline-20261024-evidence/python-tests-final-2.json)、[外層限制失敗紀錄](codex-harness-p1-offline-20261024-evidence/python-tests.json)、[受測來源](codex-harness-p1-offline-20261024-evidence/validated-sources-final.json)、[候選驗證](codex-harness-p1-offline-20261024-evidence/candidate-qualification.json)、[保護核對](codex-harness-p1-offline-20261024-evidence/protected-after.json)、[A 回放](codex-harness-p1-offline-20261024-evidence/replay-A-final.json)、[B 回放](codex-harness-p1-offline-20261024-evidence/replay-B-final.json)、[C 回放](codex-harness-p1-offline-20261024-evidence/replay-C-final.json)。

保存回放可透過 `PYTHONPATH=tests python3 -B -c 'from pathlib import Path; from harness.evidence import replay_smoke; print(replay_smoke(Path("docs/research/codex-coding-harness-implementation-evidence")))'` 重新整理，不使用封存 probe 的暫存路徑或活躍宿主。完整維護命令仍為 `python3 -B -m unittest discover -s tests -p 'test_*.py' -v`，P0 程序測試需允許 ps 及 nested sandbox-exec。

## 尚未驗證

N04 的實際模型遵循、候選 Desktop 載入與低風險任務交付、外部取消、宿主狀態／資源與帳號額度隔離仍未通過。N06 目前只支持首輪保存的 CLI RPC 格式；新 Desktop 事件覆蓋須後續有界 trial 核對，沒有背景監控或收集日常資料。N07、第二專案、其他宿主及公平效果比較不在本輪。N05 僅候選準備，不能標整體完成；沒有新模型 trial，也不以零次人工觀察宣稱省時。

## 複核與回顧

首輪 Standards 0 finding；Spec 找到兩項 P2：started／completed item 類型衝突被視為完整，以及固定結果缺失／malformed 會中止整批回放。已補反例，逐切片觀察 red → green；修正跨事件類型不變條件、逐組錯誤隔離及 grade 基本完整性，缺失驗收保持 unknown，繼續獨立組別。最終固定版本 `0a94c63fb25257e0dd5c5fd35db073edaea3dd6b` 的兩軸複核通過，兩項均已解除。本次確認舊提案中的 `test_harness_evaluation.py` 不存在，實作沿 P0 已拆分結構新增專責 evidence 測試；沒有為舊檔名補建整合入口。跨宿主能力檢查繼續留在適用範圍，避免把 CLI 通過或快取出現當成 Desktop 完整驗收。


## Standards

0 項未解除 finding，0 項新增 smell。修正維持既有標準函式庫／unittest 結構，未擴充日常 runtime。4 個來源指紋及回放各來源 hash 均相符；獨立重算三組回放與 final JSON 完全一致。未獨立重跑完整測試或操作 Desktop。

## Spec

SPEC-01、SPEC-02 均已解除，未發現修正引入的新具體問題。Reviewer 獨立驗證事件順序／型別衝突及缺 grade、malformed JSON、缺欄位、無效 grade 值與 malformed outcome；必要資料缺失保持 unknown，其他組可繼續。已核對 69 項原始測試輸出及最終來源，C 保留 partial、B 保留已知缺陷。

兩軸結果：Standards 0 待處理；Spec 0 待處理，皆無未解除最高風險項。證據：[review 記錄](codex-harness-p1-offline-20261024-evidence/reviews.json)、[完成保護核對](codex-harness-p1-offline-20261024-evidence/completion-audit.json)。本輪只讀舊 grader receipts，未重新執行 Java checker；新摘要沿用各凍結驗收範圍，不作新版 grader 或 Desktop 的行為保證。
