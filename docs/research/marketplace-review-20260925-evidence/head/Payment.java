final class Payment {
    int chargeAttempts, charges, chargedCents;
    boolean charge(int amountCents, boolean decline) {
        chargeAttempts++;
        if (decline) return false;
        charges++;
        chargedCents += amountCents;
        return true;
    }
}
