# 分批改架構移轉：`ai-code-review` 情境驗證

執行日期：2026-09-28（Asia/Taipei）。專案：`/Users/kengp3/Workspaces/mine/simple-skills`。對象為目前工作樹的 `skills/ai-code-review`，不是實際業務移轉 PR。

## 結論

**本輪六個隔離案例的審查判斷均符合事先固定的契約與實跑觀測，因此沒有修改 skill。** 正確移轉獲限定範圍通過；四個不同根因各被定位並要求修改；舊側必要證據缺失時暫緩。這證明此組案例中的判斷有效，不是對任意專案、所有輸入或完整移轉的查錯率保證。

本輪材料先出現一次缺少 `Probe.java` 和 Git objects 的 reader 包。獨立審查指出該缺口後，重建包、固定新的版本及 hash，再以**新的獨立審查者上下文**重做全部六案。第一次材料審查未計入 skill 成效，也沒有改寫不利結果。

## 固定來源與方法

- [執行計畫](../plans/ai-code-review-existing-business-validation.plan.md)定義同一舊專案分兩批改架構：batch 1 移轉 order；batch 2 移轉 refund；loyalty 屬後續獨立批次。
- [產生與校準程式](../../tests/poc_incremental_migration_review.py)建立舊版、每案 target base/head、來源、Git bundle、Probe、契約和逐案輸出。完整 [evaluator oracle](ai-code-review-incremental-migration-validation-evidence/oracle.json) 在審查前由獨立斷言固定；審查者只讀各自 reader，不取得 oracle、生成器、計畫或其他案材料。
- 六個 reader 與原始執行紀錄保存在[證據目錄](ai-code-review-incremental-migration-validation-evidence/)。[skill 基準副本](ai-code-review-incremental-migration-validation-evidence/skill-baseline/SKILL.md)及[副本雜湊](ai-code-review-incremental-migration-validation-evidence/skill-baseline-hashes.json)保存當輪指引。[provenance](ai-code-review-incremental-migration-validation-evidence/provenance.json)記錄 Python、Java、Git 版本與當輪 skill／runner SHA-256。每案 `manifest.json` 的 17 或 20 個檔案 hash 均重驗；target bundle 的 base/head 與 manifest 相符。
- 校準程式實際編譯、執行舊版和各案新版的九個指定案例，並從封存 reader 的來源與 Probe 再編譯、執行核對。雙側初態均為獨立的新實例；`sequence` 用同一個新側 `State`。它用明列的 `EXPECTED` 比對完整回傳與狀態，變異版只允許事先固定的差異集合。這是模擬 Java 程式的執行證據；獨立審查者本人只讀來源與紀錄，沒有另跑 Java。

## 逐案稽核

| 案例 | 獨立審查結果 | 實跑差異及來源根因 | 稽核 |
|---|---|---|---|
| [C0 正確分批](ai-code-review-incremental-migration-c0.research.md) | Batch 2 Approve；限定九案 PASS | 九案舊新輸出／狀態一致；新架構以 `OrderService`、`RefundService`、`Warehouse` 承接舊責任 | 符合；loyalty 正確列後續批次，不當成本批阻擋 |
| [C1 退款期限](ai-code-review-incremental-migration-c1.research.md) | Request changes；FAIL | `RefundService` 用 `ageDays >= 30`，舊版及契約允許第 30 天；`age30`、`sequence` 兩案不同 | 命中單一根因與解除條件 |
| [C2 拒付副作用](ai-code-review-incremental-migration-c2.research.md) | Request changes；FAIL | `refunds++` 在 decline 判斷前；`decline` 案新版錯增成功退款數 | 命中單一根因，未把回傳相同誤判為一致 |
| [C3 前批回歸](ai-code-review-incremental-migration-c3.research.md) | Request changes；FAIL | 本批把共用 `Policy.shipping` 的 `>= 8000` 改成 `> 8000`；未改的 order caller 在 `order8000` 和 `sequence` 多收 500 分 | 命中跨批 caller 與本批改動的因果鏈 |
| [C4 必要相依](ai-code-review-incremental-migration-c4.research.md) | Request changes；FAIL | `Warehouse.restock` 為空實作；成功退款的 `restocked` 在 `age30`、`replay`、`sequence` 少 1 | 命中必要副作用；沒有把它當成可延到後批的 loyalty |
| [C5 缺舊側證據](ai-code-review-incremental-migration-c5.research.md) | Hold；UNKNOWN | reader 缺舊 refund 來源與五個舊側必要案例；四個 order 案例仍可比較 | 正確保留已知部分並列最小補證，未捏造 bug 或給 PASS |

四個 FAIL 案均由獨立 reviewer 指出可達入口、舊規則、目標責任點、可觀測差異與最小解除方式；沒有把同根因的不同案例拆成多個阻擋。C0 無無據阻擋；C5 無憑空缺陷。所有六案均區分批次建議與整體移轉狀態。完整報告連結於上表，各報告由獨立審查者先寫入；封存路徑已改為本專案持久證據位置。

## 驗證與限制

| 檢查 | 當輪結果 |
|---|---|
| `python3 -B tests/poc_incremental_migration_review.py --out /private/tmp/incremental-migration-review-20260928-e` | exit 0；六案差異集合與獨立 oracle 完全相符，並完成 reader 重跑／bundle clone 自檢 |
| 從 `docs/research/ai-code-review-incremental-migration-validation-evidence/` 重新編譯並執行 Probe | 6 個新側與 5 個可用舊側各 9 案，共 99 次案例執行；輸出均符合封存 oracle。C5 舊側退款刻意缺證，未冒充重跑 |
| `python3 -B -m unittest discover -s tests -p 'test_migration_review.py' -v` | 5 項通過，exit 0 |
| `quick_validate.py skills/ai-code-review` | `Skill is valid!`，exit 0；系統 Python 缺 PyYAML，僅在 `/private/tmp` 安裝 `PyYAML==6.0.2` 作 validator 執行，未新增專案或全域依賴 |
| 六份 reader manifest／bundle 與研究報告連結 | hash、base/head refs 與連結均核對有效 |

上述歸檔重播、單元測試、validator 和 diff 檢查的原始命令、退出碼與輸出存於[最終驗證紀錄](ai-code-review-incremental-migration-validation-evidence/final-validation.json)。

這組 fixture 只涵蓋九個循序、記憶體內的案例，沒有 DB commit／rollback、外部付款或訊息系統、並行、部署切換或實際移轉專案的功能清單。舊系統基準若持續變動，真實每批審查仍須固定該批舊版與核准差異；本次人工案例沒有驗證動態基準治理。C0 的 PASS 只限這個合約與指定版本。

C5 的完整舊版只保存在 evaluator 證據中供事後核對；C5 reader 沒有退款來源或五個必要舊側觀測。審查者的 Hold 是對其實際可取得材料的判斷，不能用 evaluator 私有材料事後宣稱該 reader 已有足夠證據。

## 決策與交付

依計畫的條件式 T6，**未觀察到需要修正 skill 判斷流程的失敗，因此保持 `SKILL.md`、`migration.md`、helper 不變**；沒有「修後提升」或新情境 forward test 的宣稱。若未來實際批次出現漏報，應固定其舊／新版本與觸發案例，再以該反例做最小修正與重驗。

本輪交付 runner、六份獨立審查報告、封存 reader／原始紀錄／oracle、本結果研究及已更新的計畫。沒有提交、推送或更新遠端 PR。這些產物用於評估 skill；未修改任何真實業務系統。
