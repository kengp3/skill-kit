舊規則獨立盤點（先讀 base，尚未讀 head）：
R1 base/api.py:1-3 submit 原參數委派 reserve。
R2 legacy.py:2-3 done 優先；同 key 直接回前次結果，忽略變動 count。
R3 legacy.py:4-5 count < 1 或超庫存拒絕，狀態不變。
R4 legacy.py:6 成功精確扣 count。
R5 legacy.py:7 每個首次成功追加一筆 key/count 事件，保留順序與重複數。
R6 legacy.py:8-9 成功記 done 並回 accepted。
來源固定 commit 0470b8ec7cf06787cc072c1e7829b45127677fcc。規格交叉核對 contract.json。後續需確認新側 replay 優先序、事件完整性與 caller 是否改寫觀測。
