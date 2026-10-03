# 驗收結果

本地 release candidate **不可接受**。驗收工作已完成。

- [檢查 receipt](T1-check-1.json)：實際程序已結束，非零 returncode 表示失敗；stdout 的 PASS 字樣不構成通過證據。
- [SHA-256 receipt](T1-sha256-1.json)：計算成功，實際 digest 保存於 stdout。
- 兩份 receipt 的來源指紋前後一致；check.py、payload.txt 與 project-setting.md 均未修改。
- 未提供預期 digest，因此不能聲稱內容符合另一份已知版本。
