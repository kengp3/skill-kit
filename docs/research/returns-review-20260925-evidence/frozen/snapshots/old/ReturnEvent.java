final class ReturnEvent {
    final String key;
    final int quantity, amountCents;
    ReturnEvent(String key, int quantity, int amountCents) {
        this.key = key;
        this.quantity = quantity;
        this.amountCents = amountCents;
    }
    public String toString() {
        return "{\"key\":\"" + key + "\",\"quantity\":" + quantity
            + ",\"amountCents\":" + amountCents + "}";
    }
}
