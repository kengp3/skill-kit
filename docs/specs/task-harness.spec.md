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
5. 官方 skill validator 與 research validator 通過；以獨立測試資料夾做真實行為驗證，保存實際結果與限制。一般功能 smoke 不以強隔離為前置條件，也不得據此宣稱盲測、模型比較或安全隔離成立。
6. Core 不要求為 Harness 額外安裝語言 runtime；使用宿主可提供的原生證據，Python evidence helper 為選配。缺必要驗收能力時不得假成功。

## 驗證方法

- Skill：`python3 /Users/kengp3/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-harness`（此環境需透過 PYTHONPATH 指向既有 PyYAML；精確命令記錄於驗證報告）。
- Research：`python3 /Users/kengp3/.codex/skills/deep-research/scripts/validate_research_report.py docs/research/task-harness-202610.research.md`。
- 行為：agent 在獨立 fixture 驗證 planning、execution、resume；檢查實際 artifacts 與命令結果，不以 headings/措辭比對充當驗收。共用宿主的存取範圍限制須揭露；強隔離需求只在相應研究或安全契約中另行驗證。

## 原生證據與選配 helper

- Core 優先使用宿主的實際 tool input／最終 result、cwd、相關輸出，以及可歸屬的受測版本。使用可在 resume 重新取得的原生 history，或由宿主內建能力直接保存原始工具資料；tracker 摘要與人工抄值不能替代它。
- 指紋／版本綁定包含實際 dirty content。來源改變後重新核對 acceptance；command string 不冒稱 argv，合併 output 不冒稱獨立 stdout/stderr，外層成功不代替個別 check 的最終結果。
- `scripts/run_check.py` 保留為選配；需要 process argv、分離 streams、SHA-256 或 exclusive-create receipt 且 Python 3 已存在時可使用。不自動安裝語言或服務；被測專案自身 checker 的語言需求另計。
- 缺可歸屬版本、最終結果或可恢復 receipt 時，相關驗收維持 verifying／blocked，仍可規劃或完成獨立安全工作。unknown 外部副作用不得為補證據重播。
- 宿主最低能力是指示／tracker／產品的必要讀寫，以及該項驗收所需的原生結果、版本與恢復能力。Code mode 是本次實測宿主的一條可行路徑，不要求其他宿主提供同名工具。普通檔案寫入不保證原子 reservation，CRC 不宣稱抗竄改。
- 執行期不讀取本 repository 的研究 scripts、私有 session exports 或其他 skills。Core-only 安裝可省略選配 helper；完整套件保留 helper 方便已有 Python 的宿主。
- 已驗證範圍與限制見[普通資料夾功能驗收](../research/task-harness-functional-20261003.research.md)；不由單一宿主 smoke 外推所有平台或關閉其他歷史 findings。

## 並行驗收契約

- **Dispatch protocol（blocking）**：選定本輪已 ready、互不衝突且在授權／可用容量內的任務群組。逐一 dispatch → 使用真實 handle 保存各自 start checkpoint → 下一次 dispatch；群組派完前不得主動 wait、collect、accept 或執行無關工作。readiness、容量或安全條件改變時記錄縮減／停止原因；派工或 checkpoint 失敗須先處理。
- **自然完成不違規**：worker 在下一次派工前完成，或系統自動送來完成通知，不等於 coordinator 主動等待；不得以「所有 dispatch 早於 first completion」作為通用必要條件。
- **Runtime overlap（observational）**：分別記錄實際 worker 區間與派工延遲；零重疊不單獨構成 Skill 派工失敗，也不足以歸因模型或 scheduler。使用者若明確要求實際重疊，另列成果驗收，不能取消該要求；不得加入人工等待以製造重疊。
- **既有 gates 保留**：逐次 checkpoint、attempt、依賴接受後才能啟動、單一 tracker writer、receipt 與受測版本核對仍各自驗收。派工順序通過不代表其他 gates 通過。
- 契約修訂以新判讀附註呈現；歷史測試契約、結果及 raw evidence 保留。參見[2026-10-03 判讀](../research/task-harness-parallel-gate-20261003.research.md)。

## Checkpoint 與驗收交接

- Tracker 明列 numeric task attempt、check ID／check attempt 及 acceptance receipt；task restart 與 check retry 分開。首次為 1，未知歷史先 reconcile；coordinator check／retry 前須成功保存該次 attempt 與新 receipt 路徑。Worker 在獨立 evidence 路徑保存 checks，回傳由 coordinator 更新 tracker。
- Worker ownership 包含產品範圍及獨立 evidence 路徑；若僅授權產品寫入，coordinator 接手 receipt-producing verification。缺可歸屬驗證時保持 verifying，不以稍後 integration 補作先前 acceptance。
- 前置任務各自 receipt 的實際命令、cwd、結果與 fingerprint 經核對後，先成功保存 receipt reference 與 done；再確認 successor readiness、保存其起始 checkpoint，才開始產品動作。此 gate 適用 coordinator 實作，不能只延後最終 checker。
- 若歷史 attempt 數字不存在，保留 unknown；一個歷史 done/running 記錄不證明累計次數為 1。核對 artifacts／存活 worker／副作用後，可為安全新工作命名 resume epoch，以局部 task/check 計數從 1 開始；未知副作用仍不得重播。
