final class OfferEngine {
    int payable(String sku, int quantity, boolean coupon) {
        int gross = (sku.equals("KIT") ? 1200 : 350) * quantity;
        int afterTier = gross - (quantity >= 3 ? gross / 10 : 0);
        return afterTier - (coupon && gross >= 1000 ? 150 : 0);
    }
}
