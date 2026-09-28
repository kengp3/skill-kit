# 固定輸入與觀測比較

此 helper 用 Python 3.9+ 標準函式庫與 Git，不執行被審查程式，也不呼叫 AI／Joern。它檢查檔案完整性和觀測差異；agent 仍須審查案例、runner、映射及業務範圍。

## 固定兩個 repo/ref

以下 `SKILL` 表示已安裝技能的絕對目錄；所有路徑為示意，使用實際值。

```sh
python3 "$SKILL/scripts/review.py" prepare \
  --old-repo /path/legacy --old-ref refs/heads/release \
  --new-repo /path/replacement --new-ref refs/heads/migration \
  --out /path/new-review-run
python3 "$SKILL/scripts/review.py" verify --run /path/new-review-run
```

產物：manifest.json 與 snapshots/old、snapshots/new。只納入 commit 的普通檔案及 executable mode，不套用 export-ignore／export-subst，不自動 fetch。快照不得改寫或加入建置產物；編譯輸出放 run/build，需原地建置時另複製並核對輸入。未提交來源不納入，工作樹本身保持不動。

symlink、submodule、LFS pointer、大小寫碰撞或非 UTF-8 路徑不支援時明確停止。既有輸出拒絕覆寫；中途失敗目錄保留但沒有成功 manifest，檢查原因後用新 run 重試。不要以此失敗要求使用者刪除正常來源檔案；必要時另採經核對的取證方式。

verify 核對快照檔案集合、內容與 executable mode。分支之後移動不影響已固定版本；要審新版本就建立新 run。manifest 與紀錄是本機證據，不是防惡意偽造的簽章或執行證明。

## 契約與 runner

在執行之前固定 contract.json，最小例子：

```json
{
  "scope": "訂單重試的資料與事件行為",
  "artifacts": {"runner.py": "實際 SHA-256"},
  "cases": [{
    "id": "retry",
    "input": {"operations": ["create", "retry"]},
    "initial_state": {"orders": []},
    "environment": {"clock": "2026-01-01T00:00:00Z"},
    "observe": ["response", "state", "events", "error"]
  }]
}
```

artifacts 為 run 內相對路徑及實際內容 hash，納入影響結果的 runner、adapter、配置、輸入與狀態映射；依賴版本、JDK、外部 fixture 亦需記錄。不要把示意字串當 hash。observe 是必須擷取的欄位，任何一個缺少都不能通過該案例；空案例／空 observe 拒絕。

`observed` 的頂層欄位須與該案例 `observe` 一致。出現未宣告欄位會列 UNKNOWN，不能靜默忽略後 PASS；已有其他有效差異時仍維持 FAIL 並保留缺口。先確認新增觀測是否屬契約，再更新契約並重驗；診斷資訊留在原始 logs，不混入業務觀測，也不為了通過而刪除副作用證據。

agent 依專案既有工具執行並記錄命令、退出碼、stdout/stderr、原始觀測及初始狀態。只有程式真正執行成功，才將結果包裝如下。失敗／未執行不得手填 exit_code=0。

`command` 是非空的 argv 字串陣列；多個命令則使用非空的 argv 陣列清單。每個 argv 的第一項是非空程式名稱，其餘參數可為空字串，所有參數不得含 NUL。布林、數字、物件或整段 shell 字串不符合格式，列 UNKNOWN；格式有效仍不證明命令真的執行。

```json
{
  "side": "old",
  "commit": "該側完整 commit",
  "manifest_sha256": "manifest.json 的 SHA-256",
  "contract_sha256": "contract.json 的 SHA-256",
  "command": ["實際執行命令", "實際參數"],
  "exit_code": 0,
  "records": [{
    "id": "retry",
    "input": {"operations": ["create", "retry"]},
    "initial_state": {"orders": []},
    "environment": {"clock": "2026-01-01T00:00:00Z"},
    "observed": {
      "response": {"status": "created"},
      "state": {"orderCount": 1},
      "events": ["OrderCreated"],
      "error": null
    }
  }]
}
```

新側同格式，side=new、commit 對應新側。records 的 input、initial_state、environment 描述實際執行情境，必須與契約相符，不可只是複製契約卻未設定環境。不同 schema 的實際 fixture、raw output 與映射另存原始證據，審核投影不會抹掉差異。

使用相同業務案例，不要求兩側測試框架相同。Java 可先用原有 JUnit 或單獨 javac/java harness；保留真實程式碼，勿把舊演算法抄進 adapter 再測 adapter 自己。反射／代理／DB／MQ 未被實際執行時不得宣稱其已驗證。

## 比較與判讀

```sh
python3 "$SKILL/scripts/review.py" compare \
  --run /path/new-review-run \
  --contract /path/new-review-run/contract.json \
  --old /path/new-review-run/old.json --new /path/new-review-run/new.json \
  --out /path/new-review-run/comparison.json
```

退出碼 0＝所列案例一致，1＝存在有效差異，2＝UNKNOWN／輸入無效。UNKNOWN 也可能只出現在 stdout 的 error JSON（尚未能產生 comparison.json）；保留 log，不能因找不到報告就當零問題。報告檔拒絕覆寫。

比較器不排序陣列、不去重、不忽略額外業務值、不提供浮點容差。物件 key 排序只用於穩定序列化；false 與 0、null 與缺欄位不同。JSON 小數與指數數字一律拒絕，避免二進位浮點解析先損失精度而誤判相同；金額等精確小數使用十進位字串，整數可直接比較。不同表示需事先定義並驗證 adapter，不能看到差異後任意正規化。

有效觀測已有差異且別的欄位缺失時保留 FAIL 和 unknowns；來源／契約失效或 runner 執行失敗則該側資料不能作有效反例。檢查比較器輸出的 differences 與 raw output，排除映射或環境問題再形成業務 finding。

compare 不驗證「命令真的執行」「所有規則已發現」「artifact 清單列全」「映射正確」。這些仍是 agent 查核責任；需要更強執行可追溯性時使用既有 CI logs／測試產物，而非增加只驗證自己 JSON 的假證明。

同理，移轉 comparison 的 PASS 不取代 [migration.md](migration.md) 的雙向規則盤點、old-old 校準、已知反例檢查、一般品質 review 及必要狀態序列。正式證明須人工核對模型、假設與完整證明義務，helper 不接收自由文字 proof=true。
