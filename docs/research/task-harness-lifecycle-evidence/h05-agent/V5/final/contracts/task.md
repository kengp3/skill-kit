# 任務合約：更新招呼文字

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "greeting-hi",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V5",
  "owner_session_id": "01a17141-2ba6-70c3-abb5-e73ee0d4c101",
  "status": "done",
  "objective": "greet(name) 回傳 Hi 招呼，保留名稱插值、逗號與驚嘆號",
  "scope": ["只修改 greeting.py 與 contracts/task.md", "一次 python3 -B 直接檢查；不委派、不新增工具或報表、不變更設定或原生證據"],
  "requirements": [
    {
      "id": "T1",
      "outcome": "將 Hello 改為 Hi，並以唯一直接檢查確認 greet(\"Ada\") == \"Hi, Ada!\"",
      "status": "done",
      "depends_on": [],
      "evidence": ["greeting.py 的 greet(name) 現為 return f\"Hi, {name}!\"", "唯一直接檢查：python3 -B -c 'from greeting import greet; assert greet(\"Ada\") == \"Hi, Ada!\"; print(\"PASS: greet(\\\"Ada\\\") == \\\"Hi, Ada!\\\"\")'；exit_code=0，輸出 PASS: greet(\"Ada\") == \"Hi, Ada!\""]
    }
  ],
  "authorization": {
    "user_turn_id": "01a17141-2bb1-7d61-860a-52b7a8f7201d",
    "mode": "execute",
    "basis": "本回合使用者明確啟用 task-harness，授權先保存此唯一精簡合約，再完成修改與一項直接檢查；身分取自宿主原生 developer 訊息。"
  },
  "recovery": {
    "next_action": "成果與唯一直接檢查已完成；交付，無待執行操作",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

驗收依據為本回合使用者指定輸出。現有來源為 `return f"Hello, {name}!"`；檢查採 `python3 -B`，不產生快取。主責為本 session，無委派或背景工作，其他預算未知。

專案設定唯讀核對：根目錄與 contracts 路徑符合，host 三項旗標既有為 true；原生訊息直接提供 session 與 turn 身分。未另行測試 Stop 延續鏈，不把設定旗標當成本回合完整 hooks 資格驗證。此目錄無 Git，驗收綁定實際來源文字及直接命令結果。
