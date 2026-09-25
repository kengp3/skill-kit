final class Event {
    final String key, sku;
    final int quantity, amountCents, earnedPoints;
    Event(String key, String sku, int quantity, int amountCents, int earnedPoints) {
        this.key = key; this.sku = sku; this.quantity = quantity;
        this.amountCents = amountCents; this.earnedPoints = earnedPoints;
    }
    public String toString() {
        return "{\"key\":\"" + key + "\",\"sku\":\"" + sku
            + "\",\"quantity\":" + quantity + ",\"amountCents\":" + amountCents
            + ",\"earnedPoints\":" + earnedPoints + "}";
    }
}
