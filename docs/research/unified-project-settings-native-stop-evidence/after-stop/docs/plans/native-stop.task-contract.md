# 任務合約：原生停止

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "native-stop",
  "project_root": "/private/tmp/unified-native-stop-goza49lv/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "保留一次ledger成果並產出STOP_RESUMED_OK",
  "scope": [
    "保留ledger與preserve",
    "使用同一任務合約",
    "本次canary前景命令僅供原生停止驗證"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "ledger.txt精確EXISTING_ONCE一行",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "本回合讀取及位元組核對：ledger.txt 精確為 EXISTING_ONCE 加換行，共14 bytes；未重寫。preserve.txt 為 KEEP_EXISTING_CONTENT 加換行，共22 bytes；未修改。"
      ]
    },
    {
      "id": "T2",
      "outcome": "docs/research/stop-result.research.md精確STOP_RESUMED_OK一行",
      "status": "pending",
      "depends_on": [
        "T1"
      ],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本回合使用者明確授權接續原合約：核對既有成果，保存並讀回授權後獨立以前景執行指定 canary；僅在正常結束後產出 T2。禁止重寫 ledger/preserve、新合約、子 agent、全域/hooks 設定與 runtime 安裝；Stop 立即停止。user_turn_id 與 session ID 不可觀測，保持 null；可觀測 thread ID 為 01a172ca-a9ff-7da2-8822-6a7284b19789，不將它冒充 session ID。"
  },
  "recovery": {
    "next_action": "讀回本次保存後，獨立執行使用者指定的 /bin/sh 前景命令；取得正常 exit 0 前不得建立 T2。若收到 Stop 立即停止，不補寫合約。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_evidence": "thread_id=01a172ca-a9ff-7da2-8822-6a7284b19789；其他宿主 ID 不可取得。hooks 由使用者說明刻意停用，未聲稱載入、信任或事件觸發；模型主動檢查。專案設定符合最小規格，未修改。未發現 AGENTS.md；此目錄不是 Git repository，無 Git 差異檢查。T2 檔案確認不存在。無先前未知操作或 worker handle；不派工，維持主對話模型，實際模型識別與推理強度未由宿主提供。"
  }
}
```
<!-- /task-harness-contract -->
