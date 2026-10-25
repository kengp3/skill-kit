# AGENTS.md

本文件提供 Codex（Codex.ai/code）在此 repository 中處理程式碼時的指引。

## 開發 workflow

1. 先確認需求、範圍與可驗證的 acceptance criteria；只有資訊缺口會實質改變結果時才詢問使用者。
2. 以目前的 source code、tests、`pom.xml`、README、architecture docs 與 ADRs 作為 truth source；`.planning/` 僅為歷史封存。
3. 將工作拆成最小、可獨立驗證的 slices，並只做任務所需的變更。
4. 每個 slice 完成後執行相關檢查；交付前依風險執行完整 tests 或 build。
5. 完成 correctness、readability、architecture、security 與 performance review，修正所有 required findings 後才宣告完成。

`.planning/` 不得作為目前狀態或下一步的依據，也不得執行、建議或重新啟用其中記錄的舊 workflow commands 與 lifecycle tooling。

## 建置與執行命令

需要 Java 25 與全域 Maven 3.9+；此 repository 不含 Maven Wrapper files。

```bash
# Build (skipping tests)
mvn clean install -DskipTests

# Run the application
mvn spring-boot:run -pl channel-demo

# Run all tests
mvn test

# Run a single test class
mvn test -pl service-demo -am -Dtest=CopyThreadInfoParallelStreamTest -Dsurefire.failIfNoSpecifiedTests=false

# Run a single test method
mvn test -pl service-demo -am -Dtest=VirtualThreadParallelTest#testStructuredConcurrencyWithVirtualThreads -Dsurefire.failIfNoSpecifiedTests=false
```

> 測試與 compiler 需要 `--enable-preview`（`pom.xml` 已為 `maven-compiler-plugin` 與 `maven-surefire-plugin` 完成設定）。

## 專案目的

這是以 **Spring Boot 3.5.10 與 Java 25**（含 preview features）建立的 demo，用來探討如何在並行執行時，將以 `ThreadLocal` 為基礎的 `RequestContext` 傳遞到 worker 執行緒，並展示多種解決方案。

## 架構概覽

### 展示的核心問題

Spring 的 `@RequestScope` beans 與 `RequestContextHolder` 依賴 `ThreadLocal`。當工作轉交給 worker 執行緒（透過 `parallelStream()`、`CompletableFuture` 或 virtual threads）時，worker 執行緒沒有 `RequestContext`，因而造成 `ScopeNotActiveException`。

### 元件

**`config/AsyncConfig`** — 定義兩個皆使用 `ContextPropagatingTaskDecorator`（Spring Framework 6.2 官方實作）的 executors：
- `requestAwareExecutor`（`ThreadPoolTaskExecutor`）— platform threads
- `virtualRequestAwareExecutor`（`SimpleAsyncTaskExecutor`、`virtualThreads=true`）— virtual threads（建議使用）
- 也會註冊 `ConcurrentRequestScope`，並確保 Micrometer `ContextRegistry` 中存在 `RequestAttributesThreadLocalAccessor`（`ContextPropagatingTaskDecorator` 必須靠它擷取 `RequestContextHolder`）。

**`config/ConcurrentRequestScope`**（位於 `common`）— 自訂 Spring `Scope` 實作，使用 static `ConcurrentHashMap` + `computeIfAbsent()`，為每個 request 進行 atomic bean creation。以底層 `HttpServletRequest` 作為 scope key（可處理 `SnapshotServletRequestAttributes` wrappers），並透過 `NodeGuardConfig.concurrentRequestScopeRegistrar()` BeanFactoryPostProcessor 註冊。

**`config/HttpClientConfig`** — 提供 pooled `CloseableHttpClient` bean（Apache HttpClient 5），包含 TLS trust-all、keep-alive、idle eviction 與 retry strategy。

**`service/RequestScopeService`** — `@RequestScope` bean；每個 request lifecycle 產生一個 UUID。

**`service/NormalSingletonService`** — 透過 CGLIB proxy 委派給 `RequestScopeService` 的 Singleton（Spring 每次呼叫時都從 `ThreadLocal` 查找 scoped bean）。

**`ThreadLocalParallelStreamDemo`** — 獨立的 `main()` class（不是 Spring component），展示原始 `ThreadLocal` 在 `parallelStream()` 中遺失 context 與發生 dirty read 的問題，以及 closure variable + `try-finally` 修正方式。

### 測試類別（真正的核心內容）

| 測試 | 證明內容 |
|---|---|
| `RequestScopeParallelStreamTest` | 問題：`@RequestScope` 在 `parallelStream()` worker 執行緒中失敗 |
| `NormalServiceParallelStreamTest` | 問題：透過 singleton → scoped-bean proxy 時同樣失敗 |
| `CopyThreadInfoParallelStreamTest` | 解法 1：在 stream 前手動擷取 `RequestAttributes`，並在每個 worker 的 `try-finally` 中進行 set/reset |
| `TaskDecoratorParallelTest` | 解法 2：使用 `CompletableFuture` + `requestAwareExecutor`（搭配 `TaskDecorator`） |
| `VirtualThreadParallelTest` | 解法 3：Java 21+ `ScopedValue` + `StructuredTaskScope` — child virtual threads 會自動繼承 `ScopedValue` |
| `ServiceInternalParallelStreamTest` | 3-layer 問題展示：ScopeNotActiveException → 競態條件（race condition）→ 跨請求隔離 |
| `ParallelRequestScopeRaceConditionTest` | **完整重現競態條件並展示 5 種解法**（A-1、A-2、B、C、D、E），依 `@Order` 順序執行 |
| `BestPracticeParallelServiceTest` | **最終 best practice**：使用 Spring Boot 3.5 + Java 25 APIs 的 4 種情境 |

### 關鍵 patterns

- **解法 A-1（預先擷取唯讀值）**：在 main thread 從 `@RequestScope` bean 擷取 immutable values，作為 closure variables。零風險。
- **解法 A-2（預先擷取 + 延後寫入）**：並行階段只進行純計算；並行處理完成後，由 main thread 寫入 `@RequestScope` bean。
- **解法 B/D（預熱 + ContextPropagatingTaskDecorator）**：main thread 先呼叫 bean 一次，強制在 `RequestAttributes` 中完成初始化（預熱）。接著由 `ContextPropagatingTaskDecorator` 將同一份 `RequestAttributes` 傳遞給每個 worker。Workers 找到非 null 的 `getAttribute()` → 使用單一 instance，不會發生競態。**D 另加入 virtual threads**（建議使用）。
- **解法 C（ScopedValue + StructuredTaskScope）**：Java 25 preview 作法。並行 workers 完全繞過 `@RequestScope`；immutable values 透過 `ScopedValue` 流動，並行處理完成後由 main thread 寫回 mutable state。
- **解法 E（ConcurrentRequestScope）**：使用 atomic `computeIfAbsent` 的自訂 `Scope`，不需要預熱。必須將 bean annotation 從 `@RequestScope` 改為 `@Scope("concurrentRequest")`。
- **解法 F（ConcurrentRequestScope + ConcurrentRequestAuditService）**：與 E 相同，但使用專用的 `@Scope("concurrentRequest")` audit service（`ConcurrentRequestAuditService`），其 mutable fields 採用 thread-safe types（`Collections.synchronizedList`）。

### Java 25 API 狀態（`--enable-preview` 決策的關鍵）

| API | 定案版本 | Java 25 狀態 | 需要 `--enable-preview`？ |
|-----|-------------|---------------|--------------------------|
| Virtual Threads | Java 21（JEP 444） | Stable ✅ | 否 |
| `ScopedValue` | Java 24（JEP 487） | Stable ✅ | **否** |
| `StructuredTaskScope` | 尚未定案（JEP 505 = 第 4 次 Preview） | **Preview** ⚠️ | **是** |

> **重要**：`ScopedValue` 在 **Java 24 已定案**，不是 Java 25。在 Java 25 中，`ScopedValue` 是完全 stable 的 API，不需要 `--enable-preview`。截至 Java 25，`StructuredTaskScope` 仍處於第 4 次 Preview，且需要 `--enable-preview`。

### Spring Boot 3.5 + Java 25 關鍵設定

`ContextPropagatingTaskDecorator`（Spring Framework 6.2）要求手動在 `ContextRegistry.getInstance()` 中註冊 `RequestAttributesThreadLocalAccessor`。Spring Boot **不會**自動註冊。

```java
// In AsyncConfig @PostConstruct — with duplicate registration guard
ContextRegistry registry = ContextRegistry.getInstance();
boolean alreadyRegistered = registry.getThreadLocalAccessors().stream()
        .anyMatch(a -> a instanceof RequestAttributesThreadLocalAccessor);
if (!alreadyRegistered) {
    registry.registerThreadLocalAccessor(new RequestAttributesThreadLocalAccessor());
}
```

若缺少此設定，`ContextSnapshot.captureAll()` 無法擷取 `RequestContextHolder`，即使使用 `ContextPropagatingTaskDecorator`，worker 執行緒仍會拋出 `ScopeNotActiveException`。

### NodeGuard × 多執行緒使用規範（v3）

`NodeContext` 是 **`@Scope("concurrentRequest")` bean** — 每個 HTTP request 一個 instance，且該 request 內的所有執行緒會共享它。不使用 ThreadLocal，也不需要手動清理 filter。

#### Whitelist 語意 — Ancestor（非直接 predecessor）
`hasAnyVisited(allowedCallers)` 會檢查 request history 中的**任一 node**是否存在於 allowed list。這讓 Facade layers 可以在經過單一 gateway node 後，呼叫多個 downstream services：

```java
// ✅ Both BackendA and BackendB can be called since Gateway is in history
gateway.enter();                      // history: ["Gateway"]
backendA.process(id);                 // allowed: [Gateway] ✓  history: [..., "BackendA"]
backendB.process(id);                 // allowed: [Gateway] ✓  still true (ancestor semantics)
```

#### 自動傳遞（零樣板程式碼）
使用 `requestAwareExecutor` 或 `virtualRequestAwareExecutor` — `ContextPropagatingTaskDecorator` 會自動傳遞 `RequestContextHolder`（透過在 `NodeGuardConfig` 註冊的 `RequestAttributesThreadLocalAccessor`）。Worker 執行緒會存取**同一個** `NodeContext` bean instance。

```java
// ✅ Auto-propagated — NodeContext bean accessible in worker
CompletableFuture.supplyAsync(() -> bizService.doWork(), virtualRequestAwareExecutor);
```

#### `parallelStream()` 必須手動包裝
`parallelStream()` 使用 `ForkJoinPool.commonPool()`，不受 executor decorator 控制。**一律必須使用 `NodeContextPropagator.wrap()` 包裝**（它使用 `ContextSnapshot.captureAll()` 擷取 `RequestContextHolder`）：

```java
import com.example.common.nodeguard.context.NodeContextPropagator;

// ✅ Correct — RequestContextHolder propagated → NodeContext bean accessible
List<String> results = productIds.parallelStream()
    .map(NodeContextPropagator.wrap(pid -> bizService.process(pid)))
    .toList();

// ❌ Wrong — worker has no RequestContext → ScopeNotActiveException
List<String> results = productIds.parallelStream()
    .map(pid -> bizService.process(pid))
    .toList();
```

#### 共享 state — workers 與 main thread 共享同一個 NodeContext
同一 request 內的所有 workers 都共享同一個 `NodeContext` bean。任一 worker 的 records 對 main thread 與其他 workers 都可見：

```java
// main thread after parallel completes can see what workers recorded
gateway.enter();                      // history: ["Gateway"]
productIds.parallelStream()
    .map(NodeContextPropagator.wrap(pid -> orderBizService.createOrder(...)))
    .toList();
// nodeContext.getHistory() now contains ["Gateway", "OrderBizService"] (workers recorded it)
auditService.log(...);               // allowed-callers=["OrderBizService"] ✓ (already in history)
```

#### 進入時記錄語意（NodeAspect design）
`NodeAspect.executeAndUpdate()` 會在 `pjp.proceed()` **之前**呼叫 `nodeContext.record(nodeName)`。這是必要規則，因為在 `@Node` method body *內部*啟動的並行 workers，執行期間必須能在 history 中看到目前 node：

```java
@Node("CheckoutBizService")
List<String> processItems(List<CartItem> items) {
    // At this point, NodeAspect has ALREADY recorded "CheckoutBizService" (record-at-entry).
    // The parallelStream workers can now see "CheckoutBizService" in history and pass
    // their whitelist check (allowed-callers: [CheckoutBizService]).
    return items.parallelStream()
        .map(NodeContextPropagator.wrap(item -> stockClient.check(item.productId())))
        .toList();
}
```

副作用：即使 method 拋出 exception，node 仍會被記錄。測試必須反映此行為 — 應使用 `assertTrue(history.contains(nodeName))`，不得斷言該 node 不存在。

#### Flow 4 — Checkout（CF outer + parallelStream inner）

以下是展示 NodeGuard whitelist 兩層並行傳遞的完整 call chain：

```
POST /node-guard/checkout/{userId}
  CheckoutController  @Node("CheckoutController")     [無 allowed-callers — 進入點]
  └── CheckoutFacadeService                           [無 @Node — 透明委派]
        ├── CF#1: virtualRequestAwareExecutor (virtual thread)
        │     UserBizService  @Node("UserBizService") [allowed: CheckoutController, UserController]
        │       └── ThirdPartyClient @Node("UserClient") [allowed: UserBizService]
        └── CF#2: virtualRequestAwareExecutor (virtual thread)
              CheckoutBizService @Node("CheckoutBizService") [allowed: CheckoutController]
                └── items.parallelStream() + NodeContextPropagator.wrap()
                      ├── StockClient   @Node("StockClient")   [allowed: CheckoutBizService]
                      └── CatalogClient @Node("CatalogClient") [allowed: CheckoutBizService]
```

CF outer + parallelStream inner 不是禁止使用的 pattern（P-5a），原因如下：
- CF outer 使用 `virtualRequestAwareExecutor` → JEP 444 virtual thread scheduler（獨立 pool）
- parallelStream inner 使用 `ForkJoinPool.commonPool()`（不同的 pool instance）
- 兩個 pools 完全獨立 → 沒有 deadlock 風險

#### TaskContext — request metadata 傳遞

`TaskContext extends NodeContext` — channel-demo 中具體的 `@Scope("concurrentRequest")` bean，由 `TaskContextInterceptor.preHandle()` 初始化：

```java
// Fields populated once per request (thread-safe reads — immutable after init):
taskContext.getRequestId()   // from "x-request-id" header, or UUID auto-generated
taskContext.getMethod()      // HTTP method (GET, POST...)
taskContext.getPath()        // request URI path
taskContext.getClientIp()    // X-Forwarded-For or remoteAddr
```

`TaskContextInterceptor` 已在 `WebConfig.addInterceptors()` 中註冊，套用 path 為 `/node-guard/**`。

#### Bypass endpoint 模式

`POST /node-guard/checkout/{userId}/bypass` 沒有 `@Node` annotation。NodeContext history 會維持空白 → 第一個含 `allowed-callers` 的 downstream `@Node` service 會拋出 `NodeAccessDeniedException` → `GlobalExceptionHandler` 回傳 HTTP 403 + code `4030`。

注意：如果 exception 是在 `CompletableFuture` 內拋出，會被包裝成 `CompletionException`。`GlobalExceptionHandler` 會處理 `CompletionException`、解開其 cause，並回傳正確的 HTTP status。

#### 多執行緒問題的證明測試（NodeGuardMultiThreadProblemProofTest）

`common` 模組中有 11 個測試，證明錯誤的並行 patterns 會失敗，而正確解法可通過：

| 群組 | 測試 | 模式 |
|-------|------|---------|
| P-1 | `p1_facadeParallelStream_withoutWrap_workerThrows` | 未加 `wrap()` 的 `parallelStream()` → 沒有 RequestContext |
| P-2 | `p2_unmanagedCF_workerThrows` | 搭配 unmanaged executor 的 `CompletableFuture` |
| P-3 | `p3_bizServiceParallelStream_withoutWrap_clientThrows` | 未加 `wrap()` 的內層 `parallelStream()` |
| P-4 | `p4_managedCFouter_noWrapInner_innerThrows` | Managed CF outer + 未加 wrap 的 inner parallelStream |
| P-5a | `p5a_nestedParallelStream_innerWorkerThrows` | 巢狀 parallelStream（兩者皆使用 commonPool） |
| P-5b | `p5b_unmanagedVirtualThread_throws` | 未傳遞 context 的 `Thread.ofVirtual().start()` |
| S-1 | `s1_facadeParallelStream_withWrap_allPass` | `parallelStream()` + `NodeContextPropagator.wrap()` |
| S-2 | `s2_managedCF_contextPropagated_passes` | `CompletableFuture` + managed executor |
| S-3 | `s3_managedCFouter_withWrapInner_allPass` | CF outer + 已加 `wrap()` 的 inner |
| S-4 | `s4_requestIsolation_historyNotLeaked` | 新 request → 全新的 NodeContext |
| S-5 | `s5_workersShareNodeContext_workerRecordsVisibleToMainThread` | Workers 共享 bean |

P-測試使用 `assumeTrue(exCount.get() > 0, "parallelStream 退化，跳過")`，因此在 single-core CI environment 中，若 `parallelStream()` 退化為 sequential execution，會安全地略過測試。
