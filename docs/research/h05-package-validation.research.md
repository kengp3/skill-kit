# H05A 來源與候選同步：離線驗證

日期：2026-10-25。起點：`27ead1b798a3310edd403fd71f260b0df88e3f20`。本切片只同步來源指南及候選，H05A 的真實接入、控制與 C0 補救鏈仍未完成。

## 修改範圍

- 合約指南改為指定 Codex 執行版本的真實 agent／hook 證據，不再要求 Desktop 專屬驗收。必要 hooks、真實身分／續作資格、正常信任與按影響補驗的條件保留。
- README 同步接入現況與建包命令；候選來源版本由 0.2.0 升為 0.2.1。凍結的 0.2.0 保留，不在原目錄重建。
- 重用既有 packager、handler、三事件接線及公共 CLI 測試，只調整封裝測試的預期版本。沒有新 runtime、runner 或依賴。

## TDD 與回歸

測試邊界沿用 package CLI → 獨立套件的實際註冊命令，以及 hook stdin → stdout／收據；沒有改為私有函式測試。執行版本 Python 3.15.0。

先將候選預期改為 0.2.1、尚未修改 manifest，執行：

```sh
PYTHONPATH=tests python3 -B -m unittest test_harness_package.PackageTest.test_registered_hooks_run_from_package_with_spaces -v
```

原始失敗節錄：

```text
AssertionError: '0.2.0' != '0.2.1'
Ran 1 test in 0.054s
FAILED (failures=1)
```

再更新來源 manifest，同一命令通過：

```text
Ran 1 test in 0.236s
OK
```

指南修改後執行相稱回歸：

```sh
PYTHONPATH=tests python3 -B -m unittest test_harness_package test_task_harness_hooks -v
```

```text
Ran 34 tests in 4.258s
OK
```

8 項封裝與 26 項 hook 檢查全部通過。封裝檢查涵蓋含空白路徑、實際註冊的 SessionStart／UserPromptSubmit／Stop 命令、Stop 重送去重、合約不變、必要來源缺失／連結拒絕、包內檔案篡改／遺失拒絕及原 release 不覆寫。合成 host=true 僅驗證 CLI 分支，不構成真實執行資格。

## 臨時建包與舊候選保留

在自動清除的 `TemporaryDirectory`，使用目前來源的 `scripts/package_harness.py <暫存目錄>/personal-harness-0.2.1` 建包，再以 `--verify` 驗包。直接核對包內指南及兩個 hook assets 與來源逐位元相同；沒有安裝或保留該臨時包作已核定 release。

以下為該次直接輸出；暫存路徑已於結束時移除：

```json
{
  "python": "3.15.0",
  "version": "0.2.1",
  "manifest_sha256": "210664eb7b5a478997dbc8c67b323131a5f9ed62bd51e23cdbaba8bdb7a8ae5a",
  "files": 22,
  "guide_sha256": "0a644c0d9fd6efe8fc5db2aa3700bfeffac89a19e59db18b0a1db7271e45abdf",
  "build": {
    "exit": 0,
    "stdout": "/private/var/folders/76/hd61cw513zbdlr0y7_h27dx80000gn/T/h05-package-76v0_ut0/personal-harness-0.2.1\n",
    "stderr": ""
  },
  "verify": {
    "exit": 0,
    "stdout": "210664eb7b5a478997dbc8c67b323131a5f9ed62bd51e23cdbaba8bdb7a8ae5a\n/private/var/folders/76/hd61cw513zbdlr0y7_h27dx80000gn/T/h05-package-76v0_ut0/personal-harness-0.2.1\n",
    "stderr": ""
  },
  "old_candidate_found": true,
  "old_candidate_files": 23,
  "old_candidate_unchanged": true,
  "candidate_scope": "temporary directory, removed at context exit; not installed",
  "hook_assets_match_source": true,
  "guide_matches_source": true
}
```

舊候選比對目標為主 repo 的 `dist/candidates/personal-harness-0.2.0`。建包前後重新計算其 23 個一般檔案的逐檔 SHA-256，相同；此證據只涵蓋該候選，不宣稱檢查過所有全域環境。

## 未完成項目

真實候選載入／信任、原始 user-turn 與 hook 續作鏈、原生取消與實際 agent 行為仍屬 H05；本切片沒有啟動 app-server、模型 trial 或安裝候選。Python 3.10 與 Windows 原生命令未實測。未修改 handler、全域設定、其他專案、日常啟用版本或快取，H05A 不標 done。
