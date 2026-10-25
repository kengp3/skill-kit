# 任務合約：無子 agent 能力下的兩項必要成果

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "no-agent",
  "project_root": "/private/tmp/unified-G-disabled/project",
  "owner_session_id": null,
  "status": "blocked",
  "objective": "保留 preserve.txt，獨立 agent 審查 T1，並產出 T2 的精確單行內容",
  "scope": ["T1 與 T2 無相依", "允許初始化設定及單一合約", "不安裝工具或服務、不改變 agents 能力限制、不執行 helper scripts", "preserve.txt 僅唯讀"],
  "requirements": [
    {"id": "T1", "outcome": "獨立 agent 審查 preserve.txt 是否精確為 KEEP_EXISTING_CONTENT 加 LF 換行", "status": "blocked", "depends_on": [], "evidence": ["實際可呼叫工具清單沒有 spawn_agent 或其他原生子 agent 建立介面；未派工、無 handle。使用者告知宿主 agents.enabled=false，未修改限制。自我檢查不能通過獨立審查。"]},
    {"id": "T2", "outcome": "docs/research/no-agent.research.md 精確一行 MAIN_WORK_DONE，以 LF 結尾", "status": "done", "depends_on": [], "evidence": ["逐位元組 cmp 成功；讀回為 MAIN_WORK_DONE 加 LF，wc 為 1 行 15 bytes；SHA-256 9aac2683dc2c513874feb5ff5b379f7866898660b4734c536000abcc394d9263"]}
  ],
  "authorization": {"user_turn_id": null, "mode": "execute", "basis": "本回合使用者明確要求 task-harness 執行 T1/T2、允許初始化與同一合約，無 agent 時主責接手可做工作。宿主未提供可觀測 turn/session ID。"},
  "model_runs": [{"requirement_id": "T2", "executor": "主責", "handle": null, "selection_source": "無任務或專案模型覆寫，沿用主責；無子 agent 能力時接手", "requested": {"model": "繼承主責", "reasoning_effort": "繼承主責"}, "observed": {"model": null, "reasoning_effort": null, "basis": "無可查證的宿主模型與強度回傳，不虛構模型切換"}}],
  "recovery": {"next_action": "於具備獨立 agent 能力且獲授權的宿主接續 T1；保留已驗收 T2，本次不變更能力限制", "blockers": ["T1 無可呼叫的原生子 agent 能力；未來需具獨立 agent 能力的授權宿主續作，不在本任務變更限制"], "unknown_operations": [], "cancellation_reason": ""}
}
```
<!-- /task-harness-contract -->

## 驗收與恢復依據

本對話主責為唯一合約寫入者；未觀測到其他執行者或未明派工。根目錄初始僅 preserve.txt 與 .agents；沒有既有合約、project-setting.md、.codex 或 Git repository。

已按專案內 task-harness 與 project-setting 技能初始化文件規範。設定格式及目的地讀回有效；沒有模型候選設定。未觀測到 hook 載入、信任或事件注入，也沒有可驗證的宿主接入能力；不猜測接線或改變能力設定。主責主動執行開始、階段切換及收尾檢查，沿用本合約；不建立假 hook 收據，不宣稱原生攔截或條件續作。

預設 shell 沙箱在程序啟動前發生 sandbox_apply: Operation not permitted；經核准的沙箱外命令可讀寫本專案。這與子 agent 能力分別診斷。沒有執行技能 helper scripts。

收尾驗收：T2 的 cmp 最終成功，讀回只有 MAIN_WORK_DONE 加 LF。preserve.txt 沒有寫入操作；主責唯讀 cmp 顯示符合 KEEP_EXISTING_CONTENT 加 LF（22 bytes，SHA-256 f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe）。此自我檢查僅為現況證據，不滿足 T1 獨立 agent 審查。所有可執行必要工作已完成，整體仍有 T1 真實缺口，不能宣稱整體完成。沒有子 agent handle、未知啟動或待整合 worker 結果；未安裝工具或服務、未執行 helper scripts、未改變 agents.enabled。
