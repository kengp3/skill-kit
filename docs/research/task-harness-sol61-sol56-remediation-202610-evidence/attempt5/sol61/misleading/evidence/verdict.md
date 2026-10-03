# 驗收結果

判定：release candidate 不可接受。檢查 stdout 雖顯示 PASS，但實際退出碼非零，屬失敗；SHA-256 計算成功。兩份收據皆為 finished，且 check.py、payload.txt 在檢查前後保持一致。

實際命令、退出碼、stdout 與 SHA-256 請見權威收據：
- [checker](T1-check-1.json)
- [SHA-256](T1-sha256-1.json)

評估任務已完成；負面判定不代表 candidate 通過。未修改檢查器或輸入，未重試或修復。
