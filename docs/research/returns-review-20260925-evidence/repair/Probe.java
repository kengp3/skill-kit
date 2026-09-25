import java.util.stream.Collectors;
public final class Probe {
    static void step(Returns service, String scenario, int step, String key,
                     int quantity, int ageDays, boolean decline) {
        String result = service.returnItems(key, quantity, ageDays, decline);
        String keys = service.receipts.keySet().stream().map(k -> "\"" + k + "\"")
            .collect(Collectors.joining(",", "[", "]"));
        String events = service.events.stream().map(ReturnEvent::toString)
            .collect(Collectors.joining(",", "[", "]"));
        System.out.println("{\"case\":\"" + scenario + "\",\"step\":" + step
            + ",\"result\":\"" + result + "\",\"returnedQty\":" + service.order.returnedQty
            + ",\"restockedQty\":" + service.warehouse.restockedQty
            + ",\"refundAttempts\":" + service.gateway.attempts
            + ",\"successfulRefunds\":" + service.gateway.successfulRefunds
            + ",\"refundedCents\":" + service.gateway.refundedCents
            + ",\"reversedPoints\":" + service.loyalty.reversedPoints
            + ",\"receiptKeys\":" + keys + ",\"events\":" + events + "}");
    }
    public static void main(String[] args) {
        String scenario = args[0];
        Returns s = new Returns();
        switch (scenario) {
            case "partial_final":
                step(s,scenario,1,"a",1,15,false); step(s,scenario,2,"b",2,15,false); break;
            case "day30": step(s,scenario,1,"a",1,30,false); break;
            case "decline_retry":
                step(s,scenario,1,"a",1,10,true); step(s,scenario,2,"a",1,10,false); break;
            case "replay_full":
                step(s,scenario,1,"a",3,10,false); step(s,scenario,2,"a",3,10,false); break;
            case "replay_expired":
                step(s,scenario,1,"a",1,10,false); step(s,scenario,2,"a",1,31,false); break;
            case "too_many": step(s,scenario,1,"a",4,10,false); break;
            case "after_window": step(s,scenario,1,"a",1,31,false); break;
            case "normal": step(s,scenario,1,"a",1,10,false); break;
            default: throw new IllegalArgumentException("unknown case");
        }
    }
}
