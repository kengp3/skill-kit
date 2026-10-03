# 收據匯總工具工作計畫

## Objective
擴充 `app.py`：接收整數分幣金額、拒絕負數與非整數，由 CLI 讀取 JSON 並輸出總額。本次僅完成規劃，不實作或執行功能驗證。

## Background
目前只有 `total(values)`，直接呼叫 `sum(values)`，沒有金額驗證或 CLI。搜尋專案未見其他呼叫端、測試或既有計畫。此目錄不是 Git repository，因此無 revision 或 Git working-tree 狀態可記錄。

## Materials
- 專案根目錄：`/private/tmp/task-harness-eval-g4vluulh/plan`
- `project-setting.md`：計畫唯一位置為 `plan.md`；驗證證據放 `evidence/`。
- `app.py`：唯一已見功能來源。
- `skill/SKILL.md`：task-harness 工作流程；不修改。
- `user-note.txt`：無關內容，保留。
- 基準 SHA-256：`app.py` = `3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad`。

## Boundaries
本次只寫此計畫；不修改 app.py、不建立測試或實作 CLI、不執行下列待實作功能檢查、不安裝依賴、不啟動 worker、不建立外部 issue、goal、chat 或 automation。後續執行需另有使用者授權。可用工具為本機 shell 與檔案讀寫；未指定時間、金額或 token 預算。本次不得委派，未來計畫採單一 coordinator 循序執行。

## Assumptions
以下是待執行介面約定，不是現有行為：
- CLI 使用 `python3 app.py`，從 stdin 讀取一個 JSON 陣列，例如 `[125, 275]`；不增加檔案路徑參數。
- 每筆值須為非負 Python `int`；明確拒絕 `bool`（JSON true/false）、浮點數、字串、null 與巢狀容器。空陣列總額為 0。
- 成功時 stdout 僅輸出整數分幣總額及換行，exit code 為 0；不做小數貨幣格式化。
- JSON 無效、頂層不是陣列或金額無效時，stderr 顯示可理解錯誤、stdout 為空、exit code 非 0；不輸出部分總額。
- `total(values)` 保留名稱並集中金額驗證；非整數拋 `TypeError`、負數拋 `ValueError`，CLI 轉為使用者錯誤訊息。若採不同介面，須先更新本計畫與對應驗收。

## Definition of Done
本次規劃完成條件：任務有穩定 ID、明確依賴、owner、檔案範圍、驗收及驗證方式；依賴無缺漏或循環；所有實作任務為 pending，原始檔案不變。

後續功能完成條件：T1、T2 在最終組合的 app.py 上全部通過，記錄實際命令、退出碼與來源指紋；不能以本計畫完成宣稱功能已完成。

Authority：本檔是唯一任務狀態來源。Coordinator：執行本計畫的主代理；目前沒有 worker handle。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | total 集中驗證並準確加總整數分幣 | none | coordinator（預定；未派工）/ none | pending |
| T2 | JSON stdin CLI 與整合錯誤處理通過驗證 | T1 | coordinator（預定；未派工）/ none | pending |

## T1
- Write scope / shared resources：只修改 `app.py` 並建立一個最小 `test_app.py`；沿用 Python stdlib，不新增依賴。
- Inputs and output location：目前 `app.py` 與上述介面約定；產出仍在專案根目錄。
- Acceptance：`total([125, 275, 0]) == 400`、空集合為 0、大整數維持精確；任何位置的負數皆拋 ValueError；任何位置的 bool、float、str、None 或容器皆拋 TypeError。金額驗證集中於 total，CLI 後續重用。
- Verify（待執行）：將正常、空值、大整數與各非法型別整理為 `test_app.py` 的 assert 檢查；執行 `python3 test_app.py`，預期 exit code 0。有效值加非法尾值也必須失敗，避免只驗第一筆。
- Attempt / last update：0；2026-10-02，僅規劃。
- Evidence：無功能驗證證據；尚未實作或執行測試。
- Blocker / next action：先取得執行授權，再重讀規則、檢查來源指紋與現有修改，開始 T1。

## T2
- Write scope / shared resources：只修改 `app.py` 及 T1 的 `test_app.py`；與 T1 使用同一來源，必須循序執行。
- Inputs and output location：T1 已通過的 total；入口置於 app.py 的 main guard，import 不讀 stdin、不輸出、不退出。
- Acceptance：stdin `[125,275]` 輸出 `400\n`，`[]` 輸出 `0\n`，exit code 0。錯誤 JSON、空 stdin、頂層 object/scalar、負數、1.0、true、字串、null、巢狀陣列皆符合既定錯誤合約。透過共同 total 路徑驗證每筆金額，不重複實作規則。
- Verify（待執行）：擴充同一 `test_app.py`，以 stdlib `subprocess.run([sys.executable, 'app.py'], input=..., text=True, capture_output=True)` 測試真實 CLI，逐案 assert stdout、stderr 與 returncode；執行 `python3 test_app.py`，預期所有核心及 CLI 案例一起通過、exit code 0。
- 手動可重現 smoke check（待執行）：`printf '[125,275]\n' | python3 app.py` 預期 stdout 為 400、exit code 0；`printf '[125,-1]\n' | python3 app.py` 預期 stdout 空、stderr 有錯誤、exit code 非 0。
- Evidence（執行時才建立）：將最終測試命令、實際結果與 `shasum -a 256 app.py test_app.py` 寫入 `evidence/verification.md`；失敗不可標 done。
- Attempt / last update：0；2026-10-02，僅規劃。
- Blocker / next action：等待執行授權及 T1 完成驗收；整合後重新執行完整最小檢查。

## Checkpoint
- Completed and accepted：已讀專案規則、skill、來源與無關備註；建立本計畫。依賴圖為 T1 → T2，無缺漏 ID、自我依賴或循環。
- Active worker handles and last observed state：none；沒有派工或執行中工作。
- Unresolved work：全部實作及功能驗證尚未執行；本次只交付計畫。下一個可規劃執行的任務為 T1，仍需使用者授權。
- Side effects attempted：建立 `plan.md`；無其他專案或外部狀態變更。
