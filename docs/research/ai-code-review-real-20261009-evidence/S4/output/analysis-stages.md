# 階段 ① 目標盤點
base review-base 06ecf76f8d530a58543ea46ab16a2cd8671e5fe6；head review-head e12142caae223d49fc019618c96a5bf6422a848b。merge-base = base；採三點 diff。工作樹乾淨。
- M cache.py：新增 policy.fresh import，lookup 的判斷委派；單一 hunk。
- A policy.py：新增 fresh(now, expires)，單一 hunk。
- 關聯未變 views.py：preview、export_values，完整讀取兩版。無其他 tracked 檔案。
# 階段 ② 全目標影響分析
cache.lookup：保留 store.get 與 missing guard、tuple unpack、None 結果；唯一外部行為取決於 fresh 判斷。policy.fresh：now < expires 改為 now <= expires，整數相等可達。views.preview 直接回傳；export_values 使用 is not None，保留空字串、重複 key 及輸入順序，亦導出被錯誤視為有效的過期值。無寫入 store／外部 clock／I/O。選單張函式與條件關係圖呈現共用根因與兩入口；無跨執行緒或交易時序。
# 階段 ③ 判斷基準
契約明定純重構、now < expiration 才 fresh，missing／expired 為 None；export 保留 fresh 空字串及順序。相等界線需拒絕；正常 fresh、late expired、missing、empty、duplicate/order 均須維持。候選根因：policy.py:2 <=；反證查核：兩 caller 均未限制 now != expiration，contract 明定整數同時鐘，不排除相等。
