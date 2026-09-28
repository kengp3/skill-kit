public final class Probe {
    public static void main(String[] args) {
        LegacySystem service = new LegacySystem();
        String output;
        switch (args[0]) {
            case "order7999": output = service.order(7999); break;
            case "order8000": output = service.order(8000); break;
            case "order8001": output = service.order(8001); break;
            case "invalid": output = service.order(-1); break;
            case "age30": output = service.refund("a", 30, false); break;
            case "age31": output = service.refund("a", 31, false); break;
            case "decline": output = service.refund("a", 29, true); break;
            case "replay": service.refund("a", 29, false); output = service.refund("a", 31, true); break;
            case "sequence": service.order(8000); output = service.refund("a", 30, false); break;
            default: throw new IllegalArgumentException(args[0]);
        }
        System.out.println(output + "|" + service.state());
    }
}
