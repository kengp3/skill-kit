# 任務分割、分派與執行 Harness：2026-10 研究

## 執行摘要

- 建議建立輕量的 `task-harness` skill：一份權威任務清單，加上現有 agent 工具、驗收與續作規則；不自行重建 runtime。
- 核心是「可驗收成果 → 依賴與 ownership → 執行 → 直接證據 → 整合」，不是固定 agent 人數。
- 多 agent 適用於可獨立處理的工作；共享檔案、資料庫及合約依賴會降低可平行程度。
- 將輸出存在、worker 自報完成、驗證通過、整合通過分開；中斷後重新核對 current truth。
- 截至 **2026-10-02（Asia/Taipei）**，本次可取得資料支持上述設計方向，但不足以證明通用最優配置或成功率。skill 的有效性需另以真實情境驗證。

## 研究問題

1. 任務如何切分，才能保持完整成果又不過度分割？
2. 如何決定依賴、owner 與何時使用多 agent？
3. 如何避免共享狀態、重複分派與結果整合衝突？
4. 哪些狀態必須持久化，續作時哪些資料必須重新確認？
5. 如何以可觀察證據驗收，避免自評或過時綠燈？
6. 如何設定重試、預算與停止條件，避免盲目無限迴圈？

## 範圍與假設

研究服務於可獨立使用的 Codex skill，包含軟體及一般多步驟任務。當前環境具有原生 subagent 工具；其他安裝環境必須自行偵測可用性。沒有假設每次都能平行、所有 worker 都有隔離 checkout，或 skill 自帶持久 scheduler。

「202610」解讀為截至 2026-10-02 可查到的資料，並非整個十月的回顧。工程文章是作者的案例經驗，官方文件是產品契約，論文是特定實驗；三者不等於普遍共識。排除新增 SaaS tracker、全域安裝、價格比較與模型排名。

## 方法

搜尋 harness engineering、long-running agents、multi-agent research、structured planning、durable execution 等關鍵字；優先閱讀 OpenAI、Anthropic、LangChain 一手內容，再檢視 2026 年研究。未將搜尋摘要或社群貼文作為實作依據。

停止條件：六項問題各有直接來源或標示推論；至少跨兩個供應商交叉核對；已找到平行化、固定拆分與 deterministic harness 的限制。當條件滿足後停止擴搜，不追求來源數量。

當前產品工具名稱與權限以本 session 實際工具定義為準。下表記錄來源日期與本次讀取日期；無發布日期的動態文件不猜版本。研究不複製整篇來源，僅記錄支持本決策的主張。

## 主要發現

- **可驗收切片與外部狀態比「一次完成整個專案」可靠。**（事實；信心: 高）Anthropic 的長任務案例使用功能清單、增量執行與交接狀態；OpenAI 將較複雜工作的執行計畫及決策紀錄作為 repo artifacts。採納成果、驗證、續作資訊，但不把案例中的固定檔名或自動 commit 變成通則。[Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)、[OpenAI](https://openai.com/index/harness-engineering/)
- **平行化需要明確分工與成本判斷。**（事實；信心: 高）Anthropic 的多 agent 系統要求 objective、輸出形式、工具與邊界，也指出共享大量上下文或依賴密集的工作不適合直接套用其研究型平行架構。因此本 skill 以 ready tasks 與寫入範圍決定分派，並保留串行 fallback。[一手工程說明](https://www.anthropic.com/engineering/multi-agent-research-system)
- **拆分粒度需隨模型及工作調整，獨立 QA 仍有價值。**（事實；信心: 中）2026-03 的 Anthropic 案例在較新模型上簡化部分 scaffolding，仍透過 evaluator 發現核心功能缺口。這支持可調粒度，不支持固定三 agent 或一律取消拆分。[案例與限制](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- **checkpoint 不代表任意副作用可安全重播。**（事實；信心: 高）LangGraph 文件說明 replay 從 checkpoint 邊界恢復，未完成 task 可能重跑，寫入應採 idempotency 或先查結果。skill 只能要求核對 receipt 與 current state，不能用 Markdown 宣稱 exactly-once。[Functional API](https://docs.langchain.com/oss/python/langgraph/functional-api)
- **結構化計畫值得使用，但不能據此保證穩定性或效能。**（事實；信心: 中）2026-08 的研究測試兩個模型及兩個 synthetic 線性流程；作者明示不能直接推廣到分支或判斷型任務，延遲成本也依模型而異。這裡只採納明確欄位與驗證，不採用其成功率作產品承諾。[全文與 limitations](https://arxiv.org/html/2608.26197v1)
- **最小實作採單一 coordinator 寫任務狀態、done 前驗收、重派前查 worker。**（推論）信心: 中。這是將來源中的分工、持久狀態及重播風險轉為共享 workspace 的操作約束；不是任何來源證明的最優演算法。它不能取代 runtime 鎖或處理所有多 coordinator race。

## 證據

| ID | 發布者／類型 | 日期 | 支持主張與採用範圍 |
| --- | --- | --- | --- |
| S1 | Anthropic／一手工程案例 | 2025-11-26；讀取 2026-10-02 | 功能清單、增量工作、交接與真實流程驗證；不照搬 200 項功能或 Git 自動操作 |
| S2 | OpenAI／一手工程案例 | 2026-02-11；讀取 2026-10-02 | 短入口、漸進讀取、計畫與決策 artifacts；不要求另建整套 knowledge base |
| S3 | Anthropic／一手系統案例 | 2025-06-13；讀取 2026-10-02 | 清楚 delegation、平行限制與成本；不外推研究任務的增益到 coding |
| S4 | Anthropic／一手應用實驗 | 2026-03-24；讀取 2026-10-02 | 明確 acceptance、evaluator 及模型改變後簡化 harness；不採其擴張產品範圍的做法 |
| S5 | LangChain／官方動態文件 | 未顯示發布日；讀取 2026-10-02 | checkpoint replay、idempotency、未完成 task 可能重跑；不引入 LangGraph dependency |
| S6 | Saransh Dhage／arXiv 預印本 | 2026-08-25，v1；讀取 2026-10-02 | 檢查 structured planning、模型相關成本及實驗外推限制；未自行重現 |

來源 URL 見下方 S1–S6 對應清單。日期依頁面本文，不以搜尋引擎相對時間推算。

## 矛盾與不確定性

**JSON 對 Markdown。** S1 的案例偏好 JSON，以降低 agent 改寫功能要求；S2 則使用 repo 中的計畫文件。沒有跨環境證據證明單一格式通用最優。本實作沿用既有 tracker／Markdown，要求 stable IDs、狀態與驗收不被任意改弱；若真實使用出現反覆狀態錯誤，再加入 schema validator。

**更多 agents 對更低 overhead。** S3 支持可平行研究；S4 的經驗顯示模型改善後可刪減部分流程。採用條件式分派與 QA，不常駐 planner/executor/reviewer/gate 四層角色。

**一致性對正確性。** S6 的固定線性任務不能代表任意程式修改；同一篇 abstract landing page 與 HTML 對達到完全 reproducibility 的 cell 數量出現差異，因此不引用該數字。相同結果可能仍然錯，必須以任務驗收衡量。

**日期與索引品質。** 另查到 [arXiv 2609.00006](https://arxiv.org/abs/2609.00006)，頁面顯示 2026-07-15 的提交日，與識別碼月份及搜尋日期訊號不一致。本次不將其列入核心證據，也不以摘要中的跨系統結論制定規則。

**Skill 的能力邊界。** 文件規則不是機械 enforcement；沒有檔案鎖、持久佇列、喚醒或原子狀態交易。多個彼此不知情的 coordinator、跨程序崩潰及遠端服務重播需要額外 runtime 能力，本次不聲稱已解決。

## 建議

（建議；信心: 中）交付一個精簡 `task-harness`：入口內含完整 workflow 與任務紀錄模板，不要求其他 skills；UI metadata 只負責探索。先驗證具體行為，再依失敗補強。

| 決策 | 本次採用 | 何時重新評估 |
| --- | --- | --- |
| 任務來源 | 一份既有 tracker 或符合專案規則的計畫文件 | 多 coordinator 必須同時更新時，需要原子 claim 能力 |
| 任務拆分 | 可驗收、依賴清楚、ownership 明確 | 任務持續超出上下文或交接失敗時再切細 |
| 分派 | 現有工具；無工具或無授權就串行 | 已量測 critical path 且可隔離寫入時增加平行 |
| 驗收 | direct checks，加上必要整合或獨立評估 | 主觀品質或高風險要求另加專門 evaluator |
| 重試 | 遵循 host policy，否則安全 transient 操作最多再試一次；無新證據不重複修補 | 系統已有 retry/backoff/idempotency 機制時沿用 |
| 記錄 | artifact 與測試版本、worker handle、blocker、下一步 | 出現 stale evidence 或重播事故，再增加機械檢查 |

## 未解問題

- 真實專案中 serial 與 parallel 的時間、token 消耗、返工率差異；本研究未作 benchmark。
- 長時間中斷、跨模型／平台工具差異與多 coordinator 衝突的頻率。
- 實際使用者是否需要外部 tracker 或 durable scheduler；目前沒有此授權或需求證據。
- 本次 isolated forward tests 可提供行為證據，不能代表生產環境的可靠性保證。

## 來源

- S1：[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)。
- S2：[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)。
- S3：[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)。
- S4：[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)。
- S5：[Functional API overview：Determinism、Idempotency](https://docs.langchain.com/oss/python/langgraph/functional-api)。
- S6：[Harness Engineering for Predictable Agentic Systems](https://arxiv.org/html/2608.26197v1)。
