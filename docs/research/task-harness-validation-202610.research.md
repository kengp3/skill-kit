# Task Harness 行為驗證

## 執行摘要

- 截至 **2026-10-02（Asia/Taipei）**，三個隔離 forward tests 通過：plan-only、原生 subagent 分派與整合、過期證據與未知副作用的 resume。
- 主 agent 讀取最終計畫、實作及驗證紀錄，另重跑 fixture checks 與 extended integration checks，皆 exit 0。
- Skill runtime 只有 `SKILL.md`；`agents/openai.yaml` 提供探索資訊，不需要 Python、其他 skills 或 framework。
- 無全域安裝、commit、push 或發布。未驗證並行寫入壓力、長時間運行與真實遠端副作用。

## 研究問題

這個 skill 是否能在實際工具環境中維持「規劃不等於執行」、「回報成功不等於通過驗收」、「resume 不等於重播」的界線？

## 範圍與假設

測試在 `/private/tmp/task-harness-eval-g4vluulh/` 進行；完整 fixture 快照保存在 [task-harness-202610-evidence](task-harness-202610-evidence/)。歷史文件內保留原始暫存路徑，重跑程式以自身所在目錄定位。

受測 SKILL.md SHA-256：`d07d527704445ecb4e1dd3a9279dc7c913d1a3b33d662e11887d41dc38084424`，與交付版本一致。UI metadata 在測試 fixture 建立後產生，未參與行為測試；其格式另經 generator／validator 檢查。

## 方法

依已指定 skill-creator 的 independent forward-testing，以三個未繼承本次對話的 agent 讀取獨立複本、原始 fixture、任務及可寫範圍。未提供作者預期結論或修正方向。execute 情境允許最多兩名子 agent；實際使用一名，未為測試人數而強行拆細。

直接讀回各任務清單、程式與 evidence，再在保留的快照中重跑 checks。停止條件為三項情境取得最終結果、主 agent 重驗通過、skill 與研究文件格式檢查通過；不把測試 agent 的「已完成」訊息單獨當證據。

## 主要發現

- **此情境遵守只規劃的界線。**（推論）信心: 高。依據 T1 → T2 的 pending 計畫、待執行驗證標記、app.py 與其他原檔不變及沒有新增實作檔，判定符合本次範圍。證據：[plan.md](task-harness-202610-evidence/plan/plan.md)。
- **此情境完成分派與整合驗收。**（推論）信心: 高。依據 `/root/eval_execute/helpers` 的工具回傳及 coordinator 重跑 check.py、額外整合測試的結果判定，沒有只採信 worker 的結論。證據：[result.md](task-harness-202610-evidence/execute/evidence/result.md)。
- **此情境能辨識過時 done。**（推論）信心: 高。依據現有 check.py 失敗後重開 T1、修正共享函式及重新驗證的紀錄判定。證據：[resume-verification.md](task-harness-202610-evidence/resume/evidence/resume-verification.md)。
- **此情境避免了重送。**（推論）信心: 高。依據權威 deliveries.txt 最終仍恰好一筆及執行紀錄未再次呼叫寄送程式判定；不外推為遠端 exactly-once 保證。證據：[verification.json](task-harness-202610-evidence/verification.json)。

## 證據

| 情境 | 觀察結果 | 主 agent 檢查 |
| --- | --- | --- |
| plan-only | 有 scope、assumptions、DoD、owner、依賴及待執行命令，實作保持 pending | 讀回計畫；比對 app.py 原文、原始檔案與 source fingerprints |
| execute | 真實 spawn 取得 worker handle；T1 完成後 coordinator 驗證 T2 | `python3 -B check.py` 及 `python3 -B evidence/verify_integration.py` 通過 |
| resume | 舊紀錄保留但不當 current acceptance；修正後 T1/T2 done | `python3 -B check.py` 通過，delivery exact-byte check 通過 |
| standalone | 三份隔離 SKILL.md 均與交付 hash 相符，無 repo-root runtime references | 運行時不需 repo 中其他 skills 或資料檔 |
| metadata／文件 | 使用既有 PyYAML cache 執行官方工具，未安裝套件 | skill validator、research validator、diff whitespace 檢查通過 |

重跑保留快照的直接檢查：

```bash
python3 -B docs/research/task-harness-202610-evidence/verify.py
python3 -B docs/research/task-harness-202610-evidence/execute/evidence/verify_integration.py
```

格式驗證（本機工具路徑，非 skill 使用依賴）：

```bash
PYTHONPATH=/Users/kengp3/.cache/uv/archive-v0/s3OOPVWJ0Hw7jhwA0lvuR/lib/python3.13/site-packages python3 /Users/kengp3/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-harness
python3 /Users/kengp3/.codex/skills/deep-research/scripts/validate_research_report.py docs/research/task-harness-202610.research.md
git diff --check
```

第一次 validator 執行發現預設與 bundled Python 都沒有 PyYAML；改用既有 uv cache 的 package path 後通過。研究報告第一次格式檢查指出推論標籤不符合 parser 格式，修正標籤後通過。這些是驗證環境／報告格式修正，未改變受測 skill 行為。

## 矛盾與不確定性

僅有三個小型情境，不能估計成功率；同一模型家族的獨立 context 不等於跨模型獨立驗證。checks 證明 fixture 的具體功能，不能機械證明 skill 在所有未來任務的決策。plan-only 未執行功能檢查是符合範圍，不是漏驗實作。

execute 測到一名 worker 與 coordinator 的分派／整合，沒有同時啟動兩名寫入 worker。未測依賴循環輸入、worker crash/takeover、取消、預算耗盡、跨 worktree merge、多 coordinator、長期 session 或真實服務的 idempotency。

## 建議

（建議）信心: 中。此版本可用於授權範圍內的實際工作。下一次依具體任務使用並觀察返工與協調成本；只有證據顯示 Markdown state 或現有 runtime 不足時，才加入 schema validator、原子 claim 或 durable scheduler。

## 未解問題

仍需真實專案衡量 task 粒度、平行數與驗證成本；本次未設定或宣稱通用效能數字。獨立可攜帶已驗證，平台自動探索與全域安裝尚未實測。

## 來源

本報告的測試結論依本地 artifacts；外部資料僅說明測試選擇，不能替代測試證據：

- [任務研究與來源分析](task-harness-202610.research.md)。
- [Anthropic：incremental progress 與測試](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)。
- [Anthropic：多 agent 分工及評估](https://www.anthropic.com/engineering/multi-agent-research-system)。
- [LangChain：idempotency 與 replay](https://docs.langchain.com/oss/python/langgraph/functional-api)。
