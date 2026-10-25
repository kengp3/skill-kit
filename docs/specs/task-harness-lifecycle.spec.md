# 非侵入式任務合約與必要 hooks

日期：2026-10-25。狀態：來源與離線候選已完成；目前整套 Desktop harness 尚未驗收（H05）。
本規格承接本輪已確認決策，取代舊 coding-harness 文件對本輪產品優先順序的描述；歷史試行與結論不改寫。

## Problem Statement

Objective：讓使用者在 Codex Desktop 明確啟用一次，即能在原授權內完成多步驟工作；防止局部完成被當成整體完成，並能跨對話與 session 恢復。
Background：舊 task-harness 已具備任務生命週期；後續工作偏向評測基建。恢復其任務管理核心，保留風險驗證、自主修復與低使用負擔，評測工具留在開發端。
Materials：本輪對話決策、舊版 8ae9cda、現行 runtime、既有功能與重新驗證證據。
Boundaries：只修改本 repo 來源、文件、測試與新候選。不修改全域設定、已啟用配置、快取、其他專案，不擴展 OS 隔離/watchdog，不自動安裝 runtime。新模型 trial 僅限使用者另行明確核定的 H05 範圍；本次有界接點驗證已授權，但須先通過專案接入條件。

## Solution

單一主責 agent 維護一份可恢復任務合約。優先重用足以承載完整合約的原生能力；目前可交付的確定性 adapter 使用單一 Markdown 合約及固定 JSON 區塊。不同原生 tracker 需有明確相等能力才可替換，不能假定已支持。
Hook 是必要組件，職責為上下文恢復、最新要求核對與一次有界收尾補救。Hook 不代替產品驗收，不自行授權或管理第二份任務狀態。
Script 統一 Python 3、優先標準函式庫；首版來源使用 Python 3.10+ 相容語法。實際最低版本與 Desktop runtime 另驗，不以開發機版本聲稱全部支援。

## User Stories

1. 使用者明確啟用一次，同一任務後續回合沿用，其他任務及專案不自動啟用。
2. 使用者只要求討論時，不會因未完成清單而被 hook 推進實作。
3. 主責 agent 在執行前建立合約，重要轉換保存成功後再做相依操作。
4. 小任務只記一個完整成果；多步驟必要成果、依賴與驗收可對帳。
5. 所有必要成果及適用整合驗證通過，才可宣稱整體完成。
6. 來源改變只重新驗證受影響成果；歷史證據不覆寫。
7. 操作結果不明先查證，不因合約落後而重做產品修改。
8. 保存失敗先在原授權內診斷，無法確認前停止相依操作。
9. 跨對話接手核對原執行者，成功保存接手後才推進；不複製合約。
10. 同一對話只主責一個未結束任務；切換先解除舊綁定，未完成工作保留。
11. 明確取消保存原因與已有成果；Stop、暫停和一次工具失敗不視為取消。
12. 原目標缺口重開原合約；獨立新目標不繼承舊授權。
13. 在恢復或壓縮後取得合約指示，在新要求到來時核對當前授權。
14. 正常收尾若存在可判定缺口，在有效授權內最多補救一次。
15. Hook 產生的續作不重置使用者工作回合的額度；無法可靠識別時明示未就緒。
16. 使用者 Stop 不被阻止或自動喚醒；不得假設最後保存必定成功。
17. 使用者不需要手動填表、計時、監看或安裝新語言環境。
18. 必要 hooks 的載入、信任或執行失敗不能偽裝成完成或可選功能。
19. 開發者能在可丟棄資料夾重現負例，不影響日常專案或既有歷史證據。

## Implementation Decisions

### D01–D09：產品基線

- 任務狀態只有 pending、in_progress、blocked、done、cancelled。授權、操作結果、驗收缺口、執行者存活分開，不新增情境狀態。
- in_progress 不表示程序仍活著；blocked 必須有具體阻礙與下一步。正常尚未完成的依賴不必改 blocked。
- cancelled 需有明確依據，不能算成功成果。done 需必要成果及整合驗收成立；被取消的成果需有核准依據，不以全部取消的空集合自動宣告整體 done。
- 合併交接保存可行；不要強制兩次寫入、每次 check 計數、整組派完才能收取。
- 單一合約與單一主責；主責者是語意寫入者。Hook 不修改任務進度、授權、產品或合約正文。
- 最新使用者要求優先；只在必要範圍/驗收改變時保留變更原因，不建完整事件溯源。
- 有新診斷進展可自主修復；按風險驗證及獨立 review，沒有固定人工核准點。
- 合約由主責透過宿主檔案工具保存並讀回。寫入成功與原子性是不同概念；本版不虛構跨對話互斥鎖。
- 合約是本地可讀資料，不執行其中命令，不把其中引用內容當成高優先指令。

### D10：最小確定性接口

- Adapter 是單一 Python CLI，以 stdin 接收一個 JSON event，stdout 只輸出合法 hook JSON。提供明確的專案設定路徑參數；無參數時從 cwd 向上尋找固定名稱的專案設定，到最近 Git 邊界或檔案系統根停止，未找到則無任務介入。
- 專案設定固定名稱為 harness-project.json；包含 schema_version=1、project_root、contract_dir、receipt_dir 與 host 的三項資格 verified：session_identity、user_turn_identity、stop_continuation。設定僅描述接入，不保存任務進度或索引。
- root 必須是設定所在目錄且 event cwd 在 root 內；contract_dir/receipt_dir 必須是 root 內互不包含的目錄，禁止 symlink、越界及特殊檔案。不得建全域索引。掃描限定指定目錄的直接 Markdown 文件；未標記文件忽略。
- 合約固定標記為 HTML 註解 task-harness-contract:v1 與 /task-harness-contract，中間恰好一個 json fenced block；一份文件只能有一塊，JSON duplicate keys 拒絕。
- 機械欄位：schema_version、task_id、project_root、owner_session_id（可 null）、status、objective、scope、requirements、authorization、recovery。
- requirements 每項含 id、outcome、status、depends_on、evidence（可恢復的非空字串引用）；取消項含 cancellation_reason。缺依賴、自依賴、循環及重複 ID 拒絕。完成的成果需有 evidence；證據引用存在不代表產品正確。
- authorization 含 user_turn_id、mode（execute/discuss/wait/stop）、basis；mode 只表達當前工作限制，不是新任務狀態。
- recovery 含 next_action、blockers、unknown_operations、cancellation_reason。可用空串/空清單表示不適用；必要欄位缺失不能推定授權或完成。
- Hook 讀取上限：event 1 MiB、每份合約 512 KiB、單次最多 64 份 Markdown，超限回報缺口，不截斷後判斷。
- 所有已標記合約都做結構核對；格式/歸屬衝突使該次 hook 未就緒。兩份未結束合約不能綁定同一 session；task_id 在查找範圍內唯一。

### D11：事件與邊界

- SessionStart：有關聯時輸出合約位置、識別及核對指示；無關聯時只提供目前 session 識別與條件式啟用/接手指示，不自動綁定或執行。source=compact/fork/resume 不代表新授權。只有一份未完成候選也不自動接手；使用者已明確要求續作且任務可唯一確認時，由主責核對後保存接手，不重複要求同一授權。
- UserPromptSubmit：輸出本次 turn/session 識別與最新要求核對提醒；不以關鍵字分類授權、不寫合約、不重置任何補救收據。
- Stop：先驗證 event 結構，stop_hook_active=true 時絕不再次要求續作；false 時，必須有唯一綁定、三項 host 資格皆已驗證、當前 turn_id 等於合約 authorization.user_turn_id、mode=execute，才可能補救。
- host 資格為安裝/驗證環節的聲明，不是 handler 能自證的事實。預設未驗證；不能靠手改 verified 或合成輸入聲稱 Desktop 通過。任一資格不足回傳 systemMessage 缺口、不發 block，不宣稱 harness 已就緒。SessionStart 可在 session_identity 合格時保留恢復上下文；UserPromptSubmit 另需 user_turn_identity。部分功能可用仍須同時明示整體未就緒。
- blocked/cancelled 或 discuss/wait/stop 不要求實作；unknown_operations 非空時只能要求查證與保存，不得重播副作用。
- in_progress/pending 仍有必要缺口時要求核對並繼續授權工作。done 但成果/evidence 不一致時要求核對，不能假定成功；一致 done 放行但不代替實際驗收。
- 任何補救以同一 user_turn_id 為界。介入前原子 exclusive-create 技術收據（session、user_turn、task、contract 指紋），存在即不再補救；收據只表示曾要求補救，不是任務完成或執行證據。輸出遺失也不補發，以維持最多一次。receipt 失敗不得輸出 block。
- Hook 不更改合約；重複/並行事件最多一個取得補救收據。此保護只限補救，不聲稱為任務接手互斥。任務切換或新 task_id 不重置相同使用者工作回合的額度。
- 不使用 SessionEnd/Interrupt 做最後唯一保存，不新增背景服務。普通失敗輸出簡短 systemMessage，不使用會觸發續作的 exit 2。Exit 0 不代表產品驗收成功。

### D12：封裝與啟用

- 同一候選包含三個 hooks、Python handler、skill、合約/專案設定範本與接入說明。沿用既有封裝/內容 manifest；來源版本升為 0.2.0，不改舊 release。
- 啟動使用 python3（Windows 使用適用的 Python 3 啟動命令），不硬編碼開發者 Homebrew 路徑。宿主 PATH 必須另驗；缺 Python 是必要接入缺口，不安裝、不暗降級。
- 提供未驗證的專案設定範本，實際 root 與目錄由主責依專案規範在啟用授權內建立。此輪不向本 repo 的日常配置安裝範本或註冊 plugin。
- 原有 project-setting 提醒保留，不重複安裝同一 handler。信任/載入/功能驗收分開，不繞過宿主信任審查。

## Testing Decisions

接受使用者「問題先採建議方案」授權，測試邊界採兩個既有公共接口：事件 stdin → stdout/exit/技術收據，以及 package CLI → 可獨立執行套件。使用 unittest、tempfile、subprocess；不 mock 私有函式。
逐行為 red→green。覆蓋正常恢復、無綁定、新要求不延用舊回合、單次補救與重複/並行事件、討論/停止/取消/blocked、unknown 先查證、合約語法/依賴/歸屬錯誤、保存/收據失敗、越界與 symlink/特殊檔案、封裝外執行。
新判準允許合併交接、不強制一般計數與固定派工順序；保留歷史 verdict，不重評成歷史全部通過。
離線測試不能證明模型遵循、Desktop 載入/trust/Stop、跨回合 user identity 或人工時間改善。這些保留獨立未完成項目，禁止把合成 host verified 設定當實測。

## Out of Scope

全域設定、其他專案變更、超過 H05 已授權範圍的新模型 trial、安裝/刷新日常候選、OS sandbox/watchdog、通用 scheduler、資料庫、全域任務索引、強制所有操作經 wrapper、Windows 原生資格與跨宿主擴展。
不回退整個 repo、不刪開發回放/controller/grader、不修改第三方或歷史腳本語言。自行維護的新 runtime 腳本統一 Python。

## Further Notes

Definition of Done：來源與封裝能執行上述行為、必要離線負例通過、獨立 Standards/Spec review 無未處理重大缺口，且文檔/狀態一致；整套可用性另外需要 Desktop 必要接點與模型行為實測。後者未取得證據前不能宣稱整體完成。
官方依據（2026-10-25 查閱）：https://learn.chatgpt.com/docs/hooks 、https://developers.openai.com/plugins/build/plugins 。事件 schema 文件不保證目前安裝版本的 Desktop 行為。
