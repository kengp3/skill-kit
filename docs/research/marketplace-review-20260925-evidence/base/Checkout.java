import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Checkout {
    final Inventory inventory = new Inventory();
    final Payment payment = new Payment();
    final Ledger ledger = new Ledger();
    final Map<String,String> completed = new LinkedHashMap<>();
    final List<Event> events = new ArrayList<>();
    String checkout(String key, String sku, int quantity, boolean coupon, boolean decline) {
        if (!inventory.known(sku) || quantity < 1 || quantity > 5)
            throw new IllegalArgumentException("invalid request");
        if (completed.containsKey(key)) return completed.get(key);
        if (!inventory.available(sku, quantity)) return "OUT_OF_STOCK";
        int gross = (sku.equals("KIT") ? 1200 : 350) * quantity;
        int afterTier = gross - (quantity >= 3 ? gross / 10 : 0);
        int payable = afterTier - (coupon && afterTier >= 1000 ? 150 : 0);
        if (!payment.charge(payable, decline)) return "DECLINED";
        inventory.reserve(sku, quantity);
        ledger.earn(payable);
        String result = "OK:" + payable;
        completed.put(key, result);
        events.add(new Event(key, sku, quantity, payable, payable / 100));
        return result;
    }
}
