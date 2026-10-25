# T2 獨立唯讀核對證據

結果：PASS。`preserve.txt` 精確為 ASCII `KEEP_EXISTING_CONTENT` 加一個 LF，共 22 bytes。

- 同一任務 scoped-model / T2；唯一合約為 ../plans/scoped-model.task-contract.md。
- 原生獨立 worker handle：`/root/t2_readonly_check`，不同於 T1 的 `/root/t1_readonly_check`。
- 請求：model=`gpt-6-sol`、reasoning_effort=`low`、fork_turns=`none`，附自足輸入。
- 選擇依據：本回合無新模型指定，依優先序 2 沿用同一任務合約中仍有效的 `[gpt-6-sol;low]` 單次覆寫，優先於專案預設 `[gpt-6.1-sol;low]`。未修改長期設定。
- 宿主成功回傳 handle；未回傳實際後端模型或強度，實際值未核實，不能以請求值替代。
- worker 僅唯讀核對並回報，主責保存本產物；保留 T1，不重派。

worker 訊息提供的原始工具輸出：

```text
      22 preserve.txt
           4b  45  45  50  5f  45  58  49  53  54  49  4e  47  5f  43  4f
           4e  54  45  4e  54  0a

f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe  preserve.txt
cmp_exit=0
```

worker 回報使用 wc、od、shasum 與 `printf 'KEEP_EXISTING_CONTENT\n' | cmp -s - preserve.txt`。主責核對 hex 完整對應指定文字與唯一末尾 LF，22 bytes 與 cmp_exit=0 一致；SHA-256 與恢復時及原始合約指紋一致。

初次預設 exec 回報 `sandbox-exec: sandbox_apply: Operation not permitted`，同一唯讀命令經 require_escalated 成功。worker 回報未寫入檔案。未安裝工具或服務、未執行 helper scripts、未修改 hooks；主責主動完成流程檢查，不宣稱 hook 事件。
