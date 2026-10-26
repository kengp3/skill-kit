# G07：本機 Desktop 人工驗收環境規劃

**2026-10-26 範圍修訂（使用者已核准）：** 本方案改列選配、未執行，不是產品交付前置。以下帳號與環境方案保留作歷史規劃；本輪不建立帳號、VM 或繼續 UI 驗收。 依據：[最新規格 S1](../specs/harness-validation-gap-closure.spec.md#s1-唯一驗收邊界與狀態)。

日期：2026-10-26（Asia/Taipei）。**規劃已完成，環境未建立，UI 試驗未執行；G07 仍受阻。** 使用者已表示願意人工配合，並將環境選擇交由主責規劃。本文是待執行方案，不把新增 macOS 帳號視為 agent 已獲准的系統操作。

## Objective

在這台 Mac 的專用標準使用者帳號內，先完成實際 Desktop Stop，再完成模型選單驗收。沿用[原人工操作包](../research/harness-gap-closure-desktop-evidence/manual-runbook.md)及[補驗規格 S9](../specs/harness-validation-gap-closure.spec.md)，保留 UI、同 chat 原生紀錄、程序及產物證據；不降低任何通過門檻。

## Background 與已確認事實

- 本機唯讀查得 macOS `27.0.1`、build `26A434`。
- 已安裝 App 為 `/Applications/ChatGPT.app`，bundle ID `com.openai.codex`，版本 `26.1021.31345`、build `21828`。讀取的是套件 metadata，沒有操作 App。原先假設的 `/Applications/Codex.app` 不存在，不能沿用該路徑。
- 該 bundle 仍受[已保存的電腦操作工具拒絕](../research/harness-gap-closure-baseline-evidence/desktop-getapp.raw.jsonl)限制；UI 由使用者操作，不用其他 App 名稱、shell GUI 操作或私有介面繞過。
- 候選已重新查核為 manifest `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。來源為 `dist/candidates/kengp3-harness-0.3.0`；demo-002 HEAD 仍 `fdc13d69334235c9edd3e61a69710c5d7a5fab78`，原 dirty 內容保留。

## Materials 與環境選擇

建議採用**兩個本機標準帳號，分階段建立**。Apple 說明不同使用者可維持自己的設定；標準使用者可改自己的設定，不能管理其他使用者。建立帳號需由管理者操作。[Apple：加入使用者](https://support.apple.com/zh-tw/guide/mac-help/mchl3e281fc9/mac)

| 用途 | 建議帳號 | 建議專案根目錄 | 預期 Codex state 候選 |
| --- | --- | --- | --- |
| 第一階段：Stop | `g07stop` | `/Users/g07stop/Workspaces/harness-g07-stop` | `/Users/g07stop/.codex` |
| 第二階段：模型選單 | `g07model` | `/Users/g07model/Workspaces/harness-g07-model` | `/Users/g07model/.codex` |

以上名稱與路徑都是**規劃值，不是已存在環境**。本輪 directory service 唯讀查詢未成功（exit 70），未證明名稱可用；人工建立時若同名已存在，不接管、不覆寫，改用未占用名稱並重新確認所有路徑。

兩個帳號讓兩案各有新 HOME 與本機 App 偏好，保留 Stop 原 state 亦不需清空重用。代價是兩次帳號／登入準備；第二個帳號只在第一階段資格與 Stop 證據成立後才準備。

`CODEX_HOME` 官方文件列出的適用面包含 CLI、IDE、app-server、installers；不能僅在 shell 設這個變數，就宣稱 Desktop 已隔離。需實際核對 `.codex` 及 Desktop App 資料、原生紀錄與 daemon 的使用者／來源。[OpenAI：環境變數](https://learn.chatgpt.com/docs/config-file/environment-variables)

## Boundaries

- 這輪只交付規劃與文件。不建立／刪除帳號、不改管理政策、日常 auth/config、全域安裝或系統網路，不開試驗 chat 或模型回合。Windows 維持排除。
- 使用已安裝 App；新帳號由使用者正常登入。候選只複製四個 skills 的完整非 scripts 資源，以及 demo 當前 AGENTS／project-setting／專案設定；不複製日常 auth、個人 App 資料或 G03 trust state。
- 新 OS 帳號只提供本機使用者隔離；雲端帳號設定、managed／system 來源仍可能共用。不要改帳號級預設；若模型選單操作不能限定於驗收環境，模型案先保持受阻，另議獨立測試帳號，不自行新增付費服務。
- macOS 與 ChatGPT 登入、帳號建立、UI Stop／模型選擇由使用者操作。驗收模型維護合約；獨立觀測者只讀指定 case、原生紀錄與自有程序，不能代改合約、gate、canary 或信任設定。
- 不把原對話的 agent 當作已能讀新 OS 帳號的私有檔案。需在測試帳號安排獨立唯讀觀測者／驗收對話；觀測與來源讀取資格不足時，不開始故障窗口。

## 建議流程

### 1. 先準備 Stop 帳號

由使用者在「系統設定 → 使用者與群組 → 加入使用者」選擇**標準**，建議短名稱 `g07stop`。若無管理者權限，交由該 Mac 管理者處理；agent 不代輸入密碼或操作系統 UI。先不建立 `g07model`。

登入新帳號後，手動開啟 `/Applications/ChatGPT.app`，進入 Codex 的 **This computer／Local** 工作方式。帳號權限及實際選項以當下 UI 為準。[OpenAI：Codex environments](https://learn.chatgpt.com/docs/environments/modes)

### 2. 完成來源與觀測資格

採用後由主責準備可攜輸入包：固定候選的四個 skills／21 個非 scripts 檔、demo 當前指示／設定快照及 manifest；不含認證或 native 私有歷史。使用者複製到新帳號的建議專案根目錄，再逐檔讀回；不能用 Git checkout 冒充包含 demo 未提交接入。

**材料準備進度（2026-10-26）：** [兩份 ZIP／已填案例 prompt／唯讀觀測 prompt 與操作者入口](../research/harness-gap-closure-desktop-evidence/manual-kit-20261026-4a9d7f20/operator.md)已備，[manifest](../research/harness-gap-closure-desktop-evidence/manual-kit-20261026-4a9d7f20/manifest.json)及[離線核對／負控](../research/harness-gap-closure-desktop-evidence/manual-kit-20261026-4a9d7f20/preparation-check.json)可審閱。這是可攜輸入完成，不是環境完成：OS 帳號未建、名稱可用性未證，建議 root/state 仍 proposed，實際 UID/thread/session/state 未觀測；UI 未跑，G07 維持 blocked。

在任何 canary 或 worker 開始前，保存一頁實測 qualification：實際 username／UID、HOME、App build、project／writable roots、有效指示與 skills/hooks/plugins 來源、實際 state／原生紀錄位置、chat/thread ID 與可見標題。先確認能讀這個 Desktop chat 的原生工具開始／終態及 model context。正常專案信任與 hook 信任分開；G07 不補授信或 bypass，五個 hook 的實際初態照實記錄。

若新帳號仍連到日常 state／daemon、沒有原生紀錄讀取方式或普通工具無法執行，到此停止，保留缺項。不得另開 app-server 代測 Desktop。

### 3. 執行 Stop，再明確續作

使用者在新帳號自行建立試驗 chat，另安排獨立唯讀觀測者。依原操作包準備 preserve／ledger 基準、唯一 case ID／token 與已填實際路徑的 start prompt。

驗收模型先保存唯一合約，再啟動有界前景命令。觀測者確認同 chat 真正 item/started 與自有 PID／token 仍在執行後，由使用者點 Stop 一次並保存前後畫面。停止後不向試驗 chat 送訊息；由觀測者核對原生終態、程序與既有 bytes、T2 未建立及沒有後續工作。命令先結束則記未命中，不自動重跑。

只有使用者另外送出原操作包的 resume prompt，且原程序／副作用已查明，才續作 T2；不重播 canary 或 ledger。通過後保留完整 state／原身分與證據，再進第二階段。

### 4. 新帳號執行模型選單案

以相同步驟準備第二個標準帳號 `g07model`，使用其獨立 project/state/chat。資格成立後，由 UI 實際可用項目選出不同 A／B；不預綁歷史模型名稱，也不購買或改帳號權限換取資格。

依原操作包先真派 old_worker，保存原 handle／context A 後結束主責回合；觀測到它仍 active，使用者再於同一試驗 chat 選 B。選擇後另送明確 continue prompt，核對原 handle、放 gate 並只派一個 new_worker。以原生 context／dispatch 參數證明新繼承 B、舊 worker 身分及設定保持；UI 標籤本身不是實際模型證據。

### 5. 回傳證據與收尾

每案保存 qualification、時間線、實際 UI 畫面、同 chat 原生事件／context、自有 PID 查核、合約／canary 前後 bytes 及 verdict。完整私有原件保留在測試帳號內；公開節錄需有原 hash、行號、省略索引及來源核對者，不含 auth 或帳號身分值。

可用 `/Users/Shared/harness-g07-transfer/` 人工交接**輸入包及已去除敏感內容的證據包**。Apple 說明 Shared 檔案可由其他本機使用者讀取，因此不把 auth 或完整私有 session 放入該目錄。[Apple：本機使用者共享檔案](https://support.apple.com/zh-tw/guide/mac-help/mchlp1122/mac)

若本對話無法直接讀完整來源，報告要區分測試帳號觀測者的原件核對與本對話可獨立複讀的節錄，不冒稱跨帳號存取已成立。必要證據不足時保持部分／受阻。確認所有試驗工具、worker 及程序終態、證據已讀回後才清理測試認證；刪除 OS 帳號另行決定，不能連帶刪掉待覆核 state。

## Definition of Done

**本次規劃交付：** 有推薦環境、具體預定路徑、人工與 agent 分工、資格閘門、兩案順序、交接與收尾方法；讀回及來源連結通過。沒有把環境或試驗寫成已完成。

**G07 實際完成：** 原操作包所有必要 UI／原生／程序／產物門檻有直接證據，經獨立審查並回寫唯一[中央驗收表](../research/unified-project-settings-acceptance.research.md)。本規劃不關閉 G05／G06，也不等於 G07 通過。
