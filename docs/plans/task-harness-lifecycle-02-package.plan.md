# H02：完整 hook 候選封裝

Status: done (source and offline package checks; actual agent behavior acceptance remains H05)
Blocked by: H01、H03
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：產生包含必要 hooks、handler、skill 與接入範本的新版本候選，離開 checkout 仍能使用；不安裝到日常宿主。

- [x] 三事件註冊、來源版本 0.2.0，無個人絕對路徑。
- [x] runtime-manifest 包含完整 hook 相依；缺檔/linked來源/篡改拒絕。
- [x] 新目錄建包/驗包與套件外 event CLI 驗證；舊 release 不變。

證據：[H02 封裝驗證](../research/task-harness-hooks-package-evidence/package.research.md)。三事件依實際註冊命令在含空白的臨時套件／專案路徑執行；8 項 package CLI 測試通過。未安裝候選或改宿主設定，Windows 原生命令與 Desktop 載入／信任仍未驗證。
