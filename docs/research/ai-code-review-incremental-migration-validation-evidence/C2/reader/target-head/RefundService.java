import java.util.HashMap;
import java.util.Map;
public final class RefundService {
    private final State state;
    private final Map<String, String> receipts = new HashMap<>();
    public RefundService(State state) { this.state = state; }
    public String refund(String key, int ageDays, boolean decline) {
        if (receipts.containsKey(key)) return receipts.get(key);
        if (ageDays < 0 || ageDays > 30) return "EXPIRED";
        state.refunds++;
        state.gatewayCalls++;
        if (decline) return "DECLINED";
        Warehouse.restock(state);
        state.events += "R";
        String receipt = "REFUND:" + state.refunds;
        receipts.put(key, receipt);
        return receipt;
    }
}
