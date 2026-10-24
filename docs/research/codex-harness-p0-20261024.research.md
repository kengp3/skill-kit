# Coding Harness P0 實作與驗證

日期：2026-10-24（Asia/Taipei）
狀態：P0 實作與整合驗收已通過，初次兩軸 review 的四項問題已修正，最終整合驗收通過，兩軸複核待完成；尚不宣告整體完成。

## Objective

依修訂規格完成 N01 測試邊界、N02 CLI 控制及 N03 grader 最小回歸。Desktop 為日常入口，CLI 供開發評測；不啟動新的模型 trial、不要求人工觀察、不改 Desktop 日常配置／快取／記憶。

## 工作來源與執行方式

- [設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫](../plans/codex-coding-harness-pilot.plan.md)。
- 本地票：[01 邊界](../plans/codex-harness-p0-01-boundary.plan.md)、[02 控制](../plans/codex-harness-p0-02-cli-control.plan.md)、[03 Grader](../plans/codex-harness-p0-03-grader.plan.md)。
- ask-matt → to-tickets → implement-spec；使用既有已確認 N01–N03 作票界線，不重新要求人工核准；ticket 位置遵循 project-setting，單票單檔。
- 整合分支 `codex/harness-p0`，基線 `89e21da`；實作者各用專屬 worktree／branch，依 TDD 累進驗證，最後整合與 Standards／Spec review。不建立外部 issue、PR 或 push。
- 僅開發測試機制；P1 規則調整、Desktop 實際任務驗收、自動統計與新增代表模型案例未納入本輪。

## 完成審核

| 要求 | 必要證據 | 目前狀態 |
| --- | --- | --- |
| N01 寫入／網路與資源限制 | `test_harness_boundary.py`：15 項真實 canary；[最終維護回歸](codex-harness-p0-20261024-evidence/python-tests-final.json) | 已驗證目前 macOS 支援範圍 |
| N01 程序收尾與日常保護 | 正常／失敗／逾時／取消清理，無關 worker 存活；[551 檔案保護核對](codex-harness-p0-20261024-evidence/protected-state.json) | 已驗證指定來源與程序群 |
| N02 精確完成歸屬 | `test_harness_control.py`：9 項含首輪真實 C RPC／readback | 已驗證純控制層，不冒稱重驗原生引擎 |
| N02 結果不明及原期限續作 | 控制測試＋`test_harness_p0_integration.py`，真實取消／writer 收尾不能代替 native readback，續作保留原 deadline | 已驗證 |
| N03 相關變更與資格 | `test_harness_grader.py`：9 項含輸入、指紋、command prefix、預期報告、缺值與三種資格 | 已驗證 API 與錯誤路徑；未擴為新功能／重構模型案例 |
| N03 固定產物重評 | 受影響 A／B／C 選取回歸；[修正後五次原生隔離重評](codex-harness-p0-20261024-evidence/fixed-grading-final/summary.json)，每次來源前後一致 | 已驗證，原 trial 不改 |
| 無模型 trial／無人工觀察 | 測試拒絕模型／app-server 命令、network deny、環境不繼承 API key；只回放事件與本機 canary／Maven | 0 新模型 trial，無人工觀察要求 |
| 整合及品質 | 60 tests：59 通過、1 原生 Windows 略過；test/source before＝after | 整合通過，Standards／Spec review 待完成 |

## 實際落地與使用

- `tests/harness/boundary.py`：macOS 開發專用 `run`、`Limits`。只接受系統暫存區的空白真實目錄；寫入與 HOME／TMP／cache/config/data 重導至自有目錄，網路拒絕。原生限制不可建立就失敗，不降級執行。
- `tests/harness/control.py`：`TrialControl` 的事件歸屬、未知結果核對、取消與續作。時間使用原始 monotonic deadline；原生 terminal 與 writer 存活分開。
- `tests/harness/grader.py`：案例輸入／資格、受影響固定產物選取、唯讀 checker 執行及新收據。缺 XML、略過、數量不符、超時或來源改變均為 unverified；產品 assertion 失敗可為 graded／false，不被 wrapper 成功掩蓋。
- 新增三組 unit／process 回歸與一項控制＋程序證據組合測試。沒有新增 evaluate runner、日常 hook、runtime skill 或發佈配置；套件版本維持原狀。
- 原生 canary 需在允許 sandbox-exec 的本機執行上下文運行。外層 sandbox 不允許嵌套時，明確回報 BoundaryUnavailable；本輪以授權的本機 escalation 執行，無人工看守。可直接使用既有 unittest discovery，不建立背景服務。

## 固定產物結果（修正後已重新驗證）

| 固定產物 | 驗收 | 結果 |
| --- | --- | --- |
| Parent | 公開 lifecycle，2 tests | 目標 assertion 失敗，符合已知缺陷 |
| A | 公開 lifecycle，2 tests | 通過 |
| A | factory-close，1 test | 通過 |
| B | factory-close，1 test | 死鎖診斷 assertion 失敗，原缺陷保留 |
| C | factory-close，1 test | 通過 |

上述是重評既有固定產物，沒有回饋或續作受測 agent。每次只在新副本準備相同的 parent POM 輸出位置 overlay `${p0.output}` 並放入既有公開 Java fixture；原始 A／B／C 與 parent 不修改。準備後的來源與 checker 不可寫，Maven 離線、網路拒絕，只有 execution 目錄可寫。每次 wall45秒、CPU25秒、RSS1024MiB 監測、最多6個自有程序、單檔16MiB；實際均在期限內完成，沒有殘留 writer。每次新收據、XML、原始 checker／driver 及準備指紋初次結果保留於 fixed-grading，修正後結果另存 fixed-grading-final，不覆寫。

## 限制與後續邊界

- 目前只驗證 macOS。RSS／程序數以20ms抽樣，可能短暫超過門檻；CPU有繼承的單程序 kernel limit及活躍自有程序群監測，並非整個系統的硬隔離。
- 支援的子程序必須保留自有 process group；不收容任意惡意／detached 程式。清理只針對自有群組，不掃描或停止 Desktop／其他工作。單工作互斥範圍是一個 Python interpreter，本輪任務順序執行。
- 本輪測試的模型／網路預算為零；沒有啟動 native app-server、測試新模型回合或消耗測試用 API 額度。開發與 review subagents 屬使用者明確指定的實作流程，不是受測模型 trial。
- 不宣稱 Desktop Stop、Desktop 新候選任務交付、其他宿主、第二專案或人工省時已通過。N04–N07 仍為後續階段；人工時間不可得保持未知，不要求使用者補量測。

## Standards（初次 review）

2項：threaded caller使用preexec_fn的exec前死鎖風險；malformed execution欄位使收據選取崩潰。前者的限制亦已核對[Python官方文件](https://docs.python.org/3/library/subprocess.html#subprocess.Popen)。沒有要求額外抽象化的Fowler smell。兩項已修正：已exec launcher取代preexec_fn；malformed execution／observations／未知writer證據均不接受，待最終複核。

## Spec（初次 review）

2項：既有收據未重核完整報告集合／數量；程序監測失效時可能跳過終止自有程序。收據問題已由主agent用既有收據的純記憶體副本重現，見[修正前重現](codex-harness-p0-20261024-evidence/review-reproductions-before.json)。兩項已修正：既有收據重核完整報告集合／精確數量；ps掃描有0.25秒上限，失效仍對自有群組終止並回報無法確認，待最終複核。[修正後收據重現](codex-harness-p0-20261024-evidence/review-reproductions-after.json)已改為選入重評／unverified，初次綠測試不足以關閉目標。

修正驗證：四項 finding 由單一修正分支 `54daaa1` 合入 `99941fb`；最終60項回歸59通過／1 Windows略過，受測來源前後一致。固定Java產物再驗五次，已知缺陷與正確產物結果不變；沒有新模型trial。原始56項結果及初次review保留，避免把早期結果回寫為最終證據。
