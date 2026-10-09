# 全目標關聯與影響分析
paging.py 唯一差異區塊 after(ids,cursor,limit)：目的為排除 cursor 本身；舊 >= 可回傳游標，新 > 排除游標。唯一公開入口 api.page 先拒絕非 int（包含 bool）與 <1 limit，再呼叫 after。ids 為排序唯一整數、cursor 為整數是契約有效輸入邊界。清單生成保留原順序，切片限制長度；不修改輸入、不發出外部副作用。
api.py 未變更，完整 guard 與 caller 已讀：type(limit) is not int 排除 bool，不能以直接呼叫 after 的非法 limit 推導公開 API bug。兩個版本共兩個 Python 檔，無其他 caller、測試或配置。影響只在本地記憶體 API 的游標相等情況；複雜度仍 O(n)，沒有新增效能退化。
選一張流程圖呈現公開 guard 與篩選/切片；無跨服務、狀態機或類別結構變動，不需其他圖。圖屬來源推導，將在報告揭露未渲染。
