import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Checkout {
    final Inventory inventory = new Inventory();
    final Payment payment = new Payment();
    final Ledger ledger = new Ledger();
    final OfferEngine offers = new OfferEngine();
    final Map<String,String> completed = new LinkedHashMap<>();
    final List<Event> events = new ArrayList<>();
    String checkout(String key, String sku, int quantity, boolean coupon, boolean decline) {
        if (!inventory.known(sku) || quantity < 1 || quantity > 5)
            throw new IllegalArgumentException("invalid request");
        if (!inventory.reserve(sku, quantity)) return "OUT_OF_STOCK";
        if (completed.containsKey(key)) return completed.get(key);
        int payable = offers.payable(sku, quantity, coupon);
        if (!payment.charge(payable, decline)) return "DECLINED";
        ledger.earn(payable);
        String result = "OK:" + payable;
        completed.put(key, result);
        int gross = (sku.equals("KIT") ? 1200 : 350) * quantity;
        events.add(new Event(key, sku, quantity, gross, payable / 100));
        return result;
    }
}
