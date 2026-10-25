# Kengp3 Harness 原生安裝與載入驗證

日期：2026-10-25；Codex CLI／stdio app-server `0.164.0`；候選 `0.2.1`。

## 結論

`kengp3-harness@kengp3-harness-local` 在全新隔離 state 完成原生安裝，並由新啟動的 app-server 讀回四個啟用 skills 與三個啟用 hooks，來源皆在測試專用快取。停用、重新啟用及移除對照均通過，載入清單沒有 warnings／errors。

三個 hooks 的 `trustStatus` 均為 `untrusted`。本次證明安裝及 loader 可辨識候選，不代表已取得原生信任或 handler 已執行；未啟動 thread、模型回合或完整任務生命週期 trial。

## 隔離與保留

- 測試根：`/private/tmp/kengp3-harness-native-4kf9f3g3`；state、catalog、project 分開。僅在子程序環境指定測試 `CODEX_HOME`，沒有變更使用者的環境設定。
- Catalog 使用本次新名稱候選的完整副本；沒有修改來源、舊候選、既有安裝或其他專案。
- 未登入或複製 auth；測試設定使用 file credential store，未取得登入資料。所有 RPC 僅限 `initialize`、`initialized`、`plugin/read`、`skills/list`、`hooks/list`。
- 日常 `/Users/kengp3/.codex/config.toml` 與日常 `plugins/` 下共 6,785 個一般非符號連結檔案，前後路徑集合及 SHA-256 完全一致。此查核不涵蓋所有全域檔案或 OS keychain。

## Expected → observed → proof

| 查核 | 預期與實際觀測 | 直接證據 |
| --- | --- | --- |
| 安裝前 | 原生 list：installed 空；available 包含新名稱 `0.2.1` | [before-install.json](kengp3-harness-native-validation-20261025-evidence/before-install.json) |
| 原生安裝 | CLI exit 0；回傳正確 plugin ID、版本及測試 state 內的 installedPath | [install.json](kengp3-harness-native-validation-20261025-evidence/install.json) |
| 安裝內容 | 實際快取通過既有 package verifier，manifest 指紋與候選一致 | [installed-package-verification.json](kengp3-harness-native-validation-20261025-evidence/installed-package-verification.json) |
| 新程序載入 | installed／enabled=true；四個 skills、三個 hooks；無載入錯誤 | [loaded-rpc.json](kengp3-harness-native-validation-20261025-evidence/loaded-rpc.json) |
| 停用對照 | 只改測試 state 的該 plugin enabled=false；新程序讀回 installed=true、enabled=false，skills／hooks 均為零 | [disabled-rpc.json](kengp3-harness-native-validation-20261025-evidence/disabled-rpc.json) |
| 重新啟用 | 只恢復測試 plugin；另一個新程序重新讀回四個 skills／三個 hooks | [reloaded-rpc.json](kengp3-harness-native-validation-20261025-evidence/reloaded-rpc.json) |
| 原生移除 | CLI exit 0；新程序讀回 installed／enabled=false，skills／hooks 均為零，測試快取消失 | [remove.json](kengp3-harness-native-validation-20261025-evidence/remove.json)、[removed-rpc.json](kengp3-harness-native-validation-20261025-evidence/removed-rpc.json) |
| 保留既有狀態 | 6,785 個檔案無新增、刪除或內容改變 | [before](kengp3-harness-native-validation-20261025-evidence/existing-installation-before.json)、[after](kengp3-harness-native-validation-20261025-evidence/existing-installation-after.json) |

載入的技能全名為 `kengp3-harness:ai-code-review`、`kengp3-harness:define-task`、`kengp3-harness:project-setting`、`kengp3-harness:task-harness`。個別 skill 名稱未變，namespace 由新 plugin ID 提供。三個事件為 `sessionStart`、`userPromptSubmit`、`stop`，各一個 command handler，全部指向同一測試快取的 `hooks/task_harness.py`。

候選及實際快取的 manifest SHA-256：

```text
ad40104033a0698dae8170bf826f9edfe4af05fd53f9bb3698d07cb3e4664628
```

## 收尾與限制

已透過原生 CLI 移除測試 plugin 及 marketplace；最終 installed 清單為空，測試 plugin 快取已移除。四個自有 app-server 程序均 exit 0。保留測試來源及證據供查核，沒有把測試安裝留在日常 state。

未驗證原生信任、handler 執行、模型遵循、完整任務生命週期或 Desktop UI；也未設定產品任務的 host 資格旗標。若要驗證 hooks 可實際執行，須在隔離 state 透過正常信任流程核對精確來源及命令後再測。

## 方法與來源

- [機械摘要](kengp3-harness-native-validation-20261025-evidence/summary.json)、[本次 RPC 檢查程式快照](kengp3-harness-native-validation-20261025-evidence/check_load.py)。程式快照依賴本次暫存設定，並非獨立驗證工具。
- [OpenAI 官方 state 路徑說明](https://learn.chatgpt.com/docs/config-file/config-advanced)：state 由 `CODEX_HOME` 指定。
- [OpenAI 官方 Developer commands](https://learn.chatgpt.com/docs/developer-commands)：原生 marketplace add／plugin add、list、remove；本次命令另以本機 `--help` 核對。
- [OpenAI 官方 app-server 文件](https://learn.chatgpt.com/docs/app-server)：skills／hooks 清單介面；本次參數另以 `0.164.0` 產生的 JSON Schema 核對。`plugin/read` 是實驗介面，本次僅用於隔離開發驗證。
