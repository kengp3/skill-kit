public final class State {
    int orderTotal, refunds, restocked, gatewayCalls;
    String events = "";
    public String state() { return orderTotal + ":" + refunds + ":" + restocked + ":" + gatewayCalls + ":" + events; }
}
