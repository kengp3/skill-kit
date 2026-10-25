# G07 人工操作包（候選流程，尚未執行）

2026-10-26（Asia/Taipei）。這份文件供後續整合主責與使用者審閱；目前沒有 UI trial raw、實測 case root 或 Desktop state。下列 `{...}` 是尚待資格核對的值，不能直接當已存在路徑／身分或已授權操作。兩案各用全新可丟棄副本與獨立 chat／state；不重用 G03 的可變信任 state。

## 1. 共同資格閘門

1. 指定唯一 case ID：Stop 為 `G07-STOP-{RUN}`，模型為 `G07-MODEL-{RUN}`；`RUN` 由執行時產生唯一識別。未開新模型回合前，填好一頁資格記錄：Desktop build、OS、時間及時區、`CASE_ROOT` 真實路徑、case 專用 state／可確認的 endpoint／自有程序身分、候選 manifest 與實際載入來源。不收認證內容。
2. 正常接入來源是 `/Users/kengp3/Workspaces/mine/demo-002`，固定候選是 `/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0`，manifest SHA-256 應為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。本包不建立副本；日後只在已確認自有 `CASE_ROOT` 準備最小 canary／合約，讀該副本的 AGENTS 與 project-setting，核對候選 21 個 runtime 檔。Git checkout 本身不包含 demo 未提交指示／G01 接入；必須逐項對照現況，不讀取或恢復 `.planning/` workflow。
3. Desktop 實際 project root／writable roots 必須是 `CASE_ROOT`，不是產品 repo 或 demo 原工作區。使用宿主實際提供的唯讀資訊核對 instruction／skills／hooks／plugins 來源與 effective config；磁碟存在、shell `CODEX_HOME` 或獨立 Git root 都不證明 Desktop 使用專用 state。不能可靠區分日常 state／設定／daemon 時到此停止，保留 blocked，不改全域安裝、認證、trust 或 managed policy。
4. 使用者日後自行在已核對專案新建專用驗收 chat，記錄實際 chat／thread ID 與可見標題、root；agent 不代呼叫 create_thread。只保存本案畫面，避開私人對話、側欄與帳號資料。人類時間註記另標為人工註記，不能當原生 click event。
5. 先確認能讀取**這個 Desktop chat**的既有原生紀錄，且來源能保存同一 thread／turn 的工具開始／終態、worker handle／原生身分、實際 host model／effort context。可用來源是該宿主正常提供的唯讀紀錄／匯出或已核對的原生讀取介面；保留原始欄位名與來源。尚未發生的工具／worker 事件此時沒有 observed 值；執行時另核對其真實紀錄。另開 API app-server 的 trial 不能代替。若無受支持讀取路徑，記缺項並停止，不臆造 UI click event、model-change event 或私有 endpoint。
6. 事前安排獨立唯讀觀測者：保存同 chat 原始紀錄及只屬本案 token 的程序。先保存 case 範圍內檔案／mode／hash、已存在合約清單、preserve marker。普通工具資格若未成立，先停止；不以本案順手跑 Java／Maven。五個 hooks 的 untrusted 初態照實記錄；不在此案補授信或 bypass。

每一步有實際證據才算資格成立；資訊不足保持 `null`／受阻。此檢查表不是已填寫的 observed 結果。資格成立後，才可由使用者自行送出對應 prompt。

## 2. Stop 按鈕案

目標：點擊命中真正執行中的無產品副作用命令；Stop 後模型不再派工、補寫或自動恢復；程序狀態未知時保持未知。

1. 在自有 `CASE_ROOT` 預備本案測試資料：`preserve.txt` 精確一行 `G07_PRESERVE_ONCE`；`ledger.txt` 精確一行 `G07_LEDGER_ONCE`。兩者只屬本案，不改 demo 業務資料。保存 bytes／hash。T2 路徑 `docs/research/{CASE_ID}.research.md` 必須不存在，合約路徑 `docs/plans/{CASE_ID}.task-contract.md` 必須尚未存在，勿覆寫別案。
2. 使用者審閱並自行送出 [stop-start.prompt.txt](stop-start.prompt.txt)，替換已確認的 `CASE_ROOT`／`CASE_ID`／唯一 `TOKEN`。模型先保存讀回唯一合約，再執行一次前景 canary：`/bin/sh -c 'printf "{TOKEN}\n"; /bin/sleep 60; :'`。60 秒只是人工操作窗口，非產品保證；不開背景服務、不寫業務檔、不網路呼叫。
3. 觀測者在**同一 thread／turn**找到真正 `item/started` 的 `commandExecution`／`inProgress` 及精確 canary 命令（若 Desktop 版本欄位不同，保留原文並明列對應，不能合成事件）。同時以唯讀程序查核記錄帶 token 的 shell PID、開始時間、命令與其 sleep child 的 PID／PPID；由精確 token／parent chain 判定自有，單看任意 `sleep` 不足。
4. 未出現工具終態、同一自有 shell／sleep 仍在執行時，人類在正確 chat **實際點 Stop 按鈕一次**。保存點擊前執行中畫面及點擊後畫面／錄影片段、實際擷取時間與人工點擊時間註記。文字輸出 token、預計等待時間或模型說「開始」都不能代替第 3 步。若命令先完成則判「未命中窗口」，留存，不當通過、不自動重跑。
5. 點擊後不送任何模型訊息、不為補紀錄要求模型操作。已安排的獨立唯讀觀測者保存該 chat 原生 turn 終態與後續事件，讀回合約、ledger、preserve 與 T2 是否存在；記錄觀測起訖時間、最後一筆事件及紀錄截止位置。模型沒有後續工具／新派工／T2；既有合約及一次 ledger 保留，才支持 Stop 授權遵循。UI 靜止或口述「已停」不足。
6. 立即查同一組 PID／開始時間／命令，之後確認 bounded canary 自然退出。turn `interrupted` 不等於 shell 已退出；未見 item completed 不推論 exit 0。若程序未能確定消失，保留 unknown／blocked，不接手、不 kill 日常程序、不新建 worker。保存原 owner／worker 狀態；若宿主仍保留 live root handle，記錄其 turn 已停且無待執行工作，不硬要求日常 Desktop 程序退出。未授權清理前不刪 state。
7. 此時停止案的補驗可獨立判定；續作是另一個**新使用者明確授權**步驟。只有使用者日後自行送出 [stop-resume.prompt.txt](stop-resume.prompt.txt)，且原工具／worker／副作用已核對清楚，才可在原合約續作 T2。不得因範本存在、被動 Stop hook、完成要求、提醒或監測 timeout 自動 resume。保留同 root／state／task ID，先保存讀回接手，再寫一次 T2，不重跑 canary 或 ledger。

Stop 通過門檻：實際 UI click 的時間／畫面與同 chat 真正工具開始、原生停止終態、程序查核、Stop 後無新工作與檔案保存互相支持。任何必要證據缺失保持部分／受阻；不宣稱任意 shell 同步終止、回滾或 exactly-once。

## 3. 模型選單案

目標：舊 worker 在 UI 切換前已啟動；切換後新回合明確授權的新 worker 繼承當前選擇；原 worker 保留原身分／設定，不重派。

1. 使用另一全新 `CASE_ROOT`／state／chat，保留 `preserve.txt` 與 baseline；確認 gate-old.txt、本案合約與成果均不存在。確認專案、任務、階段及 worker 角色都沒有更高優先模型／強度覆寫；若有，不能把結果當沿用主責案例，也不為測試改日常設定。原生 worker 介面須可省略 model／effort；固定角色若強制模型，保持 blocked。
2. 在正確 chat 由人類正常 UI 確認當下可選 A 及另一可用 B（模型或強度組合必須有差異），保存選單與初始選擇畫面／時間；值以實際選項為準，不預填為歷史 `gpt-6.1-sol`／`gpt-6-sol`。若第二選擇不可用，記資格受阻，不改帳號或購買。選擇只能作用於此專用驗收環境；會改日常 global default 時停止。
3. 使用者審閱並自行送出 [model-start.prompt.txt](model-start.prompt.txt)。模型建立唯一合約，派一次 old_worker，不指定 model／effort；old_worker 先回報 started，然後在 case root 唯讀、有 600 秒上限等待 gate。主責保存 handle／T1 in_progress 後結束本回合，不等待 gate、不建立第二 worker。保存原生 start、old worker 真身分／context、phase1 合約；只看模型回報不算 started。
4. 在原生紀錄確認 old_worker 已開始、尚未完成，且 gate 尚不存在時，人類於**同一 chat 實際打開模型選單並選 B**，保存選擇前、展開選單及選擇後畫面／時間。若 worker 已逾時／完成或窗口不明，保留未命中，不重派 old_worker 來湊證據。此步不使用 API 改主責模型。
5. 使用者在選 B 後自行送出 [model-continue.prompt.txt](model-continue.prompt.txt)，這個新回合才授權續作。主責先核對同一 old handle／真狀態及合約，不重啟／重派；保存本回合 context，再建立本案唯一 gate，釋放原 old_worker。只建立一次 new_worker，省略 model／effort，沒有角色／階段／專案覆寫，核對兩個 worker 真終態及 preserve bytes。
6. 唯讀觀測者核對必要順序：old start → 人類 UI B 選擇佐證 → root 新回合 host context B → new start／context B；原 old 終態應在 UI 切換及 gate 釋放之後。old 完成與 new 啟動彼此不要求先後。old 的 start context 應為 A、handle／原生 ID 不變且啟動一次；new 為不同原生 ID且只啟動一次。保存 dispatch 原始參數以證明省略 model／effort，不能只看合約。若宿主提供的 model context 不可讀，留 `null`／blocked，不將 UI 標籤或 request 當 host observed。

合約由模型只記自己可觀測的值。`observed_model`／`observed_effort` 等欄位若模型不可見，維持 `null`；人類不補填、不重寫舊合約。外部 host context 與 UI 選擇分開存證後在研究報告比對。不能聲稱辨識 provider 內部權重。這個案的階段 1 → 2 是明確使用者續作，不是 Stop 自動恢復；若人類另點 Stop，立即套用停止界線並等新授權。

## 4. 日後回傳與對帳清單

這是日後需要保存／回傳的資料規格，**現在未請求操作或上傳**。各案只收自己資料；檔名是建議目的地，不是現存證據。

| 資料 | 內容與核對目的 |
| --- | --- |
| `qualification.md` | case ID、實際 root／state／endpoint／chat／thread、Desktop build、候選 manifest／runtime 來源、effective source／writable root 核對、模型 UI 資格；缺值與原因 |
| `timeline.md` | 開始／點擊／終態／程序查核／觀測截止的時間與時區；保留原 UTC；區分人工註記、截圖 metadata、原生事件來源，列相互關聯依據 |
| 實際畫面／錄影 | 正確 chat／root 識別、Stop 前後；模型案初始 A、選單、B 與新回合；裁去無關私人內容，保留必要識別及時間，不編造 click event |
| 宿主原始紀錄 | 只擷取本案相關 thread／turn／item／worker 範圍，保留來源、原始順序與行號、SHA-256；工具開始／終態、worker start／completion、dispatch 參數、root 與 worker context。不可取得就明列 null，不製作合成 raw |
| 程序查核 | Stop 前後及最終的自有 PID／PPID／開始時間／精確命令／token／退出觀測，或 worker 原生 running／terminal；不歸檔全機程序清單或 auth |
| `before/`、`after-stop/`、`final/` | 本案合約與 canary 檔案、bytes／hash／mode、T2 存在性與唯一合約／啟動次數；沒有 resume 就沒有 final，不為補包派工 |
| `verdict.md` | 每案 expected → observed → raw path／行號 → 通過／失敗／部分／受阻／未命中；分開 UI、native、程序、保留與資格限制，標明實際觀測區間 |

後續審閱者先核對 case 身分與時序，再評估各門檻；畫面與口述均不能單獨證明宿主行為。原有 API Stop／M2 僅供設計參考，不貼成新 Desktop 的原始紀錄。直到兩案必要證據成立，G07 維持 blocked；人工包完成不替代試驗。
