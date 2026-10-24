# H02 必要 hooks 的離線候選封裝驗證

日期：2026-10-25。範圍：來源與套件 CLI；沒有模型 trial、安裝、啟用或快取修改。

## 改動與結果

沿用既有 `scripts/package_harness.py`，明列必要的 `hooks/hooks.json` 與 `hooks/task_harness.py` 來源；重用原有缺失／符號連結拒絕及內容 manifest，不新增打包依賴或安裝流程。manifest 版本為 0.2.0，保留四個相依 skills 與全部引用文件。

新增候選的三個事件分別指向同一 Python handler。POSIX 使用 `python3` 與引號保護的 `PLUGIN_ROOT`；Windows 候選覆寫使用 `cmd /d /c py -3` 與 `PLUGIN_ROOT`，但未在 Windows 驗證。命令不含開發者路徑；Python 或宿主載入資格不足仍屬必要接入缺口。

Python 3.15.0 執行 `python3 -B -m unittest discover -s tests -p test_harness_package.py -v`：8 項通過。驗證涵蓋：

- 實際註冊命令從 checkout 外、套件與專案都含空白的路徑執行三事件；Stop 重送只保留一次收據，合約內容不變。
- hook 設定及 handler 都在內容 manifest；任一檔修改或遺失，驗包失敗。
- hook 設定／handler 遺失、handler／hook 根目錄為符號連結時，建包失敗且不留下 release。
- 保留既有 skills、獨立 run_check、排除 research、拒絕覆寫 release 及輸出越入 runtime 來源的檢查。

第一個垂直切片先由實際候選版本缺失使測試失敗，再加入封裝與註冊通過；後續必要來源負例重用既有驗證即通過，沒有為產生失敗而回退已完成程式。[原始 red／green 結果](tdd-cli-results.json)保留命令與輸出。

整合檢查 `PYTHONPATH=tests python3 -B -m unittest test_harness_package test_task_harness_hooks -v`：32 項通過（8 項封裝、24 項 runtime），原始輸出也保存在上述證據檔。

## 依據與限制

[官方 hooks 文件](https://learn.chatgpt.com/docs/hooks#plugin-bundled-hooks)說明 plugin hook 路徑及 `PLUGIN_ROOT`；同頁列出 `commandWindows` 覆寫與 timeout 秒數。文件核對日為 2026-10-25；引用不等於目前 Desktop 已載入候選。

合成事件的 host=true 僅用來測試 CLI 分支，不是接入資格。Desktop 載入／信任、原使用者回合識別、模型遵循、Python 3.10 及 Windows 原生命令均未實測；整套 harness 完成條件仍由 H05 負責。未改舊 release、全域設定、其他專案、啟用版本或快取。
