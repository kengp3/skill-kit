# 修正 Spring context 關閉後的 TTL cleanup

此 workspace 是既有專案的歷史版本，只包含 root POM 與 concurrent-request-scope 模組。

啟用 TTL cleanup 時，Spring ApplicationContext 關閉後仍可能有該 scope 的背景清理活動。請修正其生命週期：關閉 context 後停止屬於它的背景工作，釋放由它持有的資源，並保留正常 request scope、TTL cleanup 與其他仍存活 context 的行為。共用資源應依實際所有權處理，不指定實作介面或 callback 寫法。

允許修改此 workspace 的 production code 與新增回歸測試。保留既有測試的驗證強度，不修改 harness、宿主設定或其他 checkout。只使用本 workspace 與本組提供的 harness 材料；不查找歷史修正、評測答案或其他組結果。

Java 25 與 Maven 3.9+ 已可用。已驗證的局部基線入口為：

```sh
mvn -B -o -f concurrent-request-scope/pom.xml \
  -Dtest=ConcurrentRequestScopePropertiesTest,ConcurrentRequestScopeCreationTest test
```

原始 AGENTS 的完整多模組命令在此局部歷史 workspace 不一定適用。依修改風險選擇並實際執行適當檢查，交付修改、結果、證據與未驗證限制。完整修復仍由外部驗收確認。
