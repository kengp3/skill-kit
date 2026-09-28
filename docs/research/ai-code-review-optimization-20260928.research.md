# ai-code-review 優化與驗證紀錄

## Objective

分析目前 code review skill 的可改善項目，修正有可重現證據的問題，讓報告的證據核對可靠且可操作。本輪優化已完成；不是對 skill 所有審查情境或查錯率的全面認證。

## Background

分析基準為本機 `simple-skills` 的 `6e81e15` 與目前工作樹。原有 skill 已將 SHA-256 移至獨立索引；本輪發現核對工具會略過某些格式錯誤條目，造成同頁存在合法條目時誤判通過。

## Materials

- [Skill 入口](../../skills/ai-code-review/SKILL.md)、[深度審查](../../skills/ai-code-review/references/deep-review.md)、[報告規則](../../skills/ai-code-review/references/report.md)、[移轉規則](../../skills/ai-code-review/references/migration.md)、[證據工具契約](../../skills/ai-code-review/references/evidence.md)。
- [核對工具](../../skills/ai-code-review/scripts/check_report_hashes.py)、[快照與比較工具](../../skills/ai-code-review/scripts/review.py)、[核對測試](../../tests/test_check_report_hashes.py)、[比較工具測試](../../tests/test_migration_review.py)。
- 已提交的[分頁案例 manifest](ai-code-review-paging-20260925-evidence/input/manifest.json)與兩版原碼，用於獨立複製工具的實跑驗證。
- 依 `define-task` 定義範圍、`using-agent-skills` 選擇 TDD 與 code review 流程、`ponytail` 保持最小變更、`skill-creator` 檢查必要說明及結構。歷史結果只用於定位，判斷以本輪來源與實跑為準。

## Boundaries 與 Assumptions

優化對象延續本專案的 `ai-code-review`。保留歷史報告、索引、案例與其他未提交研究；不重算舊索引冒充舊工具版本，也不自動 commit、push 或修改已安裝 plugin。工具維持標準函式庫實作，支援已明定的 Markdown 行內連結格式，未擴充為完整 Markdown parser。

## 分析與實作

| 項目 | 本輪直接證據 | 處理 |
|---|---|---|
| 格式錯誤被靜默略過 | 合法條目旁放非 hex、空值、缺值、未閉合反引號、過短或過長值，共 6 個反例在舊版均退出 0 | 先辨識已標示的條目，再驗證完整值；錯誤回報行號並退出 1 |
| 合法路徑未被識別 | `<source (copy).py:1#code>` 在舊版得到 checked 0 | 支援尖括號路徑，保留行號、錨點處理及大小寫 hex 相容性 |
| 讀檔錯誤難以操作 | 索引缺檔、目錄、非 UTF-8 內容均產生 traceback | 回傳可讀的 cannot read 訊息及退出碼 1；來源讀取錯誤同樣處理 |
| 非一般檔案保護 | 自我審查發現直接讀取可能卡在 FIFO；加入測試後初版修正確實逾時 | 保留 `is_file()` 防護，FIFO 測試通過，避免引入回歸 |
| Skill 流程與觀測比較 | 已核對入口、來源固定／比較工具及相關 reference；現有測試涵蓋 PASS、FAIL、UNKNOWN、過期證據、額外觀測與不合法命令 | 本輪未找到需要修改這些流程的直接證據，保留既有設計 |

## Definition of Done 與完成證據

1. **先重現再修正：完成。** 新增測試在原工具出現 10 個失敗斷言；最終版本全部通過。CLI 實跑而非僅比對 regex 文字。
2. **回歸：完成。** `python3 -B -m unittest discover -s tests -p 'test_*.py' -v`：13 項中 12 通過、1 項既有 Windows `cmd.exe` 專用測試因 macOS 跳過；沒有新增 skip 或停用測試。
3. **獨立使用：完成。** 將新工具複製到暫存目錄，以 Python `-I` 執行；分頁案例 manifest 的 6 個原碼值全部通過，加入第 7 個格式錯誤值後退出 1 並正確定位第 7 行。未改寫歷史索引或原碼。
4. **Skill 結構：完成。** `quick_validate.py skills/ai-code-review` 回傳 `Skill is valid!`、退出 0。系統 Python 缺少 PyYAML，已使用本機快取的 PyYAML 6.0.2 wheel 解開至暫存目錄完成驗證，沒有新增專案或全域依賴。
5. **變更審查：完成。** 已讀回工具、測試與說明，確認格式錯誤、內容不符、讀取失敗皆不會回報成功，保留正常索引與舊 hex 格式；`git diff --check` 通過。

最後一組結構與獨立 CLI 驗證時間：2026-09-28 14:22:43 +08:00。上述驗證支持本輪優化；未執行 Windows 原生測試，也不宣稱重新完成歷史上全部獨立盲測。
