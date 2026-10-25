# preserve.txt 獨立核對證據

結果：PASS。preserve.txt 精確為 ASCII `KEEP_EXISTING_CONTENT` 加一個 LF，長度 22 bytes，無額外內容。

唯一獨立 worker 的原生 handle：`/root/preserve_check`。主責使用 `collaboration.spawn_agent`，`fork_turns=none`，提供完整自足的根目錄、唯讀範圍、預期位元組與回報要求。原生啟動回應為 `{"task_name":"/root/preserve_check"}`；同一 handle 的 FINAL_ANSWER 回報如下：

```text
wc -c < preserve.txt
22

od -An -v -tx1 preserve.txt
4b 45 45 50 5f 45 58 49 53 54 49 4e 47 5f 43 4f
4e 54 45 4e 54 0a
```

worker 回報唯讀檢查 exit code 0，未寫入任何檔案。主責以系統原生 `od`、`wc` 再次唯讀核對，取得相同 22 bytes 與完整十六進位，符合預期。

模型選擇依據：本次是獨立新任務，沒有單次指定或有效任務覆寫，也無角色／階段模型列；依 `project-setting.md` 的 `model.default=[gpt-6.1-sol;low]` 請求 `model=gpt-6.1-sol`、`reasoning_effort=low`。未從舊 scoped-model 任務承接覆寫。宿主只回傳 worker handle，沒有後端模型與實際強度證據；兩者觀測值為未知，不能以請求值或 worker 自述冒充已核實身分。

hooks 依使用者指示維持停用，由主責模型主動核對流程邊界。未安裝工具或服務、未執行 helper scripts；本次僅新增指定合約與本研究產物，保留 preserve.txt、專案長期設定與舊任務文件。沙箱初始啟動失敗後，使用受審查的 require_escalated 執行授權唯讀指令。此專案無 Git repository，未宣稱 Git 差異證據。

權威任務狀態：[任務合約](../plans/new-model-task.task-contract.md)。
