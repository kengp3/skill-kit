public final class OrderService {
    private final State state;
    public OrderService(State state) { this.state = state; }
    public String order(int net) {
        if (net < 0) return "INVALID";
        state.orderTotal += net + Policy.shipping(net);
        state.events += "O";
        return "ORDER:" + state.orderTotal;
    }
}
