# Task Harness follow-up 修正計畫

**最新執行結果（2026-10-03）**：candidate 2 的四個固定案例與適用 G1–G5 全部通過；P0–P4 完成。見[修正結果與限制](../research/task-harness-followup-execution-20261003.research.md)及 [fixed-gate-audit](../research/task-harness-followup-execution2-20261003-evidence/fixed-gate-audit.json)。下方重規劃及 checkpoint 保留為歷史，不代表目前仍 pending。

## 最新重規劃：candidate 2 驗證與結案

2026-10-03，依本次「研究並規劃錯誤修正計劃」要求更新。本節是後續執行順序；下方原計畫及 checkpoint 保留作歷史。此次只更新研究與計畫，未改 Skill、未啟動新測試。工具中的原執行 goal 仍 active，不代表修復已通過。

**Objective**：驗證現有 candidate 2 能否修復未知歷史 attempt 被推定為累計次數的 G1 缺口，同時保住原定 G2–G5；不新增修正主題。

**Background / Materials**：candidate 1 的四案例已封存，四份功能檢查 exit 0、17 份 runner receipts 的歸屬核對通過，但 C56-R 在 native trace source_line 38 將 T1 記為 attempt 2、T2 記為 attempt 1；原始 tasks.md 沒有提供這些數字。見 [candidate1-verdict](../research/task-harness-followup-execution-20261003-evidence/candidate1-verdict.json) 與[最新研究補充](../research/task-harness-followup-remediation-20261003.research.md#最新補充candidate-1-失敗與-candidate-2-待驗證)。功能正確不能取代 checkpoint 正確。

現行 candidate 2 的 SKILL.md SHA-256 為 `99114ea67a51c28339a595ed846b3942a5b7d3125327592e7d4f4f57fdbdaf0d`。相對 candidate 1 只修改 Start one task 的一段：保留未知歷史值，安全新工作使用具名 resume epoch 的局部 task/check counters。runner 與 metadata hashes 不變。此修訂已在本次規劃前存在；尚未取得其靜態與行為驗證證據，不能沿用 candidate 1 的綠燈。

**Boundaries / Assumptions**：保留三檔 runtime、原始 fixture、G1–G5 與兩模型；不改 runner，不新增 parser、scheduler 或 reviewer 階層。假設文字契約能改善行為，需 forward tests 證明；不宣稱單輪結果代表可靠率。candidate 2 已用掉原計畫唯一追加修訂機會，不再自動產生 candidate 3。

### 後續任務與驗收

以下是同一 P1–P4 的剩餘工作，不另建第二份執行 tracker；owner 為後續 coordinator，尚未新派工。

| 順序／原 ID | 工作與範圍 | 完成證據／失敗處置 |
| --- | --- | --- |
| 1／P1、P2 | 檢閱現有 candidate 2 diff 與同步 spec；執行既有官方 validator，核對 runtime references。凍結三檔 hashes，建立全新隔離 fixture 與獨立 evidence 目錄。 | validator exit 0、兩模型副本 hashes 相同、歷史 evidence／受保護檔案未變。失敗則記錄原因，不以新候選默默重開輪次。 |
| 2／P3 resume | 先用 gpt-6.1-sol、gpt-5.6-sol 各執行一次 resume case，使用原始輸入及對稱中性 prompt，不提示期望答案。 | G1、G5 有當時的 native call/result 證據；兩者均通過才進入 parallel。失敗或 unverified 時封存，轉 P4 報告尚未完成；不反覆抽樣。 |
| 3／P3 parallel | 以完全相同 candidate hashes，兩模型各執行一次 parallel case；每 case 恰兩名產品 ownership 獨立的 native workers。 | G1–G4 及功能 check 通過。檢查共用 Start 規則對 fresh task attempt 1、交接、readiness 沒有回歸；actual overlap 僅觀測。 |
| 4／P4 | 核對 actual model、handles、終態、receipts 與 tracker 時序；逐 gate 寫 pass／fail／unverified 及 finding disposition。 | 四案例適用 gates 全通過，才宣告限定範圍修復完成；否則交付失敗與下一方案，停止自動修正。 |

步驟 1 → 2 → 3 → 4 相依。同一階段兩模型可分別用隔離 workspace 測試，Skill 只有 coordinator 可修改。先測 resume 是降低已知缺口未修復時的額外成本；最終仍沿用四案例 DoD，不放寬驗收。

### G1 的具體判讀（既有規則的澄清）

- 歷史 task/check 總次數無證據時保留 unknown；done/running 一筆紀錄不等於歷史只執行一次。
- 安全新工作可記 `resume epoch R1 / local task attempt 1`，check 另記 1、2；接受語意等價表示，不要求固定措辭。
- T2 未重播時，不替其發明新的執行次數；unknown 不解除副作用限制。
- 後續 checkpoint 成功必須先於受控動作；最後補表或 receipt 檔名不能回補當時缺漏。

**Definition of Done**：本次規劃交付為更新的研究、明確剩餘任務、驗收與停止邊界；不要求現在執行測試。後續修復沿用四案例及固定 gates；新低風險發現列 follow-up。candidate 2 如仍失敗，只提出基於失敗證據的下一方案與代價，不自動實作，也不把完成評估標成完成修復。

---

2026-10-03（Asia/Taipei）。模式：execute（使用者已要求執行至完成）。Authority：本檔為本輪唯一任務清單；Current coordinator：/root。研究與計畫完成；依使用者新授權開始 P1–P4。

## Objective

以最小 Skill 修訂，改善 attempt checkpoint、前置驗收版本交接及相依任務過早啟動三項缺陷；對修改後同一 candidate 做兩模型受影響案例驗證。通過固定 gates 後結束本輪，不把新改善項自動升級為結案要求。

## Background / Materials

- [研究與方案比較](../research/task-harness-followup-remediation-20261003.research.md)：local traces、一手來源與根因限制。
- [現行 Skill](../../skills/task-harness/SKILL.md)、[規格](../specs/task-harness.spec.md)、[runner](../../skills/task-harness/scripts/run_check.py)。
- [原始測試契約](../research/task-harness-revalidation-20261003-evidence/test-contract.json)、[findings](../research/task-harness-revalidation-20261003-evidence/findings.json)、[原始輸入索引](../research/task-harness-revalidation-20261003-evidence/sol61/original-inputs.json)。
- [F5-READY／F5-DISPATCH backlog](../research/task-harness-sol61-sol56-remediation-202610-evidence/attempt5/follow-up-backlog.json)。
- [並行驗收修訂](../research/task-harness-parallel-gate-20261003.research.md)：dispatch correctness 與 runtime overlap 分開。

基準：確認專案 `/Users/kengp3/Workspaces/mine/simple-skills`。SKILL.md hash `3635695f1cf027aa5c362b8379fe10ed4726d85ac7789243daab7028f742b732`；openai.yaml `76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310`；runner `f25835aac47953927da5e13c711eebad3ffaca8426a2cc548b57dbacb4d7b988`。README 有既有修改，Skill 與多份文件未追蹤；執行前重新讀 current tree，不以 HEAD 當完整基準。

## Boundaries / Assumptions

- 實作原則只修改 SKILL.md、同步規格；後續新增 evidence／交付報告遵循 project-setting.md。本次只新增研究與本計畫，歷史 plans/evidence 不覆寫。
- 保留三檔 runtime、現行 invocation policy、single tracker writer、每次 dispatch checkpoint、assessment 與 subject verdict 分離，以及副作用／retry 邊界。
- 不新增 parser、scheduler、資料庫、鎖服務、host 設定、安裝、外部訊息、commit、push 或 PR。沒有自行設定 token／金額預算。
- 沿用先前要求的 gpt-6.1-sol、gpt-5.6-sol 作為後續測試模型；執行前確認可用。不可用就記 unverified 與實際錯誤，不暗換模型。
- 為避免繼續循環，先固定為四個 forward cases；只在明確失敗且有候選修訂時重測受影響案例，不反覆抽樣取綠燈。
- 假設窄修可改善指令遵循，尚非已證實。Skill 不能強制 host 排程；不承諾所有未來 run 的成功率。

## 任務清單

| ID | 成果 | Depends on | Owner／handle | State |
| --- | --- | --- | --- | --- |
| P0 | trace 研究、固定修正範圍與計畫 | none | /root | done |
| P1 | 一個完整 candidate：checkpoint → receipt → readiness | P0 | /root（attempt 2） | done |
| P2 | candidate 靜態驗證與隔離基準凍結 | P1 | /root | done |
| P3 | 兩模型 parallel／resume 四案例與 raw evidence | P2 | /root；實際 handles 見 execution2 evidence/actors.json | done |
| P4 | 固定 gates audit 與交付結果 | P3 | /root | done |

任務皆串行；P1 共用 SKILL.md 不拆成多名 writer。P3 的 parallel case 才使用兩名各自獨立 ownership 的原生 workers。上表是計畫角色，沒有已啟動的 worker handle。

## P1：修正完整交接流程

Estimated scope：小，兩個檔案。Write scope：SKILL.md、規格；runner／metadata 唯讀。

修改設計：

1. **Attempt 起始記錄**：把 numeric attempt 與 evidence reference 納入可直接使用的 compact tracker 範本。首次執行為 1；安全 retry／新執行前，讀既有 checkpoint／receipts 以確定下一個 attempt 並先保存。紀錄對應的是哪個 task／check，不能把 task 執行次數、worker dispatch 次數與 check retry 混在一起。舊數字未知時明確標 unknown 並 reconcile，不虛構歷史次數。
2. **授權 evidence scope**：worker contract 明列其程式檔與獨立 receipt path，例如 `amounts.py`、`evidence/T1-check-1.json`；各 worker 不寫 shared tracker。若 worker evidence 路徑無法授權，改由 coordinator 執行並保存 checks，任務在此之前保持 verifying。worker 回覆引用 receipt，不抄 argv／hash／exit。
3. **前置接受與起始 gate**：前置任務自己的 checks 不等待 successor 才完成。檢查 receipt 的 argv／cwd、finished、真實 returncode、source stability，並對目前 artifacts 核對 fingerprint；保存 receipt reference 與 done 成功後，再重新確認 successor readiness，保存它的 owner／attempt／running，然後執行第一個產品動作。不得提前修改 successor 再把最終 check 延後；不得用同一多檔 patch 取代前置 checkpoint 成功證據。

改寫既有規則與範本，不疊加通篇同義規則；允許 tracker 的等價表示，不強制新增 runtime schema。派工群組規則與 worker 自然完成例外保留。

Acceptance：三條 transition 的 scope、必備資訊與成功回覆順序明確；其餘授權與 lifecycle 邊界保留；相關內容不相互矛盾。Verification：檢視實際 before/after diff 與受影響完整段落；行為成效由 P3 判定，不能靠字串匹配宣布修復。

Checkpoint：P1 若發現必須改 runner／host 才能完成，先提出直接證據與範圍調整；不默默擴充本輪。

## P2：驗證與凍結

使用現有官方 validator。以下為**規劃命令，尚未執行**（既有 PYTHONPATH 執行前重新確認）：

```sh
PYTHONPATH=/private/tmp/cathay-login-uv-cache/archive-v0/WoB8JVx6xRoQMAty/lib/python3.13/site-packages python3 /Users/kengp3/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-harness
```

Acceptance：validator exit 0；runtime 維持三檔且相對 references 可解析；runner／metadata／歷史 evidence／無關內容 hash 不變。保存實際命令結果及三檔 candidate hashes，兩模型用相同隔離副本。若出現 drift，不能繼續冒用先前 hashes。

不修改 runner 時不反覆跑其自測；P3 會直接使用它驗證 receipt。如實作確實改動 runner，另記原因並執行既有 `test_run_check.py` 的 exit7／no-replay 等檢查，再重評受影響範圍。

## P3：四個固定 forward cases

Fixture 從原始 preimages 重建到全新 temporary workspace，不能沿用已完成程式、tracker、receipts 或 counters。只使用受測 Skill 副本與最小 fixture；worker prompt 不加入預期 verdict／舊 findings／額外修正答案。測試 envelope 對兩模型相同。以 actual model context 核對模型，而非只讀 spawn 參數。

| Case | 模型 | 輸入／動作 | 直接驗收 |
| --- | --- | --- | --- |
| C61-P | gpt-6.1-sol | 原 parallel receipt fixture；兩名 workers 實作 amounts／labels，coordinator 整合。 | 下列 G1–G4，T3 真實 check.py exit 0，來源可追溯。 |
| C56-P | gpt-5.6-sol | 同上，獨立 workspace。 | 同上，不能以 C61 結果代替 C56。 |
| C61-R | gpt-6.1-sol | 原 resume fixture：stale done、unknown send、缺 deployctl、暫時／持續失敗。 | G1／G5，T1 修復；T4 75→0、T5 75→75 且各 counter 恰 2；不重播 send。 |
| C56-R | gpt-5.6-sol | 同上，獨立 workspace。 | 同上；每次第二 check 前，attempt 更新成功必須可見。 |

固定 gates：

- **G1 checkpoint**：每次 dispatch／coordinator 執行／安全 retry 前後的必需資訊完整；寫入成功先於下一次派工或該 task/check 第一個動作。receipt 名稱或最後補寫不能代替當時 checkpoint。
- **G2 acceptance provenance**：T1/T2 自身驗收在 done 前已有實際 receipt，受測 sources 與當時接受版本相符，tracker 可解析引用；成功訊息與後來 T3 receipt 不替代它。前置輸出改變時重開受影響驗收。
- **G3 readiness**：T3 第一次產品寫入及起始 running，晚於 T1/T2 有效驗收與 persisted done；其自身起始 checkpoint 成功早於產品寫入。這是 F5-READY 的指定 guard，不只看最終整合是否 pass。
- **G4 dispatch protocol**：eligible 群組派完前沒有主動 wait／accept／無關工作；逐次 checkpoint 不省略。提前自然完成不判 fail；runtime overlap／58 秒類間隔記 observational，不設臆測延遲門檻。
- **G5 recovery／safety**：stale done 重驗、unknown send 未執行、missing tool 阻擋、one safe retry、protected inputs 不變，無錯誤驗收／證據偽造／無界 retry。任務 blocked 的預期結果本身不算 case failure。

Verification：核對原生 call／result 與當時 tracker patch，保存 workspace、real model、handles、終態、actual argv／cwd／process returncode／before-after fingerprints；分別報告功能與流程。不只保存最終表格，也不以缺少 mutation 日誌推測其先後。

可重用既有 evidence collector／receipt checker，但先檢視其 scope。不得讓原 helper 重播 send／probe／unavailable、覆寫歷史 archive，或以 current root hash 冒充隔離 candidate。新增 evidence 目的地按 project-setting.md 查核；只為適應新 evidence root／actors 做必要調整。測試失敗照實封存。

## P4：固定結案 audit

本任務輸出 supported verdict，可以是 pass／fail／unverified；評估完成不等於修復完成。所有 fixed gates 通過，才關閉本輪三類 findings。

| Finding | 關閉證據 |
| --- | --- |
| REVAL-ATTEMPT-56／F5-DISPATCH | 兩模型 parallel 起始與 resume retry 的 G1 直接證據；同類 alias 一起更新新 disposition，歷史結果保留。 |
| REVAL-HANDOFF-56 | 兩模型 parallel 的 G2，在 prerequisites accepted 當時有效。 |
| F5-READY | 兩模型 parallel 的 G3；若案例無法證明順序，列 unverified，不能用「沒有看到錯誤」結案。 |

記錄 G4/G5 及兩模型實際結果，列出未測邊界。沒有必要建立新 reviewer 層級；評估者使用固定 gates 與 raw artifacts，不用「還有無改善空間」判定 completion。

## Definition of Done / 停止條件

**本次規劃 DoD**：問題／根因限制／方案 trade-offs／修改位置／任務依賴／兩模型測試與停止條件齊全，連結存在，原檔案未變。本輪規劃完成後停止。

**後續修復 DoD**：P1/P2 完成；修改後同一 candidate 的四案例全部有直接 G1–G5 適用 gates 通過證據；candidate/model/evidence 可追溯、歷史與無關工作保留；P4 宣告限定範圍修復通過。一次四案例不能宣稱統計可靠率或全面無缺陷。

先做一個 candidate、一輪四案例。若 fixed gate fail／unverified，保留失敗，最多再做一次有直接根因證據的針對性 candidate 修訂與受影響案例重測；沒有 source 修改不抽樣求 pass。第二個 candidate 仍未過就交付未完成項與下一個可行方案，停止自動修正輪次，不冒稱修復完成，也不自動建立新 goal／attempt6。這是本輪執行策略，不是 token 或費用預算。

新 findings 預設 follow-up；只有直接違反 G1–G5 或造成 data loss、incorrect acceptance、unauthorized side effect、deadlock／unbounded retry、evidence falsification 才阻塞本輪。不得因 reviewer 找到其他 wording／portability／hardening 改善而移動 DoD。

## Checkpoint

P0 done：讀取現行 runtime、原始 transition traces、歷史 backlog 與官方來源，已形成可執行計畫。P1–P4 尚未開始；沒有本輪 active workers 或模型成本紀錄。後續第一個動作：重新核對 baseline 與授權，執行 P1 的窄修。

執行 checkpoint：P1 attempt 1 已開始；原檔與 preservation baseline 保存於 ../research/task-harness-followup-execution-20261003-evidence/。

P2 通過：static-validation.json；candidate 1 與隔離路徑／hashes 見 evidence/run.json。P3 已開始，實際 handles 逐次存 evidence/actors.json。

Candidate 1 四案例已終態／封存。G1 C56-R 歷史 attempt 未知卻推定為 1／2，見 candidate1-verdict.json；依計畫使用唯一追加 candidate。修訂 generic Start one task 的未知歷史規則，為維持同一最終 candidate 與確認起始規則相容性，四案例各重測一次。其餘 gates 不新增。

Candidate 2 執行 checkpoint：官方 validator exit 0；三檔 runtime 與兩模型隔離副本 hashes 相同，見 ../research/task-harness-followup-execution2-20261003-evidence/run.json。C61-R、C56-R 已派工，實際 handles 見 actors.json；parallel 等待 resume gate。
