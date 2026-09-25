import java.util.stream.Collectors;
public final class Probe {
    static void step(Checkout c, String key, String sku, int quantity, boolean coupon, boolean decline) {
        String result;
        try { result = c.checkout(key, sku, quantity, coupon, decline); }
        catch (IllegalArgumentException e) { result = "IllegalArgumentException"; }
        String keys = c.completed.keySet().stream().map(k -> "\"" + k + "\"")
            .collect(Collectors.joining(",", "[", "]"));
        String events = c.events.stream().map(Event::toString).collect(Collectors.joining(",", "[", "]"));
        System.out.println("{\"result\":\"" + result + "\",\"stockKit\":" + c.inventory.stock.get("KIT")
            + ",\"stockAddon\":" + c.inventory.stock.get("ADDON")
            + ",\"chargeAttempts\":" + c.payment.chargeAttempts
            + ",\"charges\":" + c.payment.charges
            + ",\"chargedCents\":" + c.payment.chargedCents
            + ",\"points\":" + c.ledger.points
            + ",\"completedKeys\":" + keys + ",\"events\":" + events + "}");
    }
    public static void main(String[] args) {
        Checkout c = new Checkout();
        switch (args[0]) {
            case "coupon_boundary": step(c,"a","ADDON",3,true,false); break;
            case "qualified_coupon": step(c,"a","KIT",1,true,false); break;
            case "decline_retry": step(c,"a","KIT",1,false,true); step(c,"a","KIT",1,false,false); break;
            case "replay_exhausted": step(c,"a","KIT",2,false,false); step(c,"a","KIT",2,false,false); break;
            case "mixed": step(c,"a","KIT",1,true,false); step(c,"b","ADDON",3,true,false);
                step(c,"a","KIT",1,true,false); break;
            case "invalid": step(c,"a","BAD",1,false,false); step(c,"b","KIT",0,false,false); break;
            case "out_of_stock": step(c,"a","KIT",3,false,false); break;
            case "points": step(c,"a","ADDON",2,false,false); break;
            default: throw new IllegalArgumentException("unknown case");
        }
    }
}
