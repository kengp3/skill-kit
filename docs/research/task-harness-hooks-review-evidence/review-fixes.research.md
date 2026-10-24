# H04 審查缺口修正：離線證據

日期：2026-10-25。固定審查基線：`75cf0754e0524a2b39361a1152bf5bcca186dd7a`。

## 修正與驗證

1. `cwd` 含 `..` 時，先拒絕符號連結並確認目錄存在，再解析實際位置，避免 lexical 歸屬判斷誤准專案外事件。新增公共 CLI 負例先失敗、修正後通過；拒絕時合約不變、不產生收據，專案外臨時目錄保持空白。
2. 合約目錄列舉使用會明示失敗的 `iterdir`，保留直接 `.md` 篩選及 64 份上限。新增非 root POSIX 權限負例先失敗、修正後回報未就緒且不寫收據；測試最後恢復臨時目錄權限。
3. 技能設定加入 `policy.allow_implicit_invocation: false`。本機官方 skill-creator 的 `references/openai_yaml.md` 定義此欄位預設 true，false 可保留明確呼叫並關閉預設隱式注入。讀回原檔與臨時候選包內容相同；manifest 驗證通過，不以此宣稱 Desktop 實際啟用已驗證。

## 結果

Python 3.15.0：26 項 hook CLI 與 8 項封裝測試全部通過，共 34 項、3.338 秒。完整 red/green stdout、stderr 與 return code 見 [tdd-results.json](tdd-results.json)。候選包讀回證據見 [package-policy.json](package-policy.json)；臨時包已由 TemporaryDirectory 清除，未安裝。

可重現命令：`PYTHONPATH=tests python3 -B -m unittest test_task_harness_hooks test_harness_package -v`。

本次只改兩個 runtime 邊界、技能啟用設定及對應測試。未新增依賴、OS 控制或監控；未修改全域設定、宿主快取或其他專案。

## 限制

沒有執行模型／Desktop trial，也未證明真實宿主事件、Stop 語意與跨回合識別。Python 3.10 及 Windows 原生行為仍待驗證。此報告只支持修正後的離線行為，完整 harness 驗收仍依 H05。
