# Task Harness remediation 獨立複核

日期：2026-10-02。Reviewer：`/root/remediation_audit`。結論：OBS-01、GAP-01、GAP-02、GAP-03 在本輪明定的測試範圍內均可 closed；沒有阻止這四項修正結案的 finding。GAP-02 的 closed 僅限已識別 actors 的完整原生 tool trace，不代表 OS 全域寫入者排除證明。續作 fixture 的 T2、T3、T5 正確保持 blocked，不能稱該 fixture 全部工作已完成。

## 依據與獨立重驗

先讀取根目錄 `project-setting.md`；本文件沿用 remediation plan 明列、父任務指定的 evidence 目錄。確認目標及父目錄没有符號連結、檔案先前不存在，未修改 skill、fixtures 或 traces。

讀取本輪需求、baseline、original-inputs、三份 tasks.md、舊 findings、最終 skill、前版 skill、verifier 與五份 native trace。直接開啟各 trace 的 `source_file` 指向的原始 session JSONL，核對 session_meta identity、每筆原始行 SHA-256、source_line 與 payload 投影；五份都吻合。另將原始 session 所有四種 tool call/result 類型與投影逐筆比較：沒有遺漏 tool event。共 92 筆事件（plan 12、parallel coordinator 42、resume 22、兩 worker 各 8）。此為本次直接核對，不依賴 exporter 自述。

執行 `python3 -B docs/research/task-harness-remediation-202610-evidence/verify.py skills/task-harness`：exit 0，`failures: []`；parallel 與 resume 的安全 check.py 均通過，受保護輸入與最終 skill copy 一致。沒有重播 probe.py、unavailable.py 或 send.py。歷史 SHA manifest 134 份檔案重新計算均吻合。最終 SKILL SHA-256：`948713f0c0720334b7c4ab355a78c11c162a4a14a19b683289a37e14abeec5be`。

## 四項判定

| ID | 判定 | 直接證據與範圍 |
| --- | --- | --- |
| OBS-01 | closed | plan/tasks.md 保留 current planning agent、實際 workspace、app.py 與原 tasks.md 指紋、無 Git 的事實、shell/Python 工具與權限。實作 T1 仍 pending/unassigned。原始 plan trace 只有讀取與 tasks.md 修改，沒有 CLI 實作或執行。 |
| GAP-01 | closed | parallel 原始 call `call_au3X7UdEuNsXUBAQ0b4Gxdke`，source lines 80→82，2026-10-02T10:32:00.947Z 的 list_agents 查詢回應同時列出 amounts_helper、labels_helper 為 running。兩者均有先前成功 spawn 回應及獨立 session_meta，不靠整理後 overlap.json 自證。 |
| GAP-02 | closed，bounded tool-trace | parallel 四次 tasks.md 寫入全部出自 coordinator 身分；每次有 call/result、patch 前像／後像與讀回，worker 全部工具事件沒有 tracker 寫入。完整順序如下表。未推論未觀測的 OS 程序、其他 session 或工具外的寫入。 |
| GAP-03 | closed | plan/tasks.md 明列 `python app.py "" 10` 須非零退出且不印成功收據，另含有效姓名/總額、非整數、缺金額、負數。只規劃未執行。這次非空姓名被明列為需求，故證明此明確契約下的產物改善，不能宣稱單次結果隔離證明兩句 skill 修改的因果效果。 |

## Parallel 寫入與驗收順序

下列 source lines 均指 [coordinator trace](native-traces/remediation_parallel.json) 保存的原始 session 行號。四個 patch 的 result 都為成功，後續讀回與 patch 相符。

| source call→result | call_id | tasks.md 變更 | 前後證據 |
| --- | --- | --- | --- |
| 52→55 | call_WiYDGMaOrXTw6G86pCVlBTHx | 不存在 → T1/T2/T3 pending | 33 的查詢及結果確認不存在；59 查詢讀回新檔 |
| 93→96 | call_TySoEl9gIYYZcG86W7rYmSM4 | T1/T2 pending → running，填入真實 handles；T3 保持 pending | 68→71、74→77 為成功 spawn；80→82 為原生 overlap；98 查詢讀回 |
| 131→134 | call_GrXAVOBzk0BoLfuI4iBGOB5r | T1/T2 running → done；T3 pending → running | coordinator 112→116 及 122→125 各自讀取 helper、取 hash 並通過直接 assertions；136 查詢讀回 |
| 165→168 | call_hwY8tnnlGpZCjiWjEgb2J0vE | T3 running → done | 143→146 修改 receipt.py；150→154 最終 check.py exit 0；170 查詢讀回 |

其餘 coordinator 寫入完整盤點：86→89 僅新增 evidence/overlap.json；143→146 僅更新 receipt.py；158→161 僅新增 evidence/check.txt。最初 17→19 為 JavaScript syntax error，未執行其工具呼叫，後續修正讀取後才建立 tracker；沒有被當成成功派工或驗收。

[amounts worker trace](native-traces/remediation_parallel--amounts_helper.json) 的 42→45 僅改 amounts.py；47→50 assertions exit 0、指紋吻合。[labels worker trace](native-traces/remediation_parallel--labels_helper.json) 的 42→45 僅改 labels.py；49→53 assertions exit 0、指紋吻合。兩者沒有共享 tasks.md 寫入、額外派工或 source scope 擴張。Python imports 會產生各自模組的 __pycache__，本輪沒有相同來源模組的並行寫入衝突。

T1/T2 無前置依賴且 source inputs 已存在；T3 直到 coordinator 接受兩個 helper 的直接 assertions 後才開始。雖 helper 的 Verify 文字也列 final check.py，實际流程將它用作後續整合檢查，沒有要求 T1/T2 等待 T3 才能完成，未發生 acceptance deadlock。狀態直接由 running→done 不構成錯誤：直接驗收已完成，verifying 並非必經停留狀態。

## Plan-only 與 resume

Plan 原 A↔B cycle 與缺少 X 的 C 被重組為一個含實作及驗證的 T1，無缺失或循環依賴。原 app.py、other-plan.md、user-note.txt 均保留。第一次 delete/add patch 被工具拒絕（48→50）；第二次 update patch 成功（54→57），後續讀回，不能把第一次失敗算成已完成寫入。

[Resume trace](native-traces/remediation_resume.json) 直接顯示讀取舊 done 與當前 `value+1`、修正為 `2 * value`、安全 checker 通過；不是採信舊 PASS。send.py 只被讀取，沒有執行；本地空 deliveries.txt 未被當成 remote receipt。deployctl 查無路徑，沒有安裝或杜撰驗證。54→59 執行兩個安全服務檢查皆 exit 75，63→67 讀取 counters 為 1；71→75 唯一重試，probe 成功、unavailable 再次 75；79→83 counters 均為 2。沒有第三次盲重試。最終 T1/T4 done、T2/T3/T5 blocked 與證據相符。resume 的初次 tracker patch 也被拒絕，後續修正成功，未掩蓋工具失敗。

## 修改幅度與剩餘限制

SKILL.before.md 與最終 SKILL.md 只有兩處既有段落變更：最低交接資訊、逐項 acceptance/check 對應。metadata 與 agents/openai.yaml 未改；skill 目錄只有入口及既有 agents metadata，未引用 evidence verifier/exporter 為執行依賴，沒有新增 runtime 套件。官方 validator 通過紀錄存在 official-checks.json；本 review 的獨立重驗為 artifact verifier、hash 與原始 trace 核對，沒有把官方 validator 再執行一次。

沒有新增阻擋 finding。兩點產物精確度可在未來沿用時改善，不影響原四項驗收：plan 使用「current planning agent」而非穩定 actor handle；它另提及零金額有效，但具體例子沒有單列零金額。它們限制交接及邊界覆蓋的細緻程度，不能據此宣稱所有可能輸入都已覆蓋。Parallel 的 native running overlap 證明生命週期重疊，不證明 CPU/GPU 同時運算、速度提升、壓力容量或所有模型的行為保證。
