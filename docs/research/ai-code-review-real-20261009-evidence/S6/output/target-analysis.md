# ① 完整目標清單
比較獨立 repo 固定快照，無共同祖先假設；git diff --no-index --no-renames exit 1 表示有差異。
M api.py → api.py：兩個 hunk 行變更位於同一 diff 區塊，import 與委派 reserve 改 execute；公開 submit 保留。
D legacy.py → —：整個 reserve 9 行移除，需逐一映射 R2-R6。
A — → service.py：整個 execute 8 行新增，需反向檢查新增規則。
所有來源均 Python；無配置、二進位、生成或 repo 內測試。關聯 probe.py 為範圍提供的七案例觀測程式，不含 assert。

# ② 全目標關聯與影響
api.py：目的為入口移轉；前後 submit(state,key,count) 直接委派；caller 是 probe.py 與可重現 harness；無資料轉換或 guard，內層所有副作用可從 state 觀測。
legacy.py：移除實作而責任移至 service；done→guard→扣庫存→事件 append→done→回值；刪除事件必須有替代點，未發現。
service.py：重放、拒絕、庫存、done、回值保留；成功事件沒有替代來源。未新增 guard 或核准例外。影響是 submit 成功的可觀測 state.events。
probe.py：七案例含正常、0、超額、耗盡、同 key 相同或變量重放、第二次庫存不足；只印結果、不判定一致，不足完整契約。新增 harness 窮舉完整 110 序列，每步觀測 return/error/stock/events/done，無 schema 正規化。
選圖：一張流程圖足以說明共用 guard 及成功路徑缺事件；不是 OO，無需類別圖。API 關聯標在入口，無跨 repo 呼叫。
影響邊界：stock=3、done={}、events=[]，keys a/b、count 0..4、序列長 1..2。記憶體 dict 已是完整驗收狀態，不需 DB/broker 證據。並行、惡意 state、其他型別及更長序列不納入。
