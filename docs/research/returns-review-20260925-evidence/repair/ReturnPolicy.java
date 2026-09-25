final class ReturnPolicy {
    int amountCents(Order order, int quantity) {
        return quantity * order.unitCents
            + (order.returnedQty + quantity == order.purchasedQty ? order.shippingCents : 0);
    }
}
