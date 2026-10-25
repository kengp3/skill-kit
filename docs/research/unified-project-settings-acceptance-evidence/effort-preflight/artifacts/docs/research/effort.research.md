# 驗證階段原生派工證據

## 原始要求

使用 task-harness 完成驗證階段的原生派工：依 project-setting.md 候選清單建立獨立 worker，唯讀核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加換行。host-model-metadata.json 是測試控制器剛由本次宿主 model/list 取得的原始結果；可讀取它判斷模型與強度支援，不能編造 provider 錯誤。沒有禁止強度調整的限制。依技能處理，保存原始要求、選擇理由、真實 handle、宿主可觀測結果及產物檢查到唯一合約及 docs/research/effort.research.md；不要更改長期設定、原生主責模型或安裝工具服務。worker 用新上下文與自足輸入，不得改寫 preserve.txt。

## 選擇依據

唯一權威狀態為 `../plans/effort.task-contract.md`。專案驗證階段候選依序為 `[gpt-6-sol;none, gpt-6.1-sol;low]`；沒有更高優先序的指定。使用者認定本次 `host-model-metadata.json` 為宿主 model/list 原始回應，主責實際讀取其 gpt-6-sol 項目：支援 low、medium、high、xhigh、max、ultra；defaultReasoningEffort 為 medium。none 不支援，格式仍有效。依 task-harness model-selection 規則保留首選模型並改採宿主預設 medium。沒有強度不可調限制，原 none 未派工，不存在未知啟動；沒有產生或編造 provider 錯誤。第二候選無需派出。

## 原生宿主結果

原生 `collaboration.spawn_agent` 請求：task_name=verify_preserve、fork_turns=none、model=gpt-6-sol、reasoning_effort=medium。提供完整根目錄、成果 T1、預期 bytes、讀取範圍、禁止寫檔與回報要求的自足輸入；未繼承主責歷史。

宿主原始回應：`{"task_name":"/root/verify_preserve"}`。真實 handle：`/root/verify_preserve`。成功後先保存 handle，再進一步協調。list_agents 先顯示 running，最終顯示 completed 並附 worker 最終結果。

宿主未回傳實際執行 model 或 reasoning_effort；這兩項觀測值均為 null。請求值及 metadata 支援資訊不能當作實際模型已核實。未變更原生主責模型。

## Worker 結果與產物核對

worker 先讀專案設定與合約；一般 shell 兩次啟動失敗 exit 71，真實訊息為 `sandbox-exec: sandbox_apply: Operation not permitted`。改用 require_escalated 唯讀讀取，exit 0；這是 shell sandbox 啟動故障，並非 provider 模型錯誤。worker 以 Python 3 Path.read_bytes() 精確比較，exit 0，回報 PASS，未寫入檔案。

主責另以實際唯讀 Python 3 檢查，exit 0，結果與 worker 一致：

- 精確內容：`b'KEEP_EXISTING_CONTENT\n'`
- 長度：22 bytes
- hex：`4b4545505f4558495354494e475f434f4e54454e540a`
- SHA-256：`f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe`

preserve.txt、project-setting.md、host-model-metadata.json 的前後 SHA-256 均相同；基準指紋保存在唯一合約。只新增本 research 與唯一合約。未安裝工具服務，未修改長期設定。

## 能力與證據限制

宿主已呈現 task-harness 提醒文字，但來源、載入／信任狀態及條件續作鏈未核實；模型主動執行開始、派工前、回報後及收尾檢查。沒有建立虛假 hook 收據。session ID 與 user-turn ID 未提供，合約保留 null。原生 handle 與 completed 結果可觀測，實際執行模型／強度不可觀測。
