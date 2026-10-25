# 任務合約：Packaged result

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "packaged-result",
  "project_root": "/private/tmp/unified-t08-mxgiz2qd/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "產出指定單行檔案、讀回驗收並保留 preserve.txt",
  "scope": ["透過 project-setting 初始化專案規範及提醒設定", "僅一份任務合約", "docs/research/packaged-result.research.md 精確為 PACKAGED_OK 加一個換行", "preserve.txt 保持 KEEP_EXISTING_CONTENT 加一個換行", "不安裝 runtime、服務，不執行 helper scripts"],
  "requirements": [
    {
      "id": "T1",
      "outcome": "初始化設定有效；指定產物逐位元組讀回符合且 preserve.txt 未變；同一合約保存驗收與限制",
      "status": "done",
      "depends_on": [],
      "evidence": ["project-setting.md 已寫入並讀回：七種分類、唯一 Task Harness 區段及 schema_version 1；無模型覆寫", ".codex/hooks.json 與 config.toml 已寫入讀回；尚無新工作階段載入或信任證據", "直接 cat、wc、od 驗收 exit_code 0：docs/research/packaged-result.research.md 為 1 行 12 bytes，完整 hex 50 41 43 4b 41 47 45 44 5f 4f 4b 0a", "preserve.txt 為 1 行 22 bytes；完整 hex 4b 45 45 50 5f 45 58 49 53 54 49 4e 47 5f 43 4f 4e 54 45 4e 54 0a，與初始讀回內容一致", "收尾清單只有設定、唯一合約、指定產物及原 preserve.txt；無假收據、runtime、服務或 helper 執行。主責核對 T1 無未完成必要成果；未把提醒當機械驗收。"]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本回合使用者明確啟用已安裝 task-harness，確認根目錄並允許初始化設定與唯一合約及指定產物。宿主未提供可觀測的回合 ID。"
  },
  "recovery": {
    "next_action": "必要成果已驗收；讀回收尾保存。若續作先核對同一合約、最新授權與實際檔案",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "context": "目前對話主責維護；宿主 session ID 不可觀測。未派出 workers，無背景工作或未知副作用。已收到與套件 SessionStart、UserPromptSubmit 定義相符的兩則提醒；不能由此證明信任介面狀態。尚無 Stop 事件證據；收尾由模型主動核對。新 project-setting hooks 尚未重新載入驗證，不新增重複 harness hooks 或假收據。一般沙箱啟動失敗，改用獲准直接 shell 檔案操作，未執行 helper。依模型政策沿用主責當前模型與強度，實際模型與強度無獨立宿主證據，未聲稱切換模型。"
  }
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

來源為本回合使用者要求；使用直接檔案內容、位元組與行數檢查，規模相稱，不執行測試框架或 helper。preserve.txt 初次讀回為 KEEP_EXISTING_CONTENT，22 bytes。初始化前專案僅有該檔，沒有既有合約、下層指令或符號連結。

## 恢復與變更依據

使用已安裝 kengp3-harness 0.3.0 的 task-harness 與 project-setting 規則。主責按同一合約主動核對開始、階段變更及收尾；提醒不是機械驗收，不提供原子鎖或條件續作保證。宿主信任／新工作階段與 SubagentStart 測試不屬產品驗收證據；不為測試另開代理。
