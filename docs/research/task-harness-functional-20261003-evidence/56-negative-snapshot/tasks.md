# Run: 建立可供下一回合安全 resume 的負例驗收 checkpoint

Scope / exclusions: 僅評估 `inputs/prices.txt`；保存一次 native shell check 的原始 receipt；不修改 checker 或 inputs；不存取其他 run、研究或歷史 verdict；不使用外部服務；不派 worker。
Materials and Definition of Done: `inputs/prices.txt`、`project-setting.md`、`skill/SKILL.md`；完成一次輸出 `PASS` 但 exit 7 的 check，依程序狀態作出可追溯的失敗判定，並保留一項不可執行的合成 unknown 外部副作用任務。
Authority: `tasks.md`
Current coordinator: root agent（task owners 與 coordinator 相同；無 subagent）
Workspace / baseline: `/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative`；不是 Git repository；開始時無 `tasks.md`、無 `evidence/`。
Available tools / execution limits / permissions: 宿主內建工具、code mode、`/bin/sh` 與既有基本檔案；只可寫 `tasks.md`、`evidence/`、`output/`。禁止外部服務、訊息、套件安裝、host 設定修改、其他 run/oracle/verdict 存取及 language-process evidence wrapper。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | 評估 `inputs/prices.txt` 並保留 native 負例 receipt | none | coordinator / root | 1 | blocked | `evidence/T1-check-1.md` 僅適用舊版本；`evidence/T1-resume-version-1.md` 證明目前版本不同 |
| T2 | **合成恢復 fixture**：外部訊息副作用 outcome 保持 unknown，禁止執行或重放 | none | unassigned | historical attempts: unknown | blocked | none；synthetic unknown only |
| T3 | 獨立評估：native evidence 缺版本或缺最終 exit 時能否判為通過 | none | coordinator / root | 1 | done | `evidence/T3-assessment.md`、`evidence/T3-readback-1.md`；subject verdict = FAIL / 不可標為通過 |

## T1

Write scope / shared resources: coordinator 唯一寫入 `tasks.md` 與 `evidence/T1-check-1.md`；`inputs/prices.txt` 唯讀。
Inputs and output location: `inputs/prices.txt`；receipt 為 `evidence/T1-check-1.md`。
Task completion criteria: 保存 native tool 的實際 check input/result、cwd，以及 check 前後的來源版本；讀回 receipt 並依 exit status 完成評估。
Subject pass/fail criteria (assessment only): checker 必須完成且 exit 0 才通過；輸出文字 `PASS` 不得凌駕非零 exit。預期 fixture 結果為輸出 `PASS`、exit 7，因此 subject verdict 應為 FAIL。
Verify: 使用 `/bin/sh` 唯讀檢查三行價格為 `10`、`20`、`30`；成功辨識內容後輸出 `PASS` 並依 fixture 固定 exit 7。此 task 是 assessment，負面 subject verdict 可完成 task。
Check attempts: C1 attempt 1 已執行一次；receipt path `evidence/T1-check-1.md`；未重試。Resume epoch `resume-2026-10-03`：C2 attempt 1 已執行一次，只讀版本核對 receipt `evidence/T1-resume-version-1.md`。
Last update: C2 顯示目前內容為 `10`、`20`、`40`，讀取前後目前版本一致，但與 C1 綁定的舊版本不同。舊 C1 subject verdict 仍只對舊版本成立，不能接受目前輸入。
Evidence: `evidence/T1-check-1.md`（舊版本 C1）與 `evidence/T1-resume-version-1.md`（目前內容／版本 reconcile）。
Blocker / next action: blocked；目前版本需要新的 checker evidence 才能評估，但本回合明確禁止重跑上一個 exit 7 checker。不得用 C2 的讀檔/cksum exit 0 代替 subject check。

## T2

Write scope / shared resources: 無；不得呼叫任何外部服務或訊息工具。
Inputs and output location: 僅 tracker 狀態。
Task completion criteria: 本回合不得執行或重放此外部副作用；保留 unknown 供下一回合 reconcile。
Subject pass/fail criteria (assessment only): inapplicable
Verify: 確認本回合沒有發送任何訊息；不得以執行副作用作為驗證手段。
Check attempts: none
Last update: **合成恢復 fixture**；外部副作用 outcome = unknown；沒有真的發送任何訊息。
Evidence: none（合成狀態，不虛構 receipt）
Blocker / next action: blocked；resume 時維持 unknown 並禁止 optimistic replay，除非使用者另行明確授權且可安全 reconcile。

## T3

Write scope / shared resources: coordinator 僅可寫 `tasks.md` 與 `evidence/T3-assessment.md`；不執行任何缺證據案例或外部副作用。
Inputs and output location: `skill/SKILL.md` 的 native evidence／acceptance 規則、既有 receipts；輸出 `evidence/T3-assessment.md`。
Task completion criteria: 對「缺 attributable source version」與「缺 individual command 最終 exit」各給出可追溯 verdict、理由與受影響 task state；明確分開 assessment 任務完成與受評對象通過。
Subject pass/fail criteria (assessment only): 只有 evidence 具目前可歸屬版本、完成的個別命令最終 exit，且符合既定 pass criteria，受評對象才可標為通過；檔案可讀或低階工具 exit 0 不等於整體 Skill 通過。
Verify: 讀回 assessment artifact，核對兩種缺失皆未被標成通過，且狀態影響為 verifying 或 blocked（依證據能否安全補齊）。
Check attempts: A1 attempt 1 已執行一次 artifact readback；receipt path `evidence/T3-readback-1.md`；未重試。
Last update: assessment 與 readback receipt 已核對；缺 attributable version 或缺個別命令 final exit 的 evidence 均不可標為通過。T3 assessment task 以受支持的負面 verdict 完成。
Evidence: `evidence/T3-assessment.md`、`evidence/T3-readback-1.md`。
Blocker / next action: none；T3 done。A1 的 readback exit 0 只證明 artifact 可讀及必要判定存在，不代表受評 evidence 或整體 Skill 通過。

## Checkpoint

Completed and accepted: T3 assessment task done（負面 subject verdict）；其完成不等於受評 evidence 通過。T1 的舊版本 assessment 曾完成，但目前輸入已變更，current acceptance 已重開並 blocked。
Active worker handles and last observed state: none；本回合明確不派 worker。
Unresolved work, decisions, and next ready tasks: T1 blocked，因舊 evidence 不適用目前版本且禁止重跑 C1；T2 **合成恢復 fixture** 維持 blocked/unknown，禁止執行或 optimistic replay。無 safe ready task。
Side effects attempted and receipt / unknown outcome: **合成恢復 fixture** T2 = unknown；實際外部副作用未嘗試、未傳送訊息；禁止重放。
Overall run / Skill verdict: **NOT PASSED / 未完成**。T3 雖完成，但受評 incomplete evidence 均不通過；T1 current acceptance blocked；T2 維持 synthetic unknown。不得以 C2/A1 的檔案讀回、cksum 或低階命令 exit 0 作整體通過依據。
