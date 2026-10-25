# Harness P01 本地 CI 維護設定

日期：2026-10-25（Asia/Taipei）。範圍依[已核准規格](../specs/harness-validation-gap-closure.spec.md)與[計畫 P01](../plans/harness-validation-gap-closure.plan.md)。狀態：**本地配置／命令已查核，remote 未執行。**

## 交付與邊界

新增一份 [maintenance workflow](../../.github/workflows/tests.yml)，在未來獲准發布後以 `push`、`pull_request` 觸發單一 macOS job；目前只存於本地，沒有 push、PR、遠端執行或啟用操作。這是開發端選配維護工具，沒有改變 harness runtime、產品來源、既有測試或候選包。

沿用 [README](../../README.md) 的標準庫命令，未增加 pip 套件、依賴管理、外部服務、secrets、模型或自訂測試框架：

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

## Runner 選擇依據

先檢查全部 `tests/test_*.py` 與其 `tests/harness` 支援模組的 imports、子程序及平台前置條件。一般資料處理使用 Python 標準庫，但完整 suite 還需要以下系統能力：

| 既有邊界 | 必要能力與來源 |
| --- | --- |
| 本地受限子程序、offline grader／case 與 P0 integration | [boundary](../../tests/harness/boundary.py) 明確拒絕非 `darwin`，要求 `/usr/bin/sandbox-exec`；另需 `/bin/ps`、`/bin/sleep`、`/usr/bin/true`、`resource` limits、POSIX process groups、可寫 system temp，以及本機 loopback listener。不能改用無 sandbox 的執行來宣稱通過。 |
| 移轉審查 fixtures | [migration tests](../../tests/test_migration_review.py) 使用 Git init／commit／tree／archive 相關操作、symlink、FIFO 與 Unix socket。fixtures 自行設定本地 Git 身分，不需要帳號或外部 repo。 |
| Hooks 與提醒 | [project-setting tests](../../tests/test_project_setting.py) 與 [package tests](../../tests/test_harness_package.py) 使用 `/bin/sh` 重播；[歷史 hook tests](../../tests/test_task_harness_hooks.py) 另有 POSIX 權限與 FIFO 案例，部分權限檢查要求非 root。 |
| 收據中斷 | [run-check tests](../../tests/test_run_check.py) 使用 `SIGINT` 與 `killpg`，需要真實自有子程序。 |

因此選擇固定 OS label `macos-15`，不建立 runner matrix。官方 [runner 支援表](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)列有此標籤；[macOS 15 arm64 image 清單](https://github.com/actions/runner-images/blob/main/images/macos/macos-15-arm64-Readme.md)列有預裝 Python3 與 Git，故不加 setup-python 或安裝步驟。該清單不保證此 repo 的 sandbox 行為在 hosted runner 上通過；仍須未來真正遠端執行確認。Linux 不符合目前 boundary，沒有執行或宣稱 Linux 通過。

Windows 依本輪明確指示排除，不建立 Windows job；[既有 native Windows 測試](../../tests/test_project_setting.py)與 skip 原樣保留。略過不等於 Windows 驗收通過。

## Action 來源與權限

2026-10-25 由官方 [actions/checkout README](https://github.com/actions/checkout)及 [v7.0.1 release](https://github.com/actions/checkout/releases/tag/v7.0.1)查核版本，再以官方 repository 的 `git ls-remote` 核對 tag，鎖定完整 SHA `3d3c42e5aac5ba805825da76410c181273ba90b1`。原始 tag 查詢見[本地紀錄](harness-gap-closure-ci-evidence/local-checks.txt)。

只授予 `contents: read`，其他未指定權限依 [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)設為 `none`。Checkout 設 `persist-credentials: false`；保留預設單一 commit checkout，tests 自建所需 Git fixtures，不取完整歷史。Job 設 10 分鐘 timeout。沒有 `pull_request_target`、`workflow_run`、自訂 token、寫入權限或發布步驟。

## 本地驗證

本地環境為 macOS 27.0.1 arm64、Python 3.15.1、Git 2.56.0，與 hosted `macos-15` 不相同。只重跑與系統前置條件直接相關的既有 targeted tests；全量 suite 留給整合主責最後統一執行。

| 檢查 | Observed／判定 | 證據 |
| --- | --- | --- |
| YAML parse、command shell syntax、diff 與連結 | 使用本機 Ruby YAML parser 讀回配置，`sh -n` 查核 run 命令；人工核對 triggers、runner、SHA、權限與 timeout；`git diff --check` 與本報告 local links 查核通過。不是 GitHub workflow schema 或 hosted execution 驗證。 | [final static checks](harness-gap-closure-ci-evidence/static-checks.txt) |
| macOS boundary 第一次執行 | 工具外層 sandbox 禁止 `/bin/ps`，15 tests 的結果為 failure／errors；保留失敗，不當作產品或 runner 通過證據。 | [原始紀錄](harness-gap-closure-ci-evidence/local-checks.txt) |
| 相同 boundary targeted tests 重試 | 在自動核准的外層工具 sandbox 外重試；產品自己的 sandbox 未變更。15 tests 全通過，含網路／寫入限制、資源限制、取消與自有子程序收尾。 | [重試紀錄](harness-gap-closure-ci-evidence/local-boundary-unsandboxed.txt) |
| Git／FIFO／Unix socket | `test_migration_review.py`：8 tests 通過。 | [本地紀錄](harness-gap-closure-ci-evidence/local-checks.txt) |
| shell 提醒 | `test_project_setting.py`：3 tests，2 通過、1 既有 Windows skip。 | [本地紀錄](harness-gap-closure-ci-evidence/local-checks.txt) |
| 中斷與收據 | `test_run_check.py`：4 tests 通過。 | [本地紀錄](harness-gap-closure-ci-evidence/local-checks.txt) |

沒有新增模仿 workflow 固定字串的測試。此次設定未新增非瑣碎程式分支，依 TDD 原則使用既有公開邊界測試與相稱靜態驗證。

## 尚未驗證與風險

沒有執行整個 suite、遠端 workflow、GitHub schema validator 或 actionlint（本機未安裝）。本地 YAML parse 與 targeted tests 不足以宣稱 CI 綠燈；hosted runner 的 `sandbox-exec` 可用性、Python 版本差異、runner／Action 相容性及 suite 總時間仍待未來經授權的遠端執行確認。映像會更新，固定 OS label 不代表固定 image bytes。

本 CI 不驗證真實模型、人工 hook 信任、原生事件重入、Desktop 操作或 Windows 資格；這些維持[補驗規格](../specs/harness-validation-gap-closure.spec.md)各自的驗收邊界。遠端若失敗，保留原始原因並修正相應邊界，不能靠跳過測試或放寬 sandbox 換取綠燈。
