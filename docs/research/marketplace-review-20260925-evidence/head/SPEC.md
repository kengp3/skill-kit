# Marketplace checkout refactor contract

The change extracts offer calculation into OfferEngine while preserving checkout behavior.
Each case starts with KIT stock 2, ADDON stock 5, empty success keys, zero points and events.
Prices are KIT 1200 cents and ADDON 350 cents. Quantity must be 1..5; unknown SKU is invalid.
For quantity >= 3, tier discount is floor(gross / 10). The coupon gives 150 cents only when
the amount AFTER the tier discount is >= 1000 cents. Payable = afterTier - coupon discount.
All monetary operations use integer cents. Successful points = floor(payable / 100).
Validate SKU/quantity, then check successful key replay before mutable stock availability.
Same key/same request replay returns the original result with no payment, stock, points or event change.
Only after stock availability and successful payment may stock, points, success cache and event change.
Payment decline increments chargeAttempts only and returns DECLINED; same key may retry.
Each success creates one Checkout event: key, sku, quantity, amountCents=payable, points=earned.
No stock means OUT_OF_STOCK without charging. Invalid input raises IllegalArgumentException.
Cases are sequential on independent instances. Keys are nonempty ASCII; identical key always has
the same SKU, quantity and coupon. No concurrency, real payment, persistence or message broker.
Review all source/diff targets plus compile and every step of the eight listed cases:
coupon_boundary, qualified_coupon, decline_retry, replay_exhausted, mixed, invalid,
out_of_stock, points. Required per-step fields: result, stockKit, stockAddon,
chargeAttempts, charges, chargedCents, points, completedKeys, events. Each event needs
key, sku, quantity, amountCents and earnedPoints. Exit code zero does not prove business PASS.
This is a local simulated pull request without a remote platform action.
