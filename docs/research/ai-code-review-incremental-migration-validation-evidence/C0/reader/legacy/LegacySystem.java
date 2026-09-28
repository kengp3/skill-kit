import java.util.HashMap;
import java.util.Map;
public final class LegacySystem {
    int orderTotal, refunds, restocked, gatewayCalls;
    String events = "";
    Map<String, String> receipts = new HashMap<>();
    public String order(int net) {
        if (net < 0) return "INVALID";
        orderTotal += net + (net >= 8000 ? 0 : 500);
        events += "O";
        return "ORDER:" + orderTotal;
    }
    public String refund(String key, int ageDays, boolean decline) {
        if (receipts.containsKey(key)) return receipts.get(key);
        if (ageDays < 0 || ageDays > 30) return "EXPIRED";
        gatewayCalls++;
        if (decline) return "DECLINED";
        refunds++;
        restocked++;
        events += "R";
        String receipt = "REFUND:" + refunds;
        receipts.put(key, receipt);
        return receipt;
    }
    public String loyaltyStatus() { return "PENDING-MIGRATION"; }
    public String state() { return orderTotal + ":" + refunds + ":" + restocked + ":" + gatewayCalls + ":" + events; }
}
