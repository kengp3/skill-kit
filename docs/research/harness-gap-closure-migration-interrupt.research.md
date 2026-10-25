# G02：真實移轉 workflow 命令中斷與同任務恢復

日期：2026-10-26（Asia/Taipei）。對應 G02／V04；Windows 依使用者指示排除。

## 目前判定

**G02／V04 的真實 workflow 命令中斷與同移轉恢復通過。** 實際模型在同一原生命令寫入新設定並進入 checkpoint，觀測 PID／token／磁碟現況後施加一次 `SIGTERM`；確認原執行者退出後，明確新授權接續同一移轉，重新讀回三門檻才刪舊檔，歷史 bytes/location 與一次成果保留。第一次控制器資格失敗單獨保留，不列通過。

本案只驗證「實際模型移轉寫入新設定後、刪除舊設定前，包含寫入與 checkpoint 的同一個 workflow 命令遭 OS signal，確認原執行者退出，再以明確新授權續作同一移轉」。checkpoint 等待被中斷不證明 write／unlink syscall crash、斷電、原子寫入、交易回滾或任意副作用的 exactly-once 保證。

## 固定來源與隔離

- 固定候選為 `/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0`，manifest SHA-256 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。控制器重驗 manifest 所列全部檔案，再實體複製四個 skills，省略 `scripts/`；不使用 symlink 或 live source。
- 案例位於自有 `/private/tmp/g02-migration-*`，只從已接入的 demo-002 複製 `AGENTS.md` 與 `project-setting.md` 語意，並非全量應用程式 clone。驗收目錄移除已接入 harness 分類與表，改放自造可辨識舊版 JSON、歷史合約／JSONL、一次完成 ledger 與 preserve canary；這是移轉前初態，**新設定由實際模型寫入**。不讀 `.planning/` 舊流程，也不修改 demo 原工作區。
- 獨立 `CODEX_HOME` state `0700`、認證副本 `0600`，認證留在 repo 與證據目錄外。隔離 config 明確停用三個 HOME user skill paths；`skills/list` 核對四個候選技能 enabled、user skills disabled；plugins 停用。native hooks 在本案例停用，由模型依候選規則接手，不宣稱 V01 授信通過。
- 每個原生 thread 使用 `runtimeWorkspaceRoots=[case]`、`workspace-write`、`on-request`、`approvalsReviewer=auto_review`；核對 instructionSources 只有副本 AGENTS。外層維護控制器 scoped 提升僅為觀測／signal 自有程序，不改 native 模型 sandbox、全域安全屬性、信任資料庫或網路。無共享 daemon。
- [native-migration.py](harness-gap-closure-migration-interrupt-evidence/native-migration.py) 為維護者選配工具，公開 CLI 為 `preflight`、`run`、`check`；產品模型只用原生命令／檔案能力，不執行 Python／Node／helper。原生等待或 timeout 不等於終態，控制器不自動重派。

## 第一次試跑：不列為通過

預期 → 觀測 → raw → 判定：普通唯讀 probe 正常，新設定寫入命令確實進入 checkpoint，但控制器 `/bin/ps` 被外層 sandbox 拒絕 → 沒有發送預定 OS signal → [原始 RPC](harness-gap-closure-migration-interrupt-evidence/failed-initial/original-rpc.jsonl)、[首案磁碟現況](harness-gap-closure-migration-interrupt-evidence/failed-initial/artifacts/)、[原生查回](harness-gap-closure-migration-interrupt-evidence/failed-initial/native-readback.json) → **不通過，屬控制器資格失敗**。

未直接重啟或假稱成功：先觀測原 controller PID `98560`、server `98568`、checkpoint `4746` 均不存在；再以同 state 新 server 只做 `thread/read`，核對原 probe `completed`、原移轉 turn `interrupted`，query server `5254` 亦正常退出。保存原 settings／歷史資料與 session contexts、確認全域 config/auth hashes 不變後才清除原 case/state。直接觀測與清理結果在 [investigation.json](harness-gap-closure-migration-interrupt-evidence/failed-initial/investigation.json)。這個 interrupted 是原控制器失敗後的宿主收尾，不是本案要求的 OS signal 命中證據。

修正僅限驗收控制器：在任何 native 試驗前增加公開程序觀測 preflight，普通 sandbox [真實紅燈](harness-gap-closure-migration-interrupt-evidence/preflight-red.stderr)，scoped 提升後[綠燈](harness-gap-closure-migration-interrupt-evidence/preflight-green.stdout)。成果 checker 在尚無正式產物時亦[真實失敗](harness-gap-closure-migration-interrupt-evidence/red-check.stderr)，沒有改產品或歷史 driver。

## 正式試驗

正式案例原始資料位於 [formal/](harness-gap-closure-migration-interrupt-evidence/formal/)；[preconditions.json](harness-gap-closure-migration-interrupt-evidence/formal/preconditions.json) 記錄精確 case root、候選安裝檔 hashes、Codex CLI `0.164.0`、state/auth 權限及 demo 複製輸入 hashes。模型為 `gpt-6.1-sol`、effort `low`，有選取的 [turn contexts](harness-gap-closure-migration-interrupt-evidence/formal/session-contexts.json)。普通 probe `completed` 後才開始故障案；provider 429 與 native backoff 保存在 [server stderr](harness-gap-closure-migration-interrupt-evidence/formal/original-server.stderr.log)，始終沿用原 handle，沒有因 timeout 重派。

| 預期 | 實際觀測 | raw 與判定 |
| --- | --- | --- |
| 真實移轉命令已寫新檔、未刪舊檔 | native item `exec-44286f10-920c-4b42-b84c-a5e6af085278` 使用 `awk` 建立新內容、`mv` 寫入 `project-setting.md`，再於同一命令 `exec` checkpoint；模型自行依規格組出內容，未人工預置 partial state | [原始 RPC](harness-gap-closure-migration-interrupt-evidence/formal/original-rpc.jsonl) 第 369 行為 inProgress；[at-window](harness-gap-closure-migration-interrupt-evidence/formal/at-window/) 舊 JSON 仍為初態 bytes，新檔 hash 已變；通過 |
| 一次真正 OS signal 命中正確程序 | 唯一 token `G02_MIGRATION_0f09bd5e26df4414b9e78c8d77a1d2bf`、checkpoint.pid 與 OS PID `11111` 一致，`/bin/sleep 120` 為原 server `5541` 之子；開始約 57.858 ms 後施加唯一 SIGTERM | [target 與 ancestry](harness-gap-closure-migration-interrupt-evidence/formal/signal-target.json)、[signal](harness-gap-closure-migration-interrupt-evidence/formal/signal.json)；同 item exit `143`，不是只殺另一個普通 sleep；通過 |
| 中斷後不自動繼續或重試 | signal 後立即對原 turn 發一次 `turn/interrupt`；原生終態為 `interrupted`，signal 後無新 command/file-change item start，舊檔仍在 | 原 RPC 第 370／371／376 行、[after-signal](harness-gap-closure-migration-interrupt-evidence/formal/after-signal/)、[verification](harness-gap-closure-migration-interrupt-evidence/formal/verification.json)；通過 |
| 查明原 server／worker／tool child 全退出才續作 | 原 server `5541`、code-mode-host `5628`、checkpoint `11111` 均退出；確認集合為空後才建立新 server `11119` 並送明確新授權 | [stop-confirmation](harness-gap-closure-migration-interrupt-evidence/formal/stop-confirmation.json)、[summary](harness-gap-closure-migration-interrupt-evidence/formal/summary.json)、[新授權 prompt](harness-gap-closure-migration-interrupt-evidence/formal/resume-prompt.txt)；通過 |
| 三門檻本回合重讀後才刪舊檔 | 同一 `G02-migration` 及同一對帳位置；讀兩設定、固定候選 provider／migration 規格與歷史資料，將無遺漏、格式有效、目標版本正常讀回三項證據保存並讀回後，僅 `rm harness-project.json` 一次，exit 0；再確認舊檔無檔案／symlink、新設定不變 | [resume RPC](harness-gap-closure-migration-interrupt-evidence/formal/resume-rpc.jsonl) 第 196／205／207 行、[模型對帳](harness-gap-closure-migration-interrupt-evidence/formal/final/docs/research/g02-migration.research.md)；原生 resume `completed`；通過 |
| 舊產物不搬移、不重做成果或另造合約 | 新設定 at-window／after-signal／final bytes 完全相同；legacy.md、old.jsonl、ledger、preserve 全階段皆比對已知 literal bytes。未建立活動合約或設定備份，ledger 仍精確 `EXISTING_ONCE\n` | [final](harness-gap-closure-migration-interrupt-evidence/formal/final/)、[公開成果 CLI 核對](harness-gap-closure-migration-interrupt-evidence/formal/green-check.json)、verification；通過 |

原 thread `01a173cc-cb0c-7103-9a31-ababf559c573`／turn `01a173cc-ebf4-7721-a93b-20ad553362ff`；續作 thread `01a173d4-4787-7af0-91cb-34c857a470d3`／turn `01a173d4-4792-7be2-ae63-07a8d1402fcd`。這是新 native thread 接續相同移轉，不是 CLI session-resume 或新產品開發任務。歷史 legacy.md 是保存 canary，不冒稱符合新版活動合約格式；本案依規格沿用移轉對帳身分，不另建第二份活動合約。

模型續作中的普通 `ps` 被 native sandbox 拒絕；模型據控制器已保存的直接退出證據接手，沒有自行解除 sandbox。另有列舉不存在 `.codex` 的 `rg` exit 2；其前面的設定讀取正常，模型後續另行完整讀回，未將聚合 exit code 當三門檻證明。兩個 server 均 exit 0 且不存在，全域 config/auth 前後 hash 完全相同；只在 native 終態後刪除自有 case/state，認證副本已移除。

完成前獨立執行 [check-evidence.py](harness-gap-closure-migration-interrupt-evidence/check-evidence.py)，核對事件時序、signal 後無新工具、三門檻讀回後唯一刪檔及已知 bytes。隱私掃描初次在衍生 `session_meta.creator_account_id` 發現與 auth account ID 相同的值；[紅燈紀錄](harness-gap-closure-migration-interrupt-evidence/credential-scan-red.json)只保留欄位名稱，無值。改為只匯出 turn/model/effort/timestamp，修正維護 driver 的匯出範圍，原始 RPC 保持不變；再次以 5 個認證相關長字串值掃描所有證據，命中 0。verification 保存各證據 SHA-256。未重跑 full unittest；本案沒有產品變更，整體維護測試由主責統一執行。
