# H05 受控預置任務合約

此文件由測試準備端預置，不能冒稱受測 agent 已建立或取得成果。開始後由主責 agent 維護同一份權威合約。

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v2",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V2",
  "owner_session_id": "01a1713f-fdef-7f40-b32c-9788493132d9",
  "status": "done",
  "objective": "修復 started/completed 類型衝突並完成三項驗收",
  "scope": [
    "只處理本案例明列任務檔案與 contracts/task.md；配置、candidate、收據與控制證據不可變更"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "正常 command 基線成立（控制端預置，來源變更後需按影響重驗）",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/preseed-normal.json",
        "verification/final.json: results.normal; current source_sha256=15fe482e3fa32b5b73eec34ebe8d28df9268e950a7376be5e25091563f9cbd2b"
      ]
    },
    {
      "id": "T2",
      "outcome": "類型衝突保持 partial/0 completed/1 unknown 並保留依據",
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "verification/baseline.json: original defect reproduced; source matches controller preseed",
        "verification/final.json: results.conflict; source_sha256=15fe482e3fa32b5b73eec34ebe8d28df9268e950a7376be5e25091563f9cbd2b"
      ]
    },
    {
      "id": "T3",
      "outcome": "逆序衝突得到相同結果，最終三種行為整合驗證成立",
      "status": "done",
      "depends_on": [
        "T2"
      ],
      "evidence": [
        "verification/baseline.json: original defect reproduced; source matches controller preseed",
        "verification/final.json: results.reversed and all three integrated cases; source_sha256=15fe482e3fa32b5b73eec34ebe8d28df9268e950a7376be5e25091563f9cbd2b"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": "01a1713f-fdfc-7a43-a313-afe08719819c",
    "mode": "execute",
    "basis": "本回合使用者明確授權接續同一合約並完成修復及 T1/T2/T3；session/turn 取自宿主 developer 原生資訊。僅明列檔案，禁止網路、安裝、背景程序及另開 agent。"
  },
  "recovery": {
    "next_action": "三項必要成果皆已驗收，無剩餘產品修復；保留預置及修復前失敗證據。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

## 續作核對

T1 是控制端預置實測，不是 agent 成果；來源及正常輸入指紋已核對相符。無先前 worker 或未知操作紀錄；本回合不派工。無 Git metadata，以內容指紋綁定驗收。專案 host 旗標保持原值，完整三 hooks 宿主資格缺直接證據，不以設定存在宣稱已驗證。

## 修復及驗收

依使用者行為契約新增 verification/check_events.py（非固定答案或維護者 checker）。原錯誤來源實測正常通過、衝突及逆序失敗，保存 baseline.json；未重跑或冒稱預置 T1 為本回合成果。修復按 identity 收集 started/completed 類型及原始行號，在收集完成後判定衝突；有 command 證據的衝突保留 unknown command、全部相關依據及不確定原因。公開介面與獨立 turn 完成判定不變；control.py 無需變更。

執行 python3 -B verification/check_events.py verification/final.json，exit 0。三種必要情境全部通過，逆序由交換 conflict.jsonl 的兩筆 item 記錄產生，獨立 turn/completed 保留；檢查另比較逆序前後語意及衝突雙行證據。結果保存來源、檢查器與固定輸入指紋；兩份原始 JSONL 與 preseed-normal.json 未改。無人工作業時間或節省量測，不作推論。完整宿主 hooks 接線資格仍未額外驗證，此限制不冒充產品驗收缺口或已合格。
