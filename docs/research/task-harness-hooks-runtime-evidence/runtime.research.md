# H01：任務合約 hook CLI 的離線驗證

## 範圍與結論

2026-10-25，以 Python 3.15.0 執行公開 subprocess stdin/stdout 測試。24 個測試通過；完整合成 fixture 亦通過。Python 3.10+ 是相容設計目標，未執行 Python 3.10 runtime。未安裝 plugin、修改全域／日常設定、呼叫模型或執行 Desktop trial。

已驗證 SessionStart 恢復提醒、UserPromptSubmit 最新授權提醒、Stop 有界補救，以及結構錯誤、未驗證資格、過期授權、討論／等待／停止、blocked／cancelled、unknown 操作不盲重送等拒絕路徑。done 語意矛盾仍保留補救機會，與缺欄位／錯誤型別的未就緒結果分開。

## 可重現命令

在 repo 根目錄執行：

```text
python3 -B -m unittest discover -s tests -p 'test_task_harness_hooks.py' -v
python3 -B docs/research/task-harness-hooks-runtime-evidence/fixture.py
```

fixture 可另傳 handler 絕對路徑作為第一參數。它自建及清除臨時專案，保存完整 config／contract，連續送入三事件與重複 Stop，再核對唯一收據及合約未變。所有資格 true 都是合成測試輸入，不能作為宿主資格證據。

## Red → green 證據

- Slice 1：先寫 SessionStart 公共 CLI 測試；handler 尚不存在時失敗，最小實作後 1 個通過。
- Slice 2：加入 Stop、授權及額度測試；缺行為時失敗，實作後 7 個通過。
- Slice 3：加入 schema、依賴、重複綁定、JSON、上限與路徑邊界；原簡版出現預期失敗與 FIFO timeout，補強後 17 個通過。
- Slice 4：加入並行、失敗收據、發現邊界與 CLI 參數錯誤；最後一項顯示 argparse 的預設 exit 2 問題，修正後 23 個通過。
- Slice 5：部分宿主資格可提供上下文時，仍須明示整體未就緒；新測試先失敗，補上 systemMessage 後 24 個通過。Stop 仍要求三項資格全數合格。

實際 stdout／stderr 與 exit code 保存於 [tdd-cli-results.json](tdd-cli-results.json)；較長 red 輸出包含工具的截斷標記，未將其當成完整 log。fixture 實際輸出保存於 [fixture-result.json](fixture-result.json)。

## 重要邊界

- 並行八個 Stop 只有一個取得 exclusive-create 收據；key 只含 session + 原 user-turn，換 task_id 或收到新 prompt 不重置。
- 已存在的空／部分 reservation 不補發，先前 stdout 遺失亦不重送。收據路徑不可寫、symlink、特殊檔案均不輸出 block。
- 所有測試資源都在臨時目錄。第三 slice 的預期失敗曾在臨時根的 escape 子目錄寫出一個測試收據；確認完整內容與指紋後刪除該已知收據及空目錄，並將 fixture 改為額外一層 project，使後續越界負例仍留在個別測試擁有的臨時目錄。沒有日常設定或其他專案變更。
- hook 不寫任務合約；路徑檢查不是 OS 安全沙箱，也不宣稱提供主責接手的跨程序鎖。
- H03 config／contract 範本已擷取並透過本 CLI 在臨時資料驗證相容；owner=null 時只輸出條件式啟用提醒。

## 仍未證明

真實 Desktop 載入、hook 事件與 user-turn 身分穩定性、實際 Stop 延續、使用者 Stop 語意、模型遵循及人工投入改善均未驗證。必要資格 false 會明示未就緒，不能據此宣稱日常完整 harness 已交付。
