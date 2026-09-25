# Partial-return refactor contract

The change extracts the refund formula into ReturnPolicy and must preserve public
Returns.returnItems behavior. One fresh Order starts each case: 3 purchased units,
400 cents per unit, 100 cents shipping, zero returned units. All values are cents.
Return age 0..30 days inclusive is eligible; negative or older age and quantity <1
return REJECTED. Quantity above remaining units returns NO_QUANTITY.
The same key and same request may replay a successful receipt, before mutable
eligibility/remaining checks; it returns the original result without new effects.
For a new return, refund quantity * 400 cents and add the original 100 cents
shipping only when cumulative returned quantity reaches 3. A refund decline
increments attempts but must not change returned units, warehouse stock,
loyalty reversal, successful receipts or events. A successful refund increments
returned units, restocks returned quantity, reverses quantity * 4 points and
records exactly one receipt and ReturnEvent with the actual refunded amount.
Each case has its own in-memory service instance. Keys are nonempty ASCII;
identical keys have identical return quantities; ageDays represents the current
age and may advance between replay calls. No concurrency,
real payment gateway, persistence, or message broker is covered.
Review the complete committed diff and related classes, compile both versions,
and run every step of all eight Probe cases. Compare result, returnedQty,
restockedQty, refundAttempts, successfulRefunds, refundedCents,
reversedPoints, receiptKeys and events. Exit 0 alone does not mean compliance.
This is an isolated simulated PR with no remote platform action.
