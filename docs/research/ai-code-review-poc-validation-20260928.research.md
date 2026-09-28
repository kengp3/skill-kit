# Code review POC：判斷與報告易讀性驗收

2026-09-28，Asia/Taipei。範圍為 `simple-skills/skills/ai-code-review` 的本機情境演練，非遠端 PR 放行。

五個情境的報告品質門檻全部通過：來源／實跑判斷、問題與修法表達、真實圖形閱讀、獨立讀者與證據核對均完成。第一輪找到 S3、S4 的流程圖過度縮小，已修改兩條共用報告指引，並用 S5 新情境確認改善能轉移。正文沒有完整 SHA-256，完整值保留在各報告旁的核對索引。

## 情境與最終採用報告

| 情境 | 已核對的判斷與觀測 | 採用報告 | 報告驗收 |
|---|---|---|---|
| S1：小型分頁變更、兩個 caller | 1 個共同根因；游標等值資料重複，匯出觸發保護例外；Request changes | [S1 r1](ai-code-review-poc-s1-r1-20260928.research.md) | 判斷及圖文通過 |
| S2：經核准的折扣門檻變更 | 1,000 分含優惠時新值 900；符合新契約，沒有誤報成回歸；Approve | [S2 r1](ai-code-review-poc-s2-r1-20260928.research.md) | 判斷及圖文通過 |
| S3：Java 多類別退貨重構 | 4 個根因：分批最後一次少退 100 cents、第 30 天誤拒、退款失敗前寫入退貨／庫存、重播被可變 guard 擋住；Request changes | [S3 r2](ai-code-review-poc-s3-r2-20260928.research.md) | 判斷通過；圖表修後通過 |
| S4：來源正確、必要整合證據缺漏 | FakeBus 本機案例一致；缺真實 transport 的持久性與 acknowledgement 時序紀錄，1 個 U、0 個程式缺陷；Hold／部分完成／UNKNOWN | [S4 r2](ai-code-review-poc-s4-r2-20260928.research.md) | 正確保留缺口；圖表修後通過 |
| S5：修後新快取情境、空字串與期限 | 1 個共用判斷根因；now=expires=10 時 preview／export 仍輸出過期值，空字串合法值未被另誤報；Request changes | [S5 r2](ai-code-review-poc-s5-r2-20260928.research.md) | 判斷、圖形與獨立讀者通過 |

各報告品質通過，與被審程式是否通過是兩個判斷。S1／S3／S5 故意包含缺陷，S4 故意缺少必要證據；不能為了讓 POC 顯示綠燈，把這些結論改成 Approve。

## 確認的問題與最小修改

S3、S4 原報告將 base／head 放在同一 Mermaid 圖的 subgraph。真實預覽把 S3 約 6,665px、S4 約 3,507px 的圖縮到 1,048px 寬；節點及分支文字難以閱讀。語法有效與沒有頁面溢出，均不足以證明可讀。

修改 [report.md](../../skills/ai-code-review/references/report.md) 的兩條既有規則：

- 拓樸相同時，優先畫一版並以文字說明差異；時序不同才拆開比較，避免重複大圖。
- 在一般報告寬度、正常縮放下讀節點／分支；過小就縮短標籤、換行或拆圖，再核對 guard 與出口。

S4 改成一張 head 直向圖，原寬約 476px；S3 依版本及責任拆成四張圖，原寬約 453–533px。兩者不再因縮放犧牲字級。S5 獨立 reviewer 使用修後 skill，首次產出的單圖約 564px 寬，兩 caller、缺值 guard 及回傳分支均可閱讀。

| 前後證據 | 原版 | 修後 |
|---|---|---|
| S4 | [r1 截圖](ai-code-review-poc-20260928-evidence/s4-r1-diagram.png) | [r2 截圖](ai-code-review-poc-20260928-evidence/s4-r2-diagram.png) |
| S3 | [r1 截圖](ai-code-review-poc-20260928-evidence/s3-r1-diagram.png) | [head guard](ai-code-review-poc-20260928-evidence/s3-r2-guards-head.png)、[head 副作用](ai-code-review-poc-20260928-evidence/s3-r2-effects-head.png)、[出口](ai-code-review-poc-20260928-evidence/s3-r2-effects-head-bottom.png) |
| S5 新情境 | 不提供先前答案或報告 | [入口](ai-code-review-poc-20260928-evidence/s5-r2-diagram.png)、[分支／出口](ai-code-review-poc-20260928-evidence/s5-r2-diagram-bottom.png) |

S3、S4 r2 只改呈現，保留原開始時間、觀測、finding 與解除條件；沒有聲稱重新執行 Java／業務 Python。報告作者寫的「待主審渲染」是產稿當下狀態，本文件及 [visual-checks.json](ai-code-review-poc-20260928-evidence/visual-checks.json) 記錄其後補做的最終視覺驗收。r1 保留原樣，不改寫歷史紀錄。

## 驗證方法與證據

1. **獨立產報告：** 審查者取得 skill 與固定原始材料，沒有取得預期根因、父計畫或其他情境答案。S5 使用全新上下文與修後 skill。各 reviewer 重跑必要案例，記錄 argv、退出碼、stdout／stderr；不是只採用 generator 的輸出。
2. **來源與觀測：** 逐情境核對公開／約定入口、guard、caller、具體輸入及結果。S3 重編兩版，各完整執行八案十二步並比較九欄；五案差異合併成四個根因。S5 四個程序執行成功，但 head 的到期當下觀測不符契約，沒有把 exit 0 當成業務 PASS。
3. **獨立讀者：** [首輪記錄](ai-code-review-poc-20260928-evidence/readability-r1.json) 明列 S1／S2／S4 首次誤讀部分正文的方法偏差；另請未讀過報告的 reader 只讀基本說明及問題總表，先保存決策／剩餘／第一步回述，再讀全文與截圖。五份全部完成，15 張圖形截圖均實際查看；重大缺陷 0，optional 1（S3 首次「九欄觀測」可加附錄連結），不影響決策與解除條件理解。最終逐份回述與 gate 見 [readability-final.json](ai-code-review-poc-20260928-evidence/readability-final.json)。
4. **實際呈現：** 用已安裝的 marked、Mermaid 11 及本機 HTTP 預覽，在 1280px 瀏覽器、正常縮放下檢查。五份採用報告共八張圖，皆完成渲染；無頁面橫向溢出，章節錨點皆存在。截圖逐段包含跨畫面流程，並非只檢查圖形數量。預覽不是 Codex 原生 Markdown renderer；其他檢視器及手機寬度不在本輪保證範圍。
5. **直接檔案核對：** 七份報告（含兩份被取代的 r1）共 254 個本機引用／行號有效；七個索引共 146 個列出 hash 全部相符；五份 fixture manifest 的 55 個項目未變。正文均無 64 位完整 digest；五章及最後完整清單齊全。核對記錄見 [artifact-validation.json](ai-code-review-poc-20260928-evidence/artifact-validation.json)。兩份 skill-r2 snapshot 與目前 skill 逐檔相同。
6. **工程檢查：** `git diff --check` 通過；`python3 -B -m unittest discover -s tests -p 'test_*.py' -v` 共 13 個測試，12 通過、1 個既有 Windows native 測試因 macOS 跳過。[Skill 結構驗證](ai-code-review-poc-20260928-evidence/skill-validation.json) 通過；PyYAML 從本機既有 wheel 解到暫存目錄，未安裝依賴。

本輪保留前輪已完成的 [hash checker 優化](ai-code-review-optimization-20260928.research.md)；本次新修改只針對已證明的圖表問題。未因 optional 的流程自述或篇幅偏好再擴充規則，也未增加框架或全域依賴。

## 重現與限制

[情境產生器](../../tests/poc_review_readability.py) 重用既有 pagination／Returns fixture；新輸出目錄必須不存在，避免覆蓋先前證據：

```sh
python3 -B tests/poc_review_readability.py --out /tmp/review-poc-new-run
python3 -B tests/poc_review_readability.py --forward-only --out /tmp/review-poc-new-forward
```

生成器保存當時的 skill；新執行不會重現歷史 skill-r1 規則，歷史規則以本輪保留快照為準。預覽程式 [render-preview.mjs](ai-code-review-poc-20260928-evidence/render-preview.mjs) 保留此次本機 runtime 路徑；移機需調整 marked 路徑，Mermaid CDN 亦需連線。

本輪只能證明這五個人工情境及本機觀測的報告品質，不能推廣為任意 repository 的查錯率。S4 所需真實 transport 仍未提供／未執行；這正是 Hold 的理由。建議修法與原 head 分開，除 S1 已記錄的隔離副本驗證外，其餘未宣稱已修復或可直接放行。所有變更留在工作樹，沒有 commit、push 或遠端 review。
