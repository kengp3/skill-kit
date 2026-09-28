public final class Probe {
    public static void main(String[] args) {
        State state = new State(); OrderService orders = new OrderService(state); RefundService refunds = new RefundService(state);
        String output;
        switch (args[0]) {
            case "order7999": output = orders.order(7999); break;
            case "order8000": output = orders.order(8000); break;
            case "order8001": output = orders.order(8001); break;
            case "invalid": output = orders.order(-1); break;
            case "age30": output = refunds.refund("a", 30, false); break;
            case "age31": output = refunds.refund("a", 31, false); break;
            case "decline": output = refunds.refund("a", 29, true); break;
            case "replay": refunds.refund("a", 29, false); output = refunds.refund("a", 31, true); break;
            case "sequence": orders.order(8000); output = refunds.refund("a", 30, false); break;
            default: throw new IllegalArgumentException(args[0]);
        }
        System.out.println(output + "|" + state.state());
    }
}
