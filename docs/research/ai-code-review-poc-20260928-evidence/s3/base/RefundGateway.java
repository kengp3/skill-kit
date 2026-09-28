final class RefundGateway {
    int attempts, successfulRefunds, refundedCents;
    boolean refund(int amountCents, boolean decline) {
        attempts++;
        if (decline) return false;
        successfulRefunds++;
        refundedCents += amountCents;
        return true;
    }
}
