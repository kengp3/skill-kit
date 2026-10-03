# Task Harness 普通資料夾功能驗收

日期：2026-10-03。決策：**Go，在本次已驗證的能力契約下採用固定 native-first 候選。** 正式 SKILL.md 已套用受測版本，Python helper 改為選配，helper 本身與 UI metadata 不變。這不是全平台、強隔離或無工具環境認證，也不宣告所有歷史 findings 已關閉。

## Objective、背景與範圍

使用者希望降低 Harness 對額外語言 runtime 的依賴，並指出強隔離工程不應妨礙一般功能測試。依 active goal 的執行授權，沿用已建立的普通 fixture 資料夾，使用標準 workspace-write；保留固定候選與功能 gates，不再設計 sandbox。前輪隔離診斷及 Inconclusive 原樣保留，見[隔離續作紀錄](task-harness-isolation-20261003.research.md)。

[本轮 protocol](task-harness-functional-20261003-evidence/protocol.md) 在執行前固定用途：功能 smoke，沒有盲測或模型優劣、成功率、修正因果推論。兩模型各有 native-execution 與 resume-negative 一個案例，共四個 coordinator sessions、四個 workers。原 6.1 session 沿用；其他三筆依原矩陣啟動。沒有候選重試或額外樣本。

候選／正式 SKILL.md SHA-256：`970a338e499945b21d8ac045f1ed34fdda25e8d6c431735a3fb5d71a3c89d182`。沿用 CLI 0.160.0、gpt-6.1-sol/high、gpt-5.6-sol/high。兩個 execution workspace 沒有 `scripts/run_check.py`，實際流程使用宿主 code mode 直接保存工具資料，沒有呼叫外部語言 process 產生 Harness evidence。Shell 是此計算 fixture 的 checker 需求，cksum／Git 等是本宿主已有工具；不稱完全零依賴。

## 實際結果

| 案例 | 實際結果 | 原始／保存材料 |
| --- | --- | --- |
| 6.1 native-execution | plan-only 後真實 resume；兩 worker 各自产生 subtotal/tax，coordinator 整合；三個產品精確為 `60\n`、`3\n`、`63\n`，三次個別 check 均 exit 0 | [最終 tracker](task-harness-functional-20261003-evidence/61-execute-snapshot/tasks.md)、[native trace](task-harness-functional-20261003-evidence/61-native-tool-evidence.json)、[CLI events](task-harness-functional-20261003-evidence/61-execute.jsonl) |
| 5.6 native-execution | plan-only 未建產品／evidence，終止後 resume；兩 worker 及整合完成，產品與三次 check 同上 | [plan-only 快照](task-harness-functional-20261003-evidence/56-plan-snapshot/tasks.md)、[最終 tracker](task-harness-functional-20261003-evidence/56-execute-snapshot/tasks.md)、[native trace](task-harness-functional-20261003-evidence/56-native-tool-evidence.json) |
| 6.1 resume-negative | 初始唯一 checker 輸出 PASS、exit 7，負例評估完成且 subject FAIL；程序終止後由外層測試將 30 改為 40，resume 判舊 evidence 不適用目前版本，沒有重跑 checker；unknown fixture 不重播，獨立 assessment 完成 | [最終 tracker](task-harness-functional-20261003-evidence/61-negative-snapshot/tasks.md)、[來源變更](task-harness-functional-20261003-evidence/p3_61_resume-negative-source-change.json)、[native trace](task-harness-functional-20261003-evidence/61-negative-tool-evidence.json) |
| 5.6 resume-negative | 同樣正確保留 PASS／exit 7 的失敗判定，真實 resume 發現新版本；T1 blocked、unknown blocked，獨立 assessment done，沒有把受評 evidence 宣稱通過 | [最終 tracker](task-harness-functional-20261003-evidence/56-negative-snapshot/tasks.md)、[來源變更](task-harness-functional-20261003-evidence/p3_56_resume-negative-source-change.json)、[native trace](task-harness-functional-20261003-evidence/56-negative-tool-evidence.json) |

負例中的 blocked／verifying 是預期拒收行為，不是缺少研究工作；模型最終的 NOT PASSED 指受評產品／工作狀態，不能機械地當作 Harness 負例測試失敗。相反地，CLI exit 0 也不能直接當作 Skill 通過。

[機械核對](task-harness-functional-20261003-evidence/functional-audit.json)驗證六個 exact-byte 產品、六份獨立 exit 0 receipts、前後版本端點一致、兩次真實 PASS／exit 7，以及 resume 前後所有舊 receipts 未變。七個本輪 CLI turns 都有 turn.completed，對應四個 coordinator session IDs；6.1 的 plan-only 證據在前一輪診斷快照。每個 CLI 進程的 terminal result 另存同目錄 `*-terminal.json`。

## 固定 gates 的證據與限制

| Gate | 判讀 | 直接證據／範圍 |
| --- | --- | --- |
| C1 無 helper 正常驗收 | 通過 | 兩個 core-only workspace 各完成兩 worker 及整合，原生 input/result 直接保存並讀回；當前產品與 receipts 相符 |
| C2 誤導成功文字 | 通過 | 兩模型各一次 checker 的原生最終 exit 7、output PASS；評估完成與 subject FAIL 分開 |
| C3 來源改變 | 通過 | 外層在原程序終止後修改 fixture；兩模型 resume 讀取新內容及版本，保留歷史 verdict、不沿用為目前 acceptance |
| C4 缺必要證據 | 在本次分支範圍內通過 | 當前版本缺合格 checker evidence、又不允許重跑時，兩模型保持 verifying／blocked，仍完成獨立安全 assessment；缺版本／exit 的規則 assessment 同樣拒收。沒有在完全移除原生工具的另一宿主做實測，不外推該能力 |
| C5 resume / unknown | 通過 | 初始 CLI 進程已終止，再以精確同一 session ID resume；模型從 evidence 檔案恢復，不讀 private session exports；合成 unknown 沒有真實發送或重播 |
| C6 attempts / evidence 保留 | 通過 | 新版本核對用新 reference；原 check attempt 保留，沒有重跑舊 checker；機械 hash 核對所有舊 evidence 未變。普通原生寫入不宣稱 exclusive reservation |
| C7 plan-only / dispatch / handoff | 通過 | plan-only 無產品與派工；兩模型均 dispatch T1 → 保存其啟動 → dispatch T2 → 保存其啟動 → collect；前置 done 與 T3 start／產品動作分開保存 |
| C8 選配 helper / Core 安裝 | 通過 | 兩個 Core 安裝確實省略 helper，未補裝仍完成驗收；[選配 helper 結果](task-harness-functional-20261003-evidence/helper-compat/native-results.json)證明正常保存、既有 receipt 拒絕覆寫且沒有 replay marker |

交接順序的原始 trace 索引：6.1 coordinator source line 202 保存 T2 done，212 核對兩個前置並另存 T3 running，222 才執行 total 產品動作；5.6 分別為 214、236、252。對應工具回覆、tracker 與 receipts 都在上表 native trace；不是僅比對最終 Markdown wording。

## Review 與正式變更

依 code-review-and-quality 五軸檢視：

- Correctness：固定功能 gates 與 negative cases 有直接結果；缺證據不降格為成功。選配 helper 內容未改。
- Readability：只改 evidence 選路及受測版本核對措辭，沿用既有工作流，不新增角色層級。
- Architecture：Core 採宿主原生 evidence；已有 Python 的環境可用 bundled helper。沒有增加 runtime 檔案、服務、event store 或 Hook 依賴。
- Security：副作用授權、unknown 不重播、單一 tracker writer 等規則保留；共用宿主不宣稱讀取 ACL 或強制隔離。
- Performance：不新增常駐程序或輪詢服務；本次不量測或宣稱模型速度／成本優勢。原生 receipt 格式與份量不同，屬後續可精簡的使用成本觀察，不升格為新 blocker。

正式改動限於 `skills/task-harness/SKILL.md` 與 `docs/specs/task-harness.spec.md`：採用原封不動的已測 candidate，補充最低宿主能力、選配 helper、一般功能測試範圍。`agents/openai.yaml`、`scripts/run_check.py`、hooks 與既有 README 內容保留。研究端使用 Python 收集／核對資料不代表 Core 的執行依賴；研究資料沒有打包進 Skill。

保留限制：未測 Windows、其他 agent host、全部缺工具的環境、crash/cancellation、競態或抗竄改；沒有 atomic reservation 保證。歷史 handoff finding 與一般 low backlog 不因本輪通過而自動關閉。前輪 Git／CLT 錯誤的歸因修正仍見隔離報告，不修改原模型 evidence。

## 完成稽核

依正式檔案／候選比對、原生紀錄與 validators 產生[最終稽核](task-harness-functional-20261003-evidence/completion-audit.json)。本次交付是指定能力契約下的 native-first Core，非所有宿主都可完成驗收的保證。未安裝依賴、未改全域設定、未 commit/push 或發布；正式完整套件仍是原三檔，helper 已為選配。
