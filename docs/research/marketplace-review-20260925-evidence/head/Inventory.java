import java.util.LinkedHashMap;
import java.util.Map;
final class Inventory {
    final Map<String,Integer> stock = new LinkedHashMap<>();
    Inventory() { stock.put("KIT", 2); stock.put("ADDON", 5); }
    boolean known(String sku) { return stock.containsKey(sku); }
    boolean available(String sku, int qty) { return stock.get(sku) >= qty; }
    boolean reserve(String sku, int qty) {
        if (!available(sku, qty)) return false;
        stock.put(sku, stock.get(sku) - qty);
        return true;
    }
}
