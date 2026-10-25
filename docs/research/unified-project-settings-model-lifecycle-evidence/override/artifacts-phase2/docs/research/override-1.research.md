# T1 獨立唯讀核對證據

結果：PASS。`preserve.txt` 精確為 ASCII `KEEP_EXISTING_CONTENT` 加一個 LF，22 bytes。

- 任務：scoped-model / T1；唯一權威合約：../plans/scoped-model.task-contract.md。
- 獨立 worker 原生 handle：`/root/t1_readonly_check`；spawn 成功且 collaboration.list_agents 回報 completed。
- 原生派工請求：model=`gpt-6-sol`、reasoning_effort=`low`、fork_turns=`none`，附自足輸入。
- 選擇依據：本次使用者明確指定，優先於專案預設；本任務限定覆寫。專案長期設定未修改。
- 宿主只回傳 handle 與完成結果，未提供實際後端模型／強度；兩者未核實，不以請求值代替。
- worker 僅唯讀檢查並回報；此產物由主責整合保存。worker 未寫檔、未執行 T2。

worker 原始工具證據（依其訊息與最終回報保存）：

```text
wc -c preserve.txt
22 preserve.txt

od -An -tx1 -v preserve.txt
4b 45 45 50 5f 45 58 49 53 54 49 4e 47 5f 43 4f 4e 54 45 4e 54 0a

shasum -a 256 preserve.txt
f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe  preserve.txt

printf 'KEEP_EXISTING_CONTENT\n' | cmp -s - preserve.txt; printf 'cmp_exit=%s\n' "$?"
cmp_exit=0
```

主責核對 hex 對應指定 ASCII 文字，最後唯一換行為 0a，byte 數與完整比對成功碼一致；worker SHA-256 與主責派工前保存的原檔指紋一致。預設 sandbox 啟動失敗後，worker 使用經核准的相同唯讀 shell 檢查；未使用 helper scripts。hooks 依要求維持停用，流程檢查由模型完成，未宣稱 hook 觸發。
