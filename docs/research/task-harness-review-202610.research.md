# Task Harness review 與驗證

As-of：2026-10-02。範圍：`skills/task-harness/` 及其規格；本次完成獨立審查、隔離行為測試、最小修正及受影響情境重測。**本次驗收通過，沒有未處理的 Required finding。**

## 結果與最小修正

初次文字審查沒有找出必要修正；實際前向測試揭露 R1：產生的計畫雖然只有 C → A 的顯式依賴，卻要求 C 驗證完才能將 A 標為 done。A 等 C 驗收、C 等 A done，違反就緒規則，無法前進。

僅在 [SKILL.md](../../skills/task-harness/SKILL.md) 任務拆分段增加一條規則：成果與自身必要驗收放在同一任務；分開的 integration task 只能依賴可獨立驗收的成果，不能反過來阻止其前置任務完成；派工前推演驗收依賴。沒有增加 runtime、套件、腳本依賴、角色層級或額外批准步驟。

新的獨立 agent 收到相同需求與原始草案，產生單一 A 任務，包含完整實作與驗證；保留 B、C 舊 ID 的合併對照。獨立 reviewer 確認狀態可走完 `pending → running → verifying → done`，需求與 plan-only 邊界沒有縮減。未實作這個只要求規劃的 CLI。

## 驗證矩陣

| 項目 | 結果 | 直接證據與限制 |
| --- | --- | --- |
| Skill 官方 validator | PASS | 最終 SKILL.md：Skill is valid! |
| 研究報告 validator | PASS | 原研究報告：Report validation passed. |
| Plan-only 第一輪 | FAIL → R1 | [原計畫](task-harness-review-202610-evidence/plan/tasks.md)，顯式圖無循環但有驗收循環 |
| Plan-only 修正後新 agent | PASS | [新計畫](task-harness-review-202610-evidence/plan-fixed/tasks.md)，A 自帶必要驗證；原始碼及其他計畫未變 |
| 真實平行分派及整合 | PASS | [dispatch](task-harness-review-202610-evidence/parallel/evidence/dispatch.json)、[integration](task-harness-review-202610-evidence/parallel/evidence/integration.json)；兩個原生 worker 真實 handles、互斥檔案 ownership、coordinator 接受整合結果 |
| 過期證據續作 | PASS | [resume 結果](task-harness-review-202610-evidence/resume/evidence/verification.json)；原 done 現版失敗，修正 double 後原始 check.py 通過 |
| 未知副作用及缺少工具 | PASS | [續作清單](task-harness-review-202610-evidence/resume/tasks.md)；未重播 send.py；T2、T3 維持 blocked，沒有錯報整體完成 |
| 原三個 fixture 回歸 | PASS | 原 verify.py 及 verify_integration.py exit 0；這是歷史產物重驗，不是重新派工 |
| 封存後重跑 | PASS | [verification.json](task-harness-review-202610-evidence/verification.json)；保護檔案指紋、functional assertions 及最終 skill 比對通過 |
| 最終獨立複核 | PASS | [review-final.txt](task-harness-review-202610-evidence/review-final.txt)；R1 解除，Required 未解 0 |

平行 worker：`/root/test_harness_parallel/amounts_worker`、`/root/test_harness_parallel/labels_worker`。兩者先同時 running，完成後 coordinator 才接受各自成果並整合 receipt.py；最後都已 completed。只有 coordinator 寫入共享 tasks.md。

驗證器曾在 formatter 尚未實作時以 `NotImplementedError` 失敗，實作後成功，見 [negative-check.txt](task-harness-review-202610-evidence/negative-check.txt)。但自動產物檢查不會辨識所有語意問題：第一輪規劃的 R1 正是由獨立狀態推演發現，不能把 verify.py exit 0 當成完整行為驗收。

## 受測版本與覆蓋邊界

- 初始 skill SHA-256：`d07d527704445ecb4e1dd3a9279dc7c913d1a3b33d662e11887d41dc38084424`。
- 最終 skill SHA-256：`d64660c2e4aa67d33dd3d98c7fbe846d03254ccfb0e3b2697671eba7a44d7701`。
- 初始與最終完整 skill 都保存在 evidence 的 `skill/`、`skill-final/`。metadata 未變，skill 沒有 repo-root runtime references 或強制其他 skill。
- 平行與 resume 前向測試使用初始版；本次唯一修改是拆分規則，受影響的 plan-only 在最終版重新做 fresh-agent 測試。沒有把舊版其他情境宣稱為最終版全部重新派工。
- 現有結果驗證小型本機 fixture；未驗證 live-service idempotency、worker crash/takeover、取消、budget exhaustion、shared-resource contention、跨 worktree 整合或長時間運行。兩個 disjoint workers 同時執行不等於併發壓力或衝突測試。
- 工具／授權不足時維持 blocked 是 resume 情境的正確結果，並非本次 skill 驗收未完成。
- 未安裝 skill、未 commit/push 或發布。保留其他未提交工作。

## 可重跑命令

在 `/Users/kengp3/Workspaces/mine/simple-skills` 執行：

```sh
PYTHONPATH=/Users/kengp3/.cache/uv/archive-v0/s3OOPVWJ0Hw7jhwA0lvuR/lib/python3.13/site-packages python3 /Users/kengp3/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-harness
python3 /Users/kengp3/.codex/skills/deep-research/scripts/validate_research_report.py docs/research/task-harness-202610.research.md
python3 docs/research/task-harness-review-202610-evidence/verify.py skills/task-harness
python3 docs/research/task-harness-202610-evidence/verify.py
python3 -B docs/research/task-harness-202610-evidence/execute/evidence/verify_integration.py
git diff --check
```

第一條使用本機既有 PyYAML cache，只屬作者 validator 的環境需求；不屬於 skill runtime dependency。封存重驗只執行本機 assertion，不重新派工；重做 forward test 需依 [request 與固定驗收條件](task-harness-review-202610-evidence/requests-and-criteria.json) 建立乾淨原始 fixture，再交由獨立 agent 執行，不可把已完成產物當起始狀態。

## DoD 核對

1. Plan-only、execute、resume 的授權界線：指令審查與三種行為驗證成立。
2. 任務 ID、scope、owner、依賴、驗收、狀態：保留；修正驗收循環並確認新計畫可達完成。
3. 分派、整合、失敗及續作：本次有實際證據；重試／取消等未測情境明列邊界，未宣稱硬保證。
4. 獨立使用：最小兩檔 package，可由 tmp 中單獨的 SKILL.md 驅動；無跨 repo runtime 依賴。
5. 官方 validator、隔離測試與保存證據：通過；自動檢查與人工決策複核分開記錄。
