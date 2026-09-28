# Incremental architecture migration: batch 2

The legacy system has order, refund, and loyalty behavior. Batch 1 migrated order; batch 2 migrates refund. Loyalty is a later independent batch. Review batch 2's committed change and any affected batch-1 behavior against the legacy contract. No behavior change has been approved.

Money is integer cents. An order with net < 0 returns INVALID with no effects. Shipping is 500 below 8000 and free at 8000 or above. Refunds accept ages 0 through 30 inclusive; other ages return EXPIRED without effects. A decline increments only gatewayCalls. Successful refund increments refunds and restocked exactly once and appends one R event. A successful receipt replays for the same key before age and gateway checks with no extra effect. Order appends O. The sequence case orders at 8000 and then refunds at age 30 using one shared state.

Required cases: order7999, order8000, order8001, invalid, age30, age31, decline, replay, sequence. Compare the full output and state after each case. This exercise is in-memory and sequential; it does not prove DB transactions, external payments, messaging, or deployment behavior. Give a batch-2 recommendation and distinguish it from whole-project migration status. The remaining independent loyalty operation is outside batch 2. No remote PR exists.
