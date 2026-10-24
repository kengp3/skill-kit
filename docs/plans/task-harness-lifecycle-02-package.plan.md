# H02：完整 hook 候選封裝

Status: ready-for-agent
Blocked by: H01、H03
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：產生包含必要 hooks、handler、skill 與接入範本的新版本候選，離開 checkout 仍能使用；不安裝到日常宿主。

- [ ] 三事件註冊、來源版本 0.2.0，無個人絕對路徑。
- [ ] runtime-manifest 包含完整 hook 相依；缺檔/linked來源/篡改拒絕。
- [ ] 新目錄建包/驗包與套件外 event CLI 驗證；舊 release 不變。
