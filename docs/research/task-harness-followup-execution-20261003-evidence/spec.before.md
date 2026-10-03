# Task Harness 規格

## Objective

建立可獨立攜帶的 Codex skill，把多步驟需求轉成有依賴、負責範圍與驗收方式的任務清單，按授權分派、執行、整合及續作。

## Background

使用者要求先研究截至 2026-10-02 的最佳實踐，再建立 skill。既有 `define-task` 處理需求定義；本 skill 接續處理任務生命週期，不重建需求訪談或 agent runtime。

## Materials

- [研究報告](../research/task-harness-202610.research.md)：官方工程案例、框架文件及研究限制。
- 本次指定的 skill-creator、using-agent-skills、deep-research、ponytail。
- 已確認專案根目錄 `/Users/kengp3/Workspaces/mine/simple-skills` 及 `project-setting.md`。

## Boundaries

- 新增 `skills/task-harness/`；維護 README 技能索引。
- 不安裝依賴、不更動其他 skills、不修改既有未提交工作、不 commit/push 或發布。
- 不另造 scheduler、資料庫、鎖服務、固定多角色 pipeline 或自動重啟程序。
- 規劃要求不授權執行；執行要求不擴張外部寫入、發送訊息或發布權限。

## Assumptions

- 以此技能集合中的獨立 skill 為交付；可透過本機 SKILL.md 路徑使用，尚不做全域安裝。
- 原生 subagent 可用且允許時才分派；否則由主 agent 串行執行。
- 單一 coordinator 寫入權威任務清單；同一 scope 的重複執行要先核對存活 worker。

## Definition of Done

1. 支援 plan-only、execute、resume，且不混淆三者授權。
2. 每項任務保留穩定 ID、成果、依賴、owner、寫入範圍、驗收、驗證與狀態；禁止循環依賴、重複 claim、未驗證 done。
3. 具備分派契約、結果整合、失敗與重試界線、過期證據及副作用續作處理。
4. SKILL.md 可獨立使用；沒有 repo-root runtime references 或強制其他 skills。
5. 官方 skill validator 與 research validator 通過；以隔離 workspace 做真實行為驗證，保存實際結果與限制。

## 驗證方法

- Skill：`python3 /Users/kengp3/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-harness`（此環境需透過 PYTHONPATH 指向既有 PyYAML；精確命令記錄於驗證報告）。
- Research：`python3 /Users/kengp3/.codex/skills/deep-research/scripts/validate_research_report.py docs/research/task-harness-202610.research.md`。
- 行為：獨立 agent 在隔離 fixture 驗證 planning、execution、resume；檢查實際 artifacts 與命令結果，不以 headings/措辭比對充當驗收。

## 並行驗收契約

- **Dispatch protocol（blocking）**：選定本輪已 ready、互不衝突且在授權／可用容量內的任務群組。逐一 dispatch → 使用真實 handle 保存各自 start checkpoint → 下一次 dispatch；群組派完前不得主動 wait、collect、accept 或執行無關工作。readiness、容量或安全條件改變時記錄縮減／停止原因；派工或 checkpoint 失敗須先處理。
- **自然完成不違規**：worker 在下一次派工前完成，或系統自動送來完成通知，不等於 coordinator 主動等待；不得以「所有 dispatch 早於 first completion」作為通用必要條件。
- **Runtime overlap（observational）**：分別記錄實際 worker 區間與派工延遲；零重疊不單獨構成 Skill 派工失敗，也不足以歸因模型或 scheduler。使用者若明確要求實際重疊，另列成果驗收，不能取消該要求；不得加入人工等待以製造重疊。
- **既有 gates 保留**：逐次 checkpoint、attempt、依賴接受後才能啟動、單一 tracker writer、receipt 與受測版本核對仍各自驗收。派工順序通過不代表其他 gates 通過。
- 契約修訂以新判讀附註呈現；歷史測試契約、結果及 raw evidence 保留。參見[2026-10-03 判讀](../research/task-harness-parallel-gate-20261003.research.md)。
