# G03 正常 hook 信任：人工審閱包

狀態：等待使用者審閱精確定義並明確授權正常 CLI 信任動作；目前五個均 untrusted。

- case：`/private/tmp/g03-persisted-trust-case`
- 專用 state：`/private/tmp/g03-persisted-trust-state`（0700；auth 0600，在 repo／證據外；不含於本包）
- 正常 CLI v0.164.0，`--no-daemon --no-alt-screen`，沒有任何 hook trust bypass。
- 活躍 exec session `49562`，TUI PID `98889`，`/dev/ttys000`。目前停在 Hooks browser，底部 `t trust all · enter review · esc close`。`t` 尚未按下。
- project trust 只是本 state 的 project layer 啟用前提，並非 hook trust。
- 來源：`/private/tmp/g03-persisted-trust-case/.codex/hooks.json`；原樣來自 demo 現行定義，檔案 SHA-256 `34ea12d470060c9a974d04efcbeca15dc9b97593731391282ea3b5afc681105f`。
- 候選 runtime-manifest SHA-256：`7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。四個候選 skills 完整複製非 scripts 檔案；HOME 三個 user skills disabled，native skills/list 已確認。

依原生警告，信任後 hooks 可在 sandbox 外執行。本包五個定義只使用固定 shell built-in echo；沒有讀檔、網路、參數插入或寫入。審閱仍以以下完整 JSON 為準（含 commandWindows）；本次 Windows 不執行。

## 原生識別與 hash

|事件|native currentHash|狀態|
|---|---|---|
|sessionStart|`sha256:bc609ea578c004f9041f03a87b1d223f3758fbb5863c03e742c4a72324db82ac`|untrusted|
|sessionStart|`sha256:6116e2284ddfb21371ece682e842fc25b53f56990491d10a10be4d221fd57e94`|untrusted|
|userPromptSubmit|`sha256:215f00dd83b3b7ec4eb0d9e87d4390e39b4e689b44539f38cf31cb46e8aea7a1`|untrusted|
|subagentStart|`sha256:b2d3784fb47a53909261e30eb5ab083c9604b836d2a6d26233a916231cc3ce02`|untrusted|
|stop|`sha256:fd38ca835821c2ff23955c47633aed21bb8956f38f137177f0c31fd0046dff5e`|untrusted|

每個來源 key、timeout、matcher、enabled、管理狀態及其他欄位見 [hooks-before.json](hooks-before.json)。

## 精確完整定義

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo project-setting: Before document operations, read project-setting.md at the project root confirmed by the user or session. Do not infer the root from tool cwd or use another project. If the root or rules are missing, unreadable, empty or conflicting, report and pause related document writes. Re-read changed rules and verify actual paths. This hook only reminds.",
            "commandWindows": "cmd /d /c echo project-setting: Before document operations, read project-setting.md at the project root confirmed by the user or session. Do not infer the root from tool cwd or use another project. If the root or rules are missing, unreadable, empty or conflicting, report and pause related document writes. Re-read changed rules and verify actual paths. This hook only reminds.",
            "timeout": 5
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo task-harness: For an explicitly enabled task read project-setting.md at the confirmed project root and the task-harness references. Restore the same task contract and verify authorization artifacts workers and unknown operations before action. If hooks are unavailable use model-led checks. This reminder does not activate a task or prove completion.",
            "commandWindows": "cmd /d /c echo task-harness: For an explicitly enabled task read project-setting.md at the confirmed project root and the task-harness references. Restore the same task contract and verify authorization artifacts workers and unknown operations before action. If hooks are unavailable use model-led checks. This reminder does not activate a task or prove completion.",
            "timeout": 5
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo project-setting: Before document operations, read project-setting.md at the project root confirmed by the user or session. Do not infer the root from tool cwd or use another project. If the root or rules are missing, unreadable, empty or conflicting, report and pause related document writes. Re-read changed rules and verify actual paths. This hook only reminds.",
            "commandWindows": "cmd /d /c echo project-setting: Before document operations, read project-setting.md at the project root confirmed by the user or session. Do not infer the root from tool cwd or use another project. If the root or rules are missing, unreadable, empty or conflicting, report and pause related document writes. Re-read changed rules and verify actual paths. This hook only reminds.",
            "timeout": 5
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo task-harness: Only for an explicitly enabled task re-read changed project-setting.md and reconcile the latest user instructions in the same task contract. Before dispatch or stage changes check prerequisites and model policy. After agent reports verify artifacts and evidence. Before closure check every necessary outcome and continue authorized executable work. Respect user Stop. This reminder grants no authorization and does not validate completion.",
            "commandWindows": "cmd /d /c echo task-harness: Only for an explicitly enabled task re-read changed project-setting.md and reconcile the latest user instructions in the same task contract. Before dispatch or stage changes check prerequisites and model policy. After agent reports verify artifacts and evidence. Before closure check every necessary outcome and continue authorized executable work. Respect user Stop. This reminder grants no authorization and does not validate completion.",
            "timeout": 5
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo {}",
            "commandWindows": "cmd /d /c echo {}",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## 核准後的最小操作

使用者完成上述精確定義審閱並明確核准後，才在既有 exec session 49562 的正常 Hooks browser 按 `t`；若宿主另彈確認，保留畫面再執行已核准的同一信任操作。不得用 hook API 信任或寫 trust 資料庫。隨後記錄 native hooks/list，讓同 state 先後兩個新 invocation 完成各自無破壞小任務，核對 actual developer reminders、hook events、turn terminal 與唯一合約／精確成果。完成第二次前保留 state 與認證。
