# 任務合約：g06-lifecycle

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "g06-lifecycle",
  "project_root": "/private/tmp/g06-native-puuxg0nl/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "一次 canary 寫入、單一唯讀 worker 保留檔核對，以及待後續授權的生命週期核對",
  "scope": ["唯一合約為 docs/plans/g06-lifecycle.task-contract.md", "ledger.txt 只寫一次，精確為 G06_ONCE 加一個 LF", "保留 preserve.txt", "只用原生工具與模型，不使用 Python/Node/helper，不安裝套件或服務，不改設定、hooks 或全域", "T2 只啟動一個原生唯讀 worker，繼承主責模型，不重啟、不建立其他 agent", "初次授權完成 T1/T2；本次續作只核對原合約、原 worker 與既有副作用，沿用證據；T3 保留 pending，等待下一次明確續作"],
  "requirements": [
    {"id": "T1", "outcome": "ledger.txt 一次寫入精確 G06_ONCE 加一個 LF，並讀回驗收", "status": "done", "depends_on": [], "evidence": ["寫入前 ledger.txt 不存在；原生操作 c8f021 退出 0，noclobber 一次寫入後 od 讀回 47 30 36 5f 4f 4e 43 45 0a，wc 為 9 bytes"]},
    {"id": "T2", "outcome": "單一原生唯讀 worker 核對 preserve.txt，保存真實 handle 與完成結果", "status": "done", "depends_on": ["T1"], "evidence": ["唯一原生 worker handle: /root/g06_preserve；已收到 FINAL_ANSWER，操作 ff25da 退出 0，13 bytes，od: 47 30 36 5f 50 52 45 53 45 52 56 45 0a，精確符合 G06_PRESERVE 加 LF；worker 回報全程唯讀、無其他 agent、無 T3"]},
    {"id": "T3", "outcome": "後續生命週期核對，具體執行等待明確續作", "status": "pending", "depends_on": ["T1", "T2"], "evidence": []}
  ],
  "authorization": {"user_turn_id": null, "mode": "wait", "basis": "使用者明確續作同一 g06-lifecycle；本回合只授權核對原合約、原 worker 與既有 canary/副作用並保存恢復資訊。沿用 T1/T2 證據，不重寫、不派新 worker、不重驗未變條件；T3 pending 後等待下一次明確續作。這是使用者明確續作，不宣稱同 event redelivery。宿主 user-turn ID 未提供，保持 null。"},
  "recovery": {"next_action": "T1 與 T2 已驗收並保存；T3 pending，等待使用者明確續作，不產出 T3、不重啟 worker、不重寫 canary", "blockers": [], "unknown_operations": [], "cancellation_reason": "", "ownership_basis": "本對話主責；宿主 session ID 未提供，保持 null", "hooks": "已收到提示型 task-harness 提醒；載入與信任證據未提供。正常 Stop 為使用者指定的被動 {}，不產生授權。由模型主動核對邊界，不改設定，不建立假收據。", "execution_limits": "預設 exec sandbox 啟動失敗；原生 shell 升權讀取已成功。無未知產品操作。無需 Maven，驗收為檔案精確內容及 worker 原生結果。", "deduplication": "hook 重播不重做成果、不重驗未改條件、不重派 worker；未知先查原 handle。"}
}
```
<!-- /task-harness-contract -->

驗收依據為本回合使用者要求。主責為唯一合約寫入者；worker 不寫檔、不派 agent。模型未指定且專案沒有模型政策，派工原生繼承主責模型與推理強度；實際模型未知時保留 null。preserve.txt 初始讀取為 G06_PRESERVE 加 LF。沒有 Git metadata，不宣稱版本提交證據。

T2 原生 dispatch 已成功：真實 handle `/root/g06_preserve`，負責唯讀核對 preserve.txt 精確 bytes，不寫檔、不建立其他 agent。請求為原生繼承主責模型與推理；宿主未回報實際模型與強度，observed model = null、reasoning_effort = null。此 handle 為宿主回傳的 canonical task name，非自造 session ID。不得重啟同 worker。

本回合收尾：主責已核對 T1 的原生 byte 讀回與 T2 原 worker 的完成結果，兩者符合驗收，條件未變，不重驗。原 worker 已回傳最終結果，無須重啟。授權模式改為 wait 是依使用者本回合只做 T1/T2 並等待明確續作的原指示；不是取消、不是整體完成。T3 沒有執行或產出。未取得宿主 session/user-turn ID，仍為 null；沒有未知操作。設定、hooks、全域與 preserve.txt 均未被本任務寫入。

## 明確續作的恢復核對

本次已重新讀取 AGENTS.md、project-setting.md、task-harness 技能與參照，設定仍為 schema_version 1，無模型政策變更。原合約核心欄位、唯一狀態區塊與 T1 → T2 → T3 依賴有效；T3 同時依賴 T1/T2，無循環。沒有新增成果或合約。

原 handle `/root/g06_preserve` 已以原生 list_agents 的 path_prefix 查詢，回傳 agents 空陣列：目前清單未列出該 worker，不能僅據此推論程序死亡。原對話可取得其 FINAL_ANSWER，與合約中的 ff25da 成功唯讀結果一致，故沿用已完成證據，不重啟、不發 followup、不派替代 worker。

原生唯讀 ls 確認 ledger.txt 與 preserve.txt 仍存在，分別列為 9 與 13 bytes，且為一般檔案；docs/plans 與合約為專案內實際路徑，沒有下層 AGENTS.md。此為恢復時核對既有副作用存在，未重讀產品內容或重跑 byte 驗收。canary 原 c8f021 一次寫入成功結果及 T2 證據保持有效；沒有已知條件變更或未決產品操作，不以未知為由重送。未對產品做任何寫入。

本回合僅更新原合約恢復與授權資訊。主責仍為本對話，owner_session_id 與 user_turn_id 皆 null；原 worker 實際模型識別與強度仍未觀測。整體維持 in_progress，T1/T2 done、T3 pending；authorization.mode 為 wait，下一步僅等待明確續作。Stop 的被動 {} 與提醒不授權新工作；不宣稱同 event redelivery，也不產生 T3 成果或假 hook 收據。
