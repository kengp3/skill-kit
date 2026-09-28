public final class Policy {
    public static int shipping(int net) { return net > 8000 ? 0 : 500; }
}
