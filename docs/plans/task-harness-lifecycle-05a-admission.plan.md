# H05A：原生接入與有界補救

**What to build:** 在可丟棄專案，以既有 Codex 原生執行能力載入指定 skill／hook 候選，取得真實三事件與一次補救的直接證據；不依賴圖形介面，也不影響日常環境。

**Blocked by:** H04（已完成）。

**Status:** in_progress（依最新目標進行實作／離線驗證；實際模型案例尚未執行）。

規格：[任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)。案例、限制與共同證據格式：[H05](task-harness-lifecycle-05-desktop.plan.md)。

- [ ] 唯讀確認原生版本、公開協定、Python 與正常接入／信任；分清已有實作、歷史經驗及仍需實測項目。
- [ ] 重用既有封裝／事件／控制接口，只補具體缺少的開發端接線；不將純控制狀態或離線 boundary 當模型 runner。
- [x] 同步來源接入指南中與新規格衝突的 Desktop 專屬表述；已建立 0.2.1 候選，保留凍結 0.2.0，沒有安裝或刷新日常快取。
- [x] 完整候選在測試專用 state 正常載入／信任，未 bypass 或複製私人憑證；停用及移除讀回完成。日常 config 雜湊一致，證據不擴張為所有全域檔案監測。
- [x] 已新增開發端 probe，並完成整合後 43 項必要離線回歸；不把離線綠燈當真實資格。
- [ ] 明確允許模型執行後完成 C0；探針與產品 handler 結果分開，原 user-turn 與續作鏈可追溯，最多一次補救及重入不補發有直接證據。
- [ ] 實際取消／結果讀回與自有 writer 收尾可用；控制端逾時會停相依試行，不要求人工監看。
- [ ] 保存版本、候選、實際載入來源與 C0 判定；不藉此宣稱其他行為案例已通過。

完成條件：C0 真實事件與產品正向補救證據，以及必要控制均成立。唯讀盤點或接線完成只能算進度；模型仍禁止時本票保留未完成。後續實作沿用 integration branch 與 TDD／獨立兩軸 review，不開新的通用執行框架。

## 唯讀協定盤點（2026-10-25）

已執行版本／help 查詢，並用已安裝 CLI 的 `app-server generate-json-schema --experimental` 匯出到可丟棄目錄後檢查，隨後移除該目錄；沒有啟動 server、thread 或模型。這是工具 schema 匯出，不是 trial，也沒有產生專案程式。

| 項目 | 直接觀察 | 對下一步的影響 |
| --- | --- | --- |
| 已安裝 CLI | `codex-cli 0.164.0`；目前 PATH 指向本機 nvm 下的 Codex launcher | 建議首輪固定此版本；實作時還須保存實際 executable／候選指紋與模型設定 |
| 歷史使用的內附 CLI | `codex-cli 0.164.0-alpha.11.1` | 與已安裝版本不同，舊 smoke 不等於新版 hook 資格；不因曾用內附版本而綁定它 |
| 原生入口 | app-server 支持 stdio；CLI 另有 shared daemon／remote 入口 | 後續沿用可歸屬本次測試的原生 stdio 路徑，不接上日常共享 daemon；本輪沒有啟動任何一路 |
| hook 可觀測性 | schema 有 `hooks/list`，及 `HookStartedNotification`／`HookCompletedNotification`；通知帶 threadId、可空的 turnId、run | 可作載入／執行證據來源；通知存在不代表事件一定送達，也不能把可空 turnId 當可靠回合識別 |
| 回合與中斷 | `TurnInterruptParams` 要求 threadId／turnId；`ThreadReadParams` 有 includeTurns，並提示 paginated history 優先用 turns／items list | 重用控制歸屬與讀回判斷；歷史腳本的讀回形狀要按所選版本核對，不先修改 TrialControl 假定相容 |
| 回合來源欄位 | `TurnStartParams` 有 parentTurnId、rootTurnId、turnTrigger，均由 caller 提供或選填 | 可輔助記錄，不能當成宿主自證的使用者／hook 識別，更不能由測試端填值後宣稱資格成立 |
| 接入設定 | `ThreadStartParams` 支持 config、cwd、runtimeWorkspaceRoots；config 寫入 API 可指定 filePath，但省略時預設使用者 config | 支持參數存在不保證所有設定可被覆寫；禁止用一般寫入 API 手填 trust hash，或省略路徑造成全域寫入 |
| hook 信任接口 | 生成的 ClientRequest schema 中，hook 專用 method 只有 `hooks/list` | 尚未查得專用 trust 寫入 API；正常審查／信任在測試範圍內如何完成仍是接入缺口，不能拿 config 寫入或 bypass 冒充 |

匯出含 458 個 schema 文件；檢查的是現有 binary 公開介面，不聲稱實作行為已通過。`--help`／schema 工具回報建立 PATH aliases 被 sandbox 拒絕；沒有升權或重試建立。schema 匯出前後使用者 config 的 SHA-256 相同；未檢查所有全域檔案，不把這個單檔比對說成完整環境隔離證明。

剩餘工作限三項：正常測試接入／信任、所選版本的原生控制與讀回適配、C0 真實事件／產品補救。後續依已更新目標實作前兩項的最小接線與離線回歸；C0 另需符合模型 trial 的明確授權。此盤點本身不構成行為通過，也不將本票標 done。

## 實作與接入進度（2026-10-25）

- 來源／封裝切片 `606c484`、開發端 C0 probe 切片 `96ec169` 已整合；整合來源 `c84303c`。主責重新執行 package、產品 hook 與 probe 公共 CLI 共 43 項，全部通過（4.935 秒）。這些仍是離線測試，不替代 C0。
- 0.2.1 已在本 repo 的候選目錄建包並驗包；22 個內容檔，manifest SHA-256 `210664eb7b5a478997dbc8c67b323131a5f9ed62bd51e23cdbaba8bdb7a8ae5a`。來源與凍結候選分開，沒有改 0.2.0 或日常啟用版本。
- Probe 只在開發端，以明確測試根／證據目錄接收白名單事件，整個 attempt 最多一次無害 canary；並行／跨 turn／保存失敗不會重新補發。尚未建立新的通用 runner；原生接線及實際資格仍未完成。
- 無模型 admission 使用單獨測試設定根目錄與正常 CLI。第一次因終端輸入不是 TTY 而退出；修正終端接線後進入原生登入選單，確認未登入時尚不能審查 hooks，隨即正常退出。沒有送模型 prompt、繞過信任或讀取日常憑證。
- 使用者已明確允許該測試目錄的 ChatGPT device login，且明示不啟動模型 trial。登入程序已原生回報成功並 exit 0；沒有使用畫面或使用者回報替代完成證據。一次性代碼與 auth 檔案不封存進 repo。
- admission 前後的日常使用者 config 雜湊一致；只代表該設定檔保留，不能稱全域所有檔案已全面監測。最小接入與源碼依據見[唯讀調查](../research/h05-admission-inventory.research.md)，離線切片證據見[封裝](../research/h05-package-validation.research.md)與[探針](../research/h05-hook-probe-validation.research.md)。

## 原生接入讀回與審查結果（2026-10-25）

- 測試目錄的正常 `/hooks` 審查已完成，獨立 stdio app-server 的 `hooks/list` 讀回三個 project hooks 均 enabled／trusted，且 hash 與測試 config 一致、無 warnings／errors；TUI 與自有 app-server 均已退出。見[無模型接入證據](../research/h05-native-admission.research.md)。
- 此次驗的是與 0.2.1 bytes 相同的 handler 複本接入；不代表 plugin／skill 載入或 C0 真實事件已通過。後續精確候選／probe 定義仍須正常審查；所以完整接入 checkbox 與 C0 保留未完成。
- `27ead1b...1a08939` 的獨立 Standards 審查無發現；Spec 審查找到 H05 歷史段落仍稱「本輪只修文件」的 P2 矛盾，已由單一實作者以 `bd70dce` 修正並整合至 `0cc19b4`；獨立 Spec 複核確認問題解決，接入報告與原始讀回資料一致。沒有發現 probe 程式缺陷，兩位 reviewer 均獨立重跑 9 項 probe 測試通過。
- 本次沒有模型 prompt 或 turn/start，沒有新模型 trial；新的模型執行仍待明確核定範圍。

使用者於本輪明確選擇「先停在無模型驗證成果」。本階段到此停止，不啟動 C0 或其他模型 trial；H05A 必要成果尚未全數驗收，維持 in_progress，後續須等待明確續作及模型執行授權。測試登入資料保留在可丟棄 state 內，不封存至 repo。


## 完整候選接入完成（2026-10-25）

使用者回覆持續迭代後，已完成四項清單的第 1 項：完整 0.2.1 候選經原生安裝、四個 skills 載入、三個 hooks 正常信任、停用與原生移除讀回。安裝快取內容符合凍結 manifest；日常 config 前後雜湊一致。詳見[完整接入證據](../research/h05-native-admission.research.md#完整-021-候選接入與停用2026-10-25)。

這是測試專用 CODEX_HOME 的 user-scope plugin，不宣稱宿主提供 project-only 安裝。產品 opt-in 與任務級啟用維持原規則。測試 plugin 最終已移除，早期 project hook 複本保留為停用備份。沒有模型 trial，C0、原生取消及產品補救等未完成項維持不變；本票仍 in_progress。

獨立 Spec 複核確認四階段原始 RPC 與封存 JSON 一致、scope 界線正確、沒有誤宣稱 C0 完成；無新增 findings。
