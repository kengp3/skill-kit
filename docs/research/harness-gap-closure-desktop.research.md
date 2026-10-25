# G07：Desktop 停止與模型選單資格及人工操作包

日期：2026-10-26（Asia/Taipei）。**G07／V05 維持受阻；兩個 UI 情境均未執行。** 本次交付可審閱操作包，沒有取得 Desktop 畫面、點擊、專用 state 或模型選單資格，不以文件就緒關閉 ticket。中央細分狀態由整合主責維護，本文只記本案證據與 readiness。

## 已知資格與界線

| 預期 | 實際觀測 | 原始依據 | 判定 |
| --- | --- | --- | --- |
| 有可用 Desktop UI 控制入口 | G00 的 `cua.getApp('com.openai.codex')` 被拒；本案未重試 | [原始 call／result 兩筆](harness-gap-closure-baseline-evidence/desktop-getapp.raw.jsonl:1)、[來源行號／call_id／SHA-256](harness-gap-closure-baseline-evidence/desktop-qualification-note.json:1) | 工具 app allowlist 阻擋 |
| demo 正常接入可作候選來源 | G01 已完成 0.3.0 接入、唯一合約／成果與 clean readback；五個 hooks 仍 untrusted | [G01 報告](harness-gap-closure-demo-setup.research.md:1)、[clean readback](harness-gap-closure-demo-setup-evidence/clean-readback/summary.json:1)、[hooks 原文](harness-gap-closure-demo-setup-evidence/hooks-final.json:1) | G01 通過，不等於 Desktop 或持久信任通過 |
| 專用 Desktop workspace／state、同 chat 原生紀錄可核對 | 本案尚未取得 | [操作包資格閘門](harness-gap-closure-desktop-evidence/manual-runbook.md:7)列待核對項，沒有預填宿主觀測 | 受阻 |
| Desktop 真點擊 Stop 命中已開始工具 | 本案未操作；歷史 API Stop 有 interrupted 與程序查核 | [原 Stop 報告](unified-project-settings-native-stop.research.md:1)、[RPC](unified-project-settings-native-stop-evidence/original-rpc.jsonl:157) | API 參考；UI 未執行 |
| Desktop 模型選單改變後新派工繼承、舊 worker 不重啟 | 本案未操作；歷史 M2 是 API `turn/start` 控制 | [M2 報告](unified-project-settings-model-lifecycle.research.md:30)、[RPC](unified-project-settings-model-lifecycle-evidence/switch/rpc.jsonl:391)、[host contexts](unified-project-settings-model-lifecycle-evidence/switch/session-contexts.json:1) | API 參考；UI 未執行 |

拒絕原文為 `Computer Use is not allowed to use the app 'com.openai.codex' for safety reasons.` 原始呼叫時間 `2026-10-25T15:41:12.116Z`、回覆時間 `2026-10-25T15:41:13.665Z`，保留 UTC，不改寫為本次重試。來源 call_id 為 `call_77a3a7e661154de8b0c622699073a389`。本案只核對已歸檔兩筆及 note，沒有蒐集完整私人 session、其他 app 或 tab。

此為工具明確 app 存取限制；保持原拒絕，不以 app 別名、AppleScript／osascript／JXA、shell UI 控制或其他替代通路繞過。一般 API 成功不改變這個資格。人類日後自行操作是候選補驗安排，並非本次已發出的操作要求，也不授權 agent 建新 chat。

## 操作包與完成界線

- [manual-runbook.md](harness-gap-closure-desktop-evidence/manual-runbook.md)：資格閘門、Stop／模型兩案順序、點擊窗口、程序查核、回傳資料與判定。
- [stop-start.prompt.txt](harness-gap-closure-desktop-evidence/stop-start.prompt.txt)／[stop-resume.prompt.txt](harness-gap-closure-desktop-evidence/stop-resume.prompt.txt)：只供日後使用者審閱並自行送出；resume 範本存在不算新授權。
- [model-start.prompt.txt](harness-gap-closure-desktop-evidence/model-start.prompt.txt)／[model-continue.prompt.txt](harness-gap-closure-desktop-evidence/model-continue.prompt.txt)：既有 M2 的 old／new worker 設計，切換動作必須由真 UI 完成。
- [source-readback.json](harness-gap-closure-desktop-evidence/source-readback.json)：本次文件與引用來源的唯讀核對，不是 UI trial raw 或產品測試結果。

補驗須同時具有正確 case root／chat／state、真實 UI 操作佐證、同一 Desktop chat 的原生 thread／turn／worker context 及程序／成果讀回。畫面單獨、人類口述單獨、模型自述或其他 app-server 的 API 結果都不足。無法取得欄位維持 `null` 並記原因；模型不可見的 observed model／effort 不由人手補寫至合約。

Stop 後不派工、不補寫、不自動恢復，也不為製作證據再送模型 prompt。事前安排的獨立唯讀觀測只保存該 case 既有紀錄與程序狀態。須查明原程序、worker 與副作用後，再由使用者明確 resume，才可接續同一合約。原 API 案已證明 shell 可能在 turn interrupted 後短暫存活，不能宣稱 UI Stop 即時殺掉任意子程序或回滾。

本次只讀 demo 的現行 AGENTS／project-setting 以定位來源與確認文件規則；未操作 demo 業務程式、Java／Maven、日常設定、全域安裝、信任資料或認證。G03 人工精確 hook trust 與 G07 是不同分支；hooks untrusted 不等於 Desktop 功能失敗，亦不能為 G07 順手授信。Windows 已明確排除。

## 本次驗證與仍缺條件

已讀 [補驗規格](../specs/harness-validation-gap-closure.spec.md)、[計畫](../plans/harness-validation-gap-closure.plan.md)、[G07 ticket](../plans/harness-gap-closure-07-desktop.plan.md)及[可行性 V05](unified-project-settings-gap-fixtures-feasibility.research.md:104)。依 project-setting 將研究與附件放在本專案 `docs/research/`，核對目的地非 symlink、讀回新文件、檢查本次引用路徑及來源行號、原始拒絕兩筆 hash 與內容。沒有新增程式邏輯，因此沒有鏡像測試或重跑整套維護測試。

最小解鎖條件是：使用者選定並正常操作可隔離日常 state 的 Desktop 驗收環境，且該環境能以受支持唯讀方式取得同 chat 的必要原生紀錄；模型案還須當下 UI 確有第二個可用選擇。不能隔離時停止，不要求改全域來完成。本案沒有假定以上已成立，也未現在請求使用者操作或上傳。
