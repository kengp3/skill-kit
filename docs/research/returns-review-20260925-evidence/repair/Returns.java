import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Returns {
    final Order order = new Order();
    final Warehouse warehouse = new Warehouse();
    final RefundGateway gateway = new RefundGateway();
    final Loyalty loyalty = new Loyalty();
    final ReturnPolicy policy = new ReturnPolicy();
    final Map<String,String> receipts = new LinkedHashMap<>();
    final List<ReturnEvent> events = new ArrayList<>();
    String returnItems(String key, int quantity, int ageDays, boolean decline) {
        if (receipts.containsKey(key)) return receipts.get(key);
        if (quantity < 1 || ageDays < 0 || ageDays > 30) return "REJECTED";
        if (order.returnedQty + quantity > order.purchasedQty) return "NO_QUANTITY";
        int amountCents = policy.amountCents(order, quantity);
        if (!gateway.refund(amountCents, decline)) return "DECLINED";
        order.returnedQty += quantity;
        warehouse.restock(quantity);
        loyalty.reverse(quantity * order.unitCents / 100);
        String result = "REFUNDED:" + amountCents;
        receipts.put(key, result);
        events.add(new ReturnEvent(key, quantity, amountCents));
        return result;
    }
}
