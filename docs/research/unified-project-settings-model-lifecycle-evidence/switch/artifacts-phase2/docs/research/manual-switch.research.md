# manual-switch 核對紀錄

本任務沿用唯一合約 [manual-switch.task-contract.md](../plans/manual-switch.task-contract.md)。隔離測試的 hooks 保持停用，由主責模型主動核對；未建立 hook 收據、安裝工具或服務、執行 helper scripts。

## 派工與模型選擇

`project-setting.md` 只有 `schema_version = 1`，未設定任務、角色、階段或專案模型。兩次派工均用 `fork_turns=none` 與自足輸入，省略 `model`、`reasoning_effort` 參數，按模型選擇規則第 6 順位原生繼承派工時的主責選擇。原 worker handle 為 `/root/old_worker`；本回合先用 `collaboration.list_agents` 核對為 `running`，未重啟或重派。新 worker handle 為 `/root/new_worker`。

使用者說明測試控制器透過原生 `turn/start` 將本回合主責選擇切換為 `gpt-6-sol / medium`；本回合宿主 `model_instructions` 明示主責模型為 `gpt-6-sol`。這項切換只影響之後原生繼承的派工，不回溯變更 old_worker，也不是全體 agent 覆寫。派工回應只提供 worker handle，未提供任一 worker 的實際後端模型或推理強度；因此兩者的 observed model/effort 均保留未知。新 worker 的 medium 強度依使用者提供的 `turn/start` 資訊記錄，未有獨立宿主回傳值。

## 執行與結果

本回合建立空白 `gate-old.txt` 前，確認原 worker `running`、gate 不存在。建立後，old_worker 回報它在 `2026-10-25 11:19:57 UTC` 確認 gate 存在（檢查 `exit_code=0`）才讀取 `preserve.txt`；其開始時間為 `11:18:39 UTC`，在 600 秒上限內。old_worker 回報 `actual_repr: b'KEEP_EXISTING_CONTENT\n'`、長度 22、hex `4b4545505f4558495354494e475f434f4e54454e540a`，結果 PASS。時間與先後順序來自 worker 回報，主責未取得獨立計時事件紀錄。

new_worker 獨立回報 `wc -c` 為 22，`od -An -tx1 -v` 的 hex 同為 `4b4545505f4558495354494e475f434f4e54454e540a`，結果 PASS。主責在兩者回報後再次唯讀執行 `wc -c` 與 `od -An -tx1 -v`，取得相同的 22 bytes 與 hex；此位元組序列精確等於 ASCII `KEEP_EXISTING_CONTENT` 加一個 LF。主責也讀回 `project-setting.md`，內容仍為原文件分類表及 `schema_version = 1`。

`git status` 無法提供變更清單，因該目錄不是 Git repository。驗收依據為兩個原生 worker 的回報、主責對現有檔案的獨立唯讀核對，以及合約保存與讀回；沒有將不可觀測的模型身分或 hook 事件視作驗收證據。
