# 統一專案設定：原生 Stop 與同合約續作補充驗收

日期：2026-10-25（Asia/Taipei）。範圍：T08 補充驗收，對應規格 D4–D5、E 的中斷恢復、H2 的使用者 Stop；H3 僅涵蓋可觀測的 thread／turn 識別與跨對話接手。

## 結果

**本次真實 native Stop 與明確授權續作案例通過。** 在實際 `commandExecution` 的 `item/started`／`inProgress` 事件及 OS 程序均可觀測時，控制器對該回合發送一次 `turn/interrupt`，原生終態為 `interrupted`。中斷後沒有產出 T2，原合約及一次完成的 ledger 保留；確認舊執行者退出及受控程序消失後，新對話在明確授權下接續同一合約，先保存／讀回接手，再完成 T2。

**宿主限制：原生回合中斷不等於同步終止已啟動的 shell 子程序。** 本次 `/bin/sleep 20` 在 `interrupted` 後仍暫時存活。控制器等其消失、關閉並回收原 app-server 後才允許接手，沒有把中斷命令視為成功，也沒有靠自動重試解決狀態不明。此受控命令不寫產品資料；這個結果不能證明任意有副作用的命令在 Stop 後都會即時停止。

## 材料與方法

- 驗收候選：`/private/tmp/unified-review-final-0.3.0`，`runtime-manifest.json` SHA256：`7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。
- 原生宿主：Codex CLI `0.164.0` 的 `app-server --stdio`；真實模型為 `gpt-6.1-sol`、推理強度 `low`。模型／強度由保存的原生 turn context 佐證，合約無法觀測的 session／user-turn ID 保持 `null`，未冒充可取得。
- 使用真正的 `initialize`、`thread/start`、`turn/start`、`turn/interrupt`、`thread/read`，不是 mock、事件 replay 或 Desktop UI 操作。官方 [App Server 文件](https://learn.chatgpt.com/docs/app-server) 說明這些串流事件與中斷介面；本案例仍以實際 raw RPC 為驗收依據。
- 兩個 persistent thread，共用同一個隔離專案及唯一合約。hooks 刻意停用，驗證 task-harness 的主責模型檢查路徑。候選的四個技能複製到測試專案；`scripts/` 排除，沒有安裝使用者必要 runtime。測試控制器本身是維護者工具，見 [native-stop.py](unified-project-settings-native-stop-evidence/native-stop.py)。
- 唯一 canary 為帶隨機 token 的獨立 `/bin/sh -c` 前景命令，內含 `/bin/sleep 20`。觸發條件精確比對同一 thread／turn、`item/started`、`commandExecution`、`inProgress` 及完整命令，另外確認 OS 中這次唯一 shell／sleep 的 PID。只比對輸出文字、已完成事件或固定等待時間都不會觸發中斷；driver 有相應正反自檢。
- 使用隔離的暫存 state、認證副本與專案，不修改全域設定或其他既有專案。認證副本權限 `0600`，state `0700`；測後已直接確認暫存根目錄消失，證據沒有保存認證內容。

## 實際預期、觀測與證據

| 項目 | 預期 | 實際觀測 | 證據 |
| --- | --- | --- | --- |
| 中斷命中真實執行窗口 | 受控工具已開始，尚無完成事件 | 原 RPC 第 157 行為正確命令的 `inProgress`；OS shell PID `49915`、sleep PID `49916` 存在。57.695 ms 後發送中斷 | [original-rpc.jsonl](unified-project-settings-native-stop-evidence/original-rpc.jsonl)、[summary.json](unified-project-settings-native-stop-evidence/summary.json) |
| 使用者 Stop | 只中斷本次 thread／turn，取得原生中斷終態 | 第 158 行為唯一 `turn/interrupt`，第 163 行為 `interrupted`，間隔 5.318 ms；沒有 canary `item/completed`，不推論命令 exit 0 | [verification.json](unified-project-settings-native-stop-evidence/verification.json)、原 RPC |
| Stop 不為紀錄或完成要求繼續 | 不寫 T2，不重播既有成果 | 原串流終態後未出現新的工具事件；保存的 Stop 後快照沒有 T2，ledger 仍精確 `EXISTING_ONCE\n`，preserve 不變 | [after-stop/](unified-project-settings-native-stop-evidence/after-stop/)、原 RPC |
| 查明原工具與原執行者狀態 | 未確認退出前不得交接 | `interrupted` 後最初仍觀測到相同 shell／sleep；等待後兩者清單為空，原 app-server PID `49620` 已回收且不存在。原 app-server exit 0 僅屬 server，不屬 canary | [stop-confirmation.json](unified-project-settings-native-stop-evidence/stop-confirmation.json)、summary |
| 明確新授權及同合約恢復 | 核對保存、產品現況、未知操作及舊執行者後才繼續 | 約在中斷請求 19.916 秒後，才送出新的使用者執行授權；新 thread 先讀取合約、ledger、preserve 與停止證據，保存並讀回接手／授權，再建立 T2。未重跑 canary | [prompt-resume.txt](unified-project-settings-native-stop-evidence/prompt-resume.txt)、[resume-rpc.jsonl](unified-project-settings-native-stop-evidence/resume-rpc.jsonl) |
| 最終成果與保存 | 唯一合約維持 task ID，既有成果不重做 | 同一 `task_id=native-stop`、唯一合約狀態 `done`；T2 精確 `STOP_RESUMED_OK\n`；ledger 一次、preserve 不變，未解未知操作清單為空 | [final/](unified-project-settings-native-stop-evidence/final/)、verification |
| 全域／認證清理 | 隔離操作，無 credential 外洩 | 全域 config/auth 的前後 digest 相同；暫存根目錄刪除後重新確認不存在；另行比對證據內容未包含認證檔中的長字串值 | summary、verification |

原 thread：`01a172ca-a9ff-7da2-8822-6a7284b19789`；原 turn：`01a172ca-ac3c-7420-a3a2-c20270f6dd44`。續作 thread：`01a172cb-748e-7c71-8af4-c093300c96a8`；續作 turn：`01a172cb-7496-7be0-bd31-513d40ee60b4`。兩個自有 app-server 均已退出。這些是原生介面 ID；合約不把 thread ID 當成不可觀測的 session ID。

## 驗證邊界

1. 本案例證明的是使用者 Stop、Stop 後沒有後續模型工具工作，以及核對完真實原操作／原執行者狀態後的明確續作。受控命令沒有產品副作用；不能外推為任意命令的中斷、回滾或 exactly-once 保證。程序觀測與退出檢查是測試控制器執行，不能宣稱純 Markdown 提供 OS 程序鎖。
2. 沒有發生 `turn/start` 回應遺失，也沒有實際的子 agent 啟動逾時。本案例核對的是已啟動工具的中斷後未知結果；**H7 的子 agent 逾時／未知啟動仍由其他驗收項目提供證據**，不以本次結果替代。
3. hooks 刻意停用，因此未驗證 hook 恢復／重複事件 re-entry、條件阻擋或正常 Stop hook 自動續作。被動 Stop `echo {}` 也不能當成會產生條件續作的證據；使用者新授權才啟動本次續作。
4. 未測 Desktop 的停止按鈕或 UI 呈現、Windows、多主責競爭或宿主間識別互通。沒有觀測到的 hook 事件、模型切換或技術收據均未補造。

原始 RPC、prompt、三個快照、終態及另外執行的事後核對均保存在 [證據目錄](unified-project-settings-native-stop-evidence/)。`verification.json` 記錄既有證據的 SHA256 及獨立讀回結果；它是完成 native trial 後的檔案／事件核對，沒有重播產品操作。
