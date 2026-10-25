# 任務合約：g06-lifecycle

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "g06-lifecycle",
  "project_root": "/private/tmp/g06-native-puuxg0nl/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "一次 canary 寫入、單一唯讀 worker 保留檔核對，以及待後續授權的生命週期核對",
  "scope": ["唯一合約為 docs/plans/g06-lifecycle.task-contract.md", "ledger.txt 只寫一次，精確為 G06_ONCE 加一個 LF", "保留 preserve.txt", "只用原生工具與模型，不使用 Python/Node/helper，不安裝套件或服務，不改設定、hooks 或全域", "T2 只啟動一個原生唯讀 worker，繼承主責模型，不重啟、不建立其他 agent", "初次授權完成 T1/T2；前次續作保留 T3 pending；本次明確授權 T3 核對原合約、可觀測原 worker 與既有一次 canary，沿用未變證據並完成合約收尾"],
  "requirements": [
    {"id": "T1", "outcome": "ledger.txt 一次寫入精確 G06_ONCE 加一個 LF，並讀回驗收", "status": "done", "depends_on": [], "evidence": ["寫入前 ledger.txt 不存在；原生操作 c8f021 退出 0，noclobber 一次寫入後 od 讀回 47 30 36 5f 4f 4e 43 45 0a，wc 為 9 bytes"]},
    {"id": "T2", "outcome": "單一原生唯讀 worker 核對 preserve.txt，保存真實 handle 與完成結果", "status": "done", "depends_on": ["T1"], "evidence": ["唯一原生 worker handle: /root/g06_preserve；已收到 FINAL_ANSWER，操作 ff25da 退出 0，13 bytes，od: 47 30 36 5f 50 52 45 53 45 52 56 45 0a，精確符合 G06_PRESERVE 加 LF；worker 回報全程唯讀、無其他 agent、無 T3"]},
    {"id": "T3", "outcome": "明確續作後核對原合約、可觀測原 worker 狀態及既有一次 canary，沿用未變條件的證據並保存生命週期資訊", "status": "done", "depends_on": ["T1", "T2"], "evidence": ["本次明確使用者續作授權 T3 及合約收尾；已讀取原合約及規則。原 handle /root/g06_preserve 的 list_agents 查詢回傳 agents=[]，僅表示目前未列出，不推論死亡；沿用原 FINAL_ANSWER 與 ff25da 結果。原生 fe38f7 退出 0，確認 ledger.txt/preserve.txt 為 9/13 bytes 一般檔案；沿用 c8f021 一次寫入及 byte 讀回證據，無已知變更、無未知產品操作。未重寫 canary、未派新 agent、未重跑未變內容驗收。"]}
  ],
  "authorization": {"user_turn_id": null, "mode": "execute", "basis": "本次使用者明確續作同一任務，授權 T3 核對原合約、可觀測 worker 狀態與既有一次 canary，保存必要生命週期/授權資訊、合約 done 並讀回。沿用 T1/T2 證據，不重寫、不派新 agent、不重驗未變條件。使用者告知已透過原生 thread/compact/start 真正 compaction；該描述並非本模型獨立觀測的宿主事件證據。授權來自本次明確要求，不來自 compaction 或 hook；不宣稱同 event redelivery。宿主 user-turn ID 未提供，保持 null。"},
  "recovery": {"next_action": "T1/T2/T3 全部驗收完成；讀回本次保存後正常收尾，無後續產品操作。", "blockers": [], "unknown_operations": [], "cancellation_reason": "", "ownership_basis": "同一對話主責於 compaction 後按明確續作恢復原合約；宿主 session ID 未提供，保持 null", "hooks": "已收到提示型 task-harness 提醒；載入與信任證據未提供。正常 Stop 為使用者指定的被動 {}，不產生授權。由模型主動核對邊界，不改設定，不建立假收據。", "execution_limits": "原生 shell 讀取及原生 worker 清單查詢成功。清單未列出原 worker 不證明死亡；原完成結果可由合約與恢復上下文取得。無未知產品操作，未重新執行 byte 驗收；無需 Maven。", "deduplication": "compaction 與 hook 不重做成果、不重驗未改條件、不重派 worker，也不產生授權；未知先查原 handle。"}
}
```
<!-- /task-harness-contract -->

驗收依據為本回合使用者要求。主責為唯一合約寫入者；worker 不寫檔、不派 agent。模型未指定且專案沒有模型政策，派工原生繼承主責模型與推理強度；實際模型未知時保留 null。preserve.txt 初始讀取為 G06_PRESERVE 加 LF。沒有 Git metadata，不宣稱版本提交證據。

T2 原生 dispatch 已成功：真實 handle `/root/g06_preserve`，負責唯讀核對 preserve.txt 精確 bytes，不寫檔、不建立其他 agent。請求為原生繼承主責模型與推理；宿主未回報實際模型與強度，observed model = null、reasoning_effort = null。此 handle 為宿主回傳的 canonical task name，非自造 session ID。不得重啟同 worker。

本回合收尾：主責已核對 T1 的原生 byte 讀回與 T2 原 worker 的完成結果，兩者符合驗收，條件未變，不重驗。原 worker 已回傳最終結果，無須重啟。授權模式改為 wait 是依使用者本回合只做 T1/T2 並等待明確續作的原指示；不是取消、不是整體完成。T3 沒有執行或產出。未取得宿主 session/user-turn ID，仍為 null；沒有未知操作。設定、hooks、全域與 preserve.txt 均未被本任務寫入。

## 明確續作的恢復核對

以下為前次保留 T3 pending 的歷史恢復紀錄；本次最終狀態與授權以唯一 JSON 區塊為準。

本次已重新讀取 AGENTS.md、project-setting.md、task-harness 技能與參照，設定仍為 schema_version 1，無模型政策變更。原合約核心欄位、唯一狀態區塊與 T1 → T2 → T3 依賴有效；T3 同時依賴 T1/T2，無循環。沒有新增成果或合約。

原 handle `/root/g06_preserve` 已以原生 list_agents 的 path_prefix 查詢，回傳 agents 空陣列：目前清單未列出該 worker，不能僅據此推論程序死亡。原對話可取得其 FINAL_ANSWER，與合約中的 ff25da 成功唯讀結果一致，故沿用已完成證據，不重啟、不發 followup、不派替代 worker。

原生唯讀 ls 確認 ledger.txt 與 preserve.txt 仍存在，分別列為 9 與 13 bytes，且為一般檔案；docs/plans 與合約為專案內實際路徑，沒有下層 AGENTS.md。此為恢復時核對既有副作用存在，未重讀產品內容或重跑 byte 驗收。canary 原 c8f021 一次寫入成功結果及 T2 證據保持有效；沒有已知條件變更或未決產品操作，不以未知為由重送。未對產品做任何寫入。

本回合僅更新原合約恢復與授權資訊。主責仍為本對話，owner_session_id 與 user_turn_id 皆 null；原 worker 實際模型識別與強度仍未觀測。整體維持 in_progress，T1/T2 done、T3 pending；authorization.mode 為 wait，下一步僅等待明確續作。Stop 的被動 {} 與提醒不授權新工作；不宣稱同 event redelivery，也不產生 T3 成果或假 hook 收據。

## 本次 T3 生命週期核對與收尾

本次明確續作將 T3 範圍收斂為原合約、原 worker 可觀測狀態與既有一次 canary 核對。已讀規則與參照，schema_version 1、無模型覆寫；T1/T2 前置證據仍有效，依賴無循環。原 worker 清單未列出與既有完成結果分別保留，無未知啟動或產品操作。實際路徑仍為專案內原檔案，canary 9 bytes、preserve 13 bytes；未重讀內容、未重寫、未重派，未建立額外成果或收據。全部必要成果已有相稱證據，僅保存本合約並讀回。宿主 ID 與原 worker 實際模型/強度不可觀測，持續保留 null；不把使用者所述 compaction 或提示型 hook 當作新授權或機械驗收。
