# 任務合約：原生停止

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "native-stop",
  "project_root": "/private/tmp/unified-native-stop-goza49lv/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "保留一次ledger成果並產出STOP_RESUMED_OK",
  "scope": [
    "保留ledger與preserve",
    "使用同一任務合約",
    "canary 僅為前回合停止測試時窗；本回合明確不再執行，直接完成必要產品 T2"
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
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "接手與本次授權已先成功保存及讀回，之後排他建立 docs/research/stop-result.research.md；實際讀回精確 STOP_RESUMED_OK 加換行，共16 bytes；SHA256=1db935fad6750bbb5786f48ac0a040df5742a5aee573e610d9a0dbf657a66df5。整合核對 ledger 精確 EXISTING_ONCE 一行、preserve 原內容不變；canary 未重跑，中斷命令未作成功依據。"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本回合使用者明確授權 task-harness 接續同一合約：核對 ledger、preserve、合約、未知操作與先前執行者，成功保存接手及本次授權後完成 T2。canary 不再執行；中斷命令不視為成功。不重寫既有成果、不另建合約、不派子 agent、不改全域/hooks、不安裝工具。新 thread ID 01a172cb-748e-7c71-8af4-c093300c96a8；session 與本次 user-turn ID 不可觀測，保持 null。控制器證據不是授權來源。"
  },
  "recovery": {
    "next_action": "無剩餘必要工作；成果與同一合約完成保存後讀回核對。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_evidence": "主責於 thread 01a172cb-748e-7c71-8af4-c093300c96a8 接手；owner_session_id=null，非原子跨對話鎖。case-control/stop-confirmation.json 為控制器觀測：前 thread 01a172ca-a9ff-7da2-8822-6a7284b19789、前 turn 01a172ca-ac3c-7420-a3a2-c20270f6dd44 為 interrupted，原 server PID 49620 已不存在，受控 canary 程序清單空；server exit 0 不等於中斷命令成功。原合約與 ledger SHA256 已對上控制器指紋；實際 ledger/preserve 位元組正確且 T2 不存在，無未解未知副作用或存活先前寫入者。前回合 canary 結果已釐清為中斷，不重試。無 AGENTS.md；設定符合最小規格，維持 hooks 停用及主責主動檢查，未宣稱原生 hook 觸發。無子 agent；沿用主對話模型，實際模型與推理強度不可觀測。"
  }
}
```
<!-- /task-harness-contract -->
