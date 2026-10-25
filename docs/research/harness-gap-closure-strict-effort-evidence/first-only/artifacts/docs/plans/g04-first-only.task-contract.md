# 任務合約：g04-first-only

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "g04-first-only",
  "project_root": "/private/tmp/g04-first-only-03wn2vm6/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "由獨立唯讀 worker 核對 preserve.txt，主責驗收真實回報後建立精確成果並讀回同一合約。",
  "scope": ["只新增本合約及 docs/research/strict-worker.research.md", "保留所有初始檔案與長期設定；hooks 停用，不改 hooks 或信任", "不安裝服務或套件、不使用 Python、Node 或 helper、不存取其他 root", "唯一成果 T1；使用原生獨立 worker，fork_turns=none 與自足輸入"],
  "requirements": [{"id": "T1", "outcome": "獨立 worker 實測 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加 LF；主責驗收後寫出 G04_STRICT_WORKER_OK 加 LF，讀回成果與同一合約", "status": "done", "depends_on": [], "evidence": ["獨立 worker /root/strict_worker 真實 MESSAGE 與 FINAL_ANSWER：printf + cmp exit 0；od 為 4b 45 45 50 5f 45 58 49 53 54 49 4e 47 5f 43 4f 4e 54 45 4e 54 0a；wc 22 bytes，未寫檔。", "主責驗收 worker 回報後寫入成果；工具 chunk 4d1128 exit 0：成果 cmp 無差異、cat 讀回、od 結尾 0a、wc 21 bytes；SHA256 66a107d1569bb1737653f049fb333e96c8cb871b58e9de749a01aa310c7f5fab。", "初始所有 25 檔案 SHA256 與 a6ae85 基線逐項一致；只新增指定合約與成果。"] }],
  "authorization": {"user_turn_id": null, "mode": "execute", "basis": "本次使用者明確啟用 task-harness、指定唯一根目錄、合約與候選並授權原生子 agent；宿主未提供可觀測 user-turn/session ID。後續環境日期更新未變更任務授權。"},
  "model_overrides": [{"applies_to": "T1 獨立唯讀 worker", "candidates": "[gpt-6.1-sol;minimal, gpt-6-sol;low]", "basis": "本次使用者明確指定；strict 不可變更強度只適用首選 minimal，後續 low 明確合格。"}],
  "model_runs": [{"requirement_id": "T1", "executor": "獨立唯讀 worker", "handle": "/root/strict_worker", "selection_source": "本次使用者指定之第二候選；metadata preflight 支援 low", "requested": {"model": "gpt-6-sol", "reasoning_effort": "low"}, "observed": {"model": null, "reasoning_effort": null, "basis": "collaboration.spawn_agent 成功回傳 task_name /root/strict_worker；未回傳實際模型或強度。fork_turns=none，自足輸入，僅唯讀核對。"}}, {"requirement_id": "T1", "executor": "未啟動的首選候選", "handle": null, "selection_source": "本次使用者指定", "requested": {"model": "gpt-6.1-sol", "reasoning_effort": "minimal"}, "observed": {"model": null, "reasoning_effort": null, "basis": "派工前讀取 host-model-metadata.json：gpt-6.1-sol supportedReasoningEfforts 為 low/medium/high/xhigh/max/ultra，無 minimal。依 strict 限制略過，未發送不合格請求。"}}],
  "recovery": {"next_action": "T1 已驗收完成；正常收尾讀回同一合約及成果，無待辦或未知操作。", "blockers": [], "unknown_operations": [], "cancellation_reason": ""}
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

使用者唯一 T1 為 acceptance source。精確位元組比對使用原生 shell printf 與 cmp、od、wc；不需 Java build，因沒有程式碼變更。主責是唯一合約及成果寫入者，worker 不寫檔。設定已核對符合 schema 1，分類與本次指定路徑一致，無需修復。

## 恢復與證據

目前主責為本對話 /root；session 與 user-turn 宿主識別不可觀測，故保持 null。hooks 依明確指示停用，以模型主動檢查開始、派工前、worker 回報後及收尾邊界；不宣稱 hook 載入、信任或事件成功。

最初普通唯讀命令兩次於執行前遭 sandbox-exec sandbox_apply Operation not permitted（exit 71）；依使用者 scoped 授權 require_escalated 重試本案命令成功。git status 顯示本案例不是 git repository，docs 原不存在；初始根目錄只有 .agents、AGENTS.md、project-setting.md、host-model-metadata.json、preserve.txt。已用 find/shasum 原生命令取得初始檔案指紋，保留於工具原始輸出，收尾核對。無其他執行者或舊合約。

主責已驗收 /root/strict_worker 的真實實測回報（MESSAGE 與 FINAL_ANSWER）；其原生命令證據支持精確內容，並非主責代做獨立核對。worker 原生命令同樣遇到啟動前 sandbox 拒絕後 scoped 重試成功。spawn 回應只提供 task_name，worker 回報也不提供 host 實際模型證據，因此 observed model/reasoning_effort 仍為 null。

收尾主動檢查：唯一 T1 無依賴、自指或循環；唯一 JSON 狀態區塊與固定標記完整，核心欄位及授權保留。已核對 correctness（精確位元組）、readability（單一合約）、architecture（無程式變更）、security（限兩個指定檔案）、performance（無執行程式變更），無 required findings。初始 25 個檔案指紋逐項一致；保留 preserve.txt、技能與長期設定，不新增 hook 收據。實際時間、預算與節省人時無可比較數據，不作估稱。
