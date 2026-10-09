# ai-code-review 真實情境驗證（2026-10-09）

本輪現行 skill 的 **7 個獨立情境判斷均符合驗收預期**：功能變更及正確修復沒有被誤判為回歸；三個已知缺陷均被辨識；必要整合證據缺漏則得到 Hold，而非誤放行或捏造缺陷。沒有確認需要修改 skill 的新問題，本輪未修改正式 skill 或被審來源。

## 範圍與方法

- 目標：實際使用 skill 審查功能開發／需求變更、問題修正、重構及跨 repository 移轉，檢查判斷、證據、範圍與可操作性。
- 版本：現行 `skills/ai-code-review` 的 8 份 authored 檔案；雜湊見 [protocol.json](ai-code-review-real-20261009-evidence/protocol.json)。測後核對與正式來源逐位元一致。
- 在 `/private/tmp/ai-review-real-20261009` 建立全新隔離工作區，重用已構造的原始案例設計與 Git commits，排除舊報告、舊執行結果。每案由獨立、無父層歷史的 agent 載入 skill 後實際執行。
- agent 僅取得需求、固定版本、原始來源、probe 及輸出規則，未提供預期答案、疑似 bug 或建議修法。每案有自己的 output；沒有互看其他案例。
- 主驗證者先以獨立 oracle 確认材料行為，再閱讀各份實際報告、runner 及原始輸出，最後核對來源完整性、報告連結與 hash。不是只比對報告關鍵字。
- 額外提示明確要求先記開始時間、保留命令與原始輸出，因此本輪不作為「沒有提示也會自行遵守記時規則」的證明。

## 情境與結果

| 情境 | 原始材料與驗收目的 | 本輪 agent 實際結果 | 判斷是否符合預期 |
|---|---|---|---|
| [S1 功能變更](ai-code-review-real-20261009-evidence/S1/output/review.md) | 核准折扣門檻改為含 1000 cents；不得要求保留舊政策 | Approve；head 21/21，base 僅新門檻不符；公開輸入 guard 有效 | 是 |
| [S2 正確修復](ai-code-review-real-20261009-evidence/S2/output/review.md) | 排他 cursor 修復，保留順序、cap 與 limit guard | Approve；7 個邊界、7 個非法輸入、1,344 組有限域比對通過 | 是 |
| [S3 修復引入回歸](ai-code-review-real-20261009-evidence/S3/output/review.md) | cursor 修好但切片多一筆 | Request changes；F-001 定位 `[:limit + 1]`，公開入口可重現 | 是 |
| [S4 重構回歸](ai-code-review-real-20261009-evidence/S4/output/review.md) | 抽出 freshness policy 後相等邊界改錯 | Request changes；56 項檢查中 head 12 項失敗，兩個 caller 受影響 | 是 |
| [S5 完整本地移轉](ai-code-review-real-20261009-evidence/S5/output/review.md) | 跨獨立 repo、更名，保持回值及完整記憶體狀態 | Approve；110 序列、210 步觀測一致；old-old 與五類 mutation 校準 | 是 |
| [S6 移轉漏副作用](ai-code-review-real-20261009-evidence/S6/output/review.md) | 回值、庫存、done 一致，但漏成功事件 | Request changes；90/110 序列事件不同；沒有因回值相同而放行 | 是 |
| [S7 移轉缺必要證據](ai-code-review-real-20261009-evidence/S7/output/review.md) | 模擬一致，但契約另要求真實 rollback 與 exactly-once 證據 | Hold／部分完成／UNKNOWN；保留 U-001、U-002，沒有宣稱本地測試證明正式整合 | 是 |

S1 是既有功能的核准需求變更，不是從零開發整套應用。S5 的 dict 是明定完整驗收狀態；S7 的 dict 則只是正式持久化模擬，相同本地結果必須導向不同驗收結論。S7 的 Hold 是測試預期行為，不代表本次 skill 驗證工作未完成。

## 先確認問題，再驗證修法

主驗證者對兩版共執行 **1,052 筆觀測**，原始命令、輸出及 mismatch 見 [oracle-execution.json](ai-code-review-real-20261009-evidence/oracle-execution.json)。三個缺陷均在真實 fixture 程式重現後，才於獨立副本試作下列最小修法：

| 已確認 fixture 問題 | 唯一納入的修法 | PoC 結果 |
|---|---|---|
| S3 回傳超過 limit | 保留 `i > cursor`，切片恢復 `[:limit]` | 88 項：13 失敗 → 0 失敗 |
| S4 到期當下仍有效 | 共用 `fresh` 恢復 `now < expires` | 9 項：2 失敗 → 0 失敗 |
| S6 成功預約漏事件 | 扣庫存後、done 寫入前恢復一次 event append | 110 項：90 失敗 → 0 失敗 |

合計 **207 項修法 PoC 通過**；完整更動、命令、輸出見 [solution-poc.json](ai-code-review-real-20261009-evidence/solution-poc.json)，可重現程式為 [poc_solutions.py](ai-code-review-real-20261009-evidence/poc_solutions.py)。這些是測試材料的缺陷及解法，不是 skill 缺陷；未套用到被審來源。個別 agent 報告的「修法未驗證」正確描述其自身執行，本節另提供主驗證者的獨立 PoC。

S7 缺少真實整合材料，不提出未驗證的交易或事件架構修法。補證條件留在其報告，不以本地 mock PoC 冒充 production 驗收。沒有確認 skill 缺陷，因此沒有新增 skill 修正選項或實作計畫。

## 最終證據核對

- [parent-validation.json](ai-code-review-real-20261009-evidence/parent-validation.json)：14 個來源側快照與指定 Git commit 一致；8 項 migration helper 測試、6 項 hash checker 測試及 `quick_validate.py` 本輪重新執行，全數成功。
- [completion-audit.json](ai-code-review-real-20261009-evidence/completion-audit.json)：7 份報告均已實際閱讀；五章結構與末端完整清單確認；報告內本機連結皆可解析；所有來源輸入 hash 未變、來源 Git 工作樹乾淨、現行 skill 與測試副本相同。
- 最後寫入後重新執行每案 hash checker：S1 22、S2 32、S3 51、S4 24、S5 67、S6 54、S7 51，共 **301 個 linked hash 全部 exit 0**。數量不是通過依據，退出碼和 stderr 均保留於 completion audit。
- 三個移轉案例的 runner 實際匯入固定原碼，逐步深複製狀態，保存事件次序及重複數；old-old 與受控壞觀測用於校準。受控 mutation 明示為比較器測試，未冒充業務系統執行。

## 證據保存與限制

可閱讀檔案位於 [本輪證據目錄](ai-code-review-real-20261009-evidence)，與原始執行檔逐位元核對；[archive-manifest.json](ai-code-review-real-20261009-evidence/archive-manifest.json) 記錄完整清單。普通目錄副本排除 nested `.git`，完整 fixture Git metadata 另保存在 [original-run.tar.gz](ai-code-review-real-20261009-evidence/original-run.tar.gz)。

原始報告、logs 與部分 runner 保留實際 `/private/tmp/ai-review-real-20261009` 絕對路徑，未改寫歷史紀錄。若該暫存目錄已移除，可檢查封存後，將封存還原到 `/private/tmp` 再重現；已有同名工作區時不要直接覆寫。需要重跑會寫檔的 runner 時先另存原始證據，helper 的 `--out` 使用新檔名。

本輪是真實 agent + Git + Python 執行，但材料是小型合成 repo；不能推廣成大型專案、其他語言／框架、真實 DB／broker 或高併發的全面驗證。每案只執行一次，未估計跨次穩定性。Mermaid 均未實際渲染，僅核對來源與關係，不聲稱視覺驗收。沒有安裝依賴到專案、修改正式 skill、提交、推送或變更外部平台。
