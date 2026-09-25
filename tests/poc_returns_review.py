#!/usr/bin/env python3
"""Create a fixed Java return-refactor review fixture and run its cases."""

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
from pathlib import Path


SPEC = """# Partial-return refactor contract

The change extracts the refund formula into ReturnPolicy and must preserve public
Returns.returnItems behavior. One fresh Order starts each case: 3 purchased units,
400 cents per unit, 100 cents shipping, zero returned units. All values are cents.
Return age 0..30 days inclusive is eligible; negative or older age and quantity <1
return REJECTED. Quantity above remaining units returns NO_QUANTITY.
The same key and same request may replay a successful receipt, before mutable
eligibility/remaining checks; it returns the original result without new effects.
For a new return, refund quantity * 400 cents and add the original 100 cents
shipping only when cumulative returned quantity reaches 3. A refund decline
increments attempts but must not change returned units, warehouse stock,
loyalty reversal, successful receipts or events. A successful refund increments
returned units, restocks returned quantity, reverses quantity * 4 points and
records exactly one receipt and ReturnEvent with the actual refunded amount.
Each case has its own in-memory service instance. Keys are nonempty ASCII;
identical keys have identical return quantities; ageDays represents the current
age and may advance between replay calls. No concurrency,
real payment gateway, persistence, or message broker is covered.
Review the complete committed diff and related classes, compile both versions,
and run every step of all eight Probe cases. Compare result, returnedQty,
restockedQty, refundAttempts, successfulRefunds, refundedCents,
reversedPoints, receiptKeys and events. Exit 0 alone does not mean compliance.
This is an isolated simulated PR with no remote platform action.
"""

ORDER = """final class Order {
    final int purchasedQty = 3;
    final int unitCents = 400;
    final int shippingCents = 100;
    int returnedQty;
}
"""

WAREHOUSE = """final class Warehouse {
    int restockedQty;
    void restock(int quantity) { restockedQty += quantity; }
}
"""

GATEWAY = """final class RefundGateway {
    int attempts, successfulRefunds, refundedCents;
    boolean refund(int amountCents, boolean decline) {
        attempts++;
        if (decline) return false;
        successfulRefunds++;
        refundedCents += amountCents;
        return true;
    }
}
"""

LOYALTY = """final class Loyalty {
    int reversedPoints;
    void reverse(int points) { reversedPoints += points; }
}
"""

EVENT = """final class ReturnEvent {
    final String key;
    final int quantity, amountCents;
    ReturnEvent(String key, int quantity, int amountCents) {
        this.key = key;
        this.quantity = quantity;
        this.amountCents = amountCents;
    }
    public String toString() {
        return "{\\"key\\":\\"" + key + "\\",\\"quantity\\":" + quantity
            + ",\\"amountCents\\":" + amountCents + "}";
    }
}
"""

BASE_RETURNS = """import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Returns {
    final Order order = new Order();
    final Warehouse warehouse = new Warehouse();
    final RefundGateway gateway = new RefundGateway();
    final Loyalty loyalty = new Loyalty();
    final Map<String,String> receipts = new LinkedHashMap<>();
    final List<ReturnEvent> events = new ArrayList<>();
    String returnItems(String key, int quantity, int ageDays, boolean decline) {
        if (receipts.containsKey(key)) return receipts.get(key);
        if (quantity < 1 || ageDays < 0 || ageDays > 30) return "REJECTED";
        if (order.returnedQty + quantity > order.purchasedQty) return "NO_QUANTITY";
        int amountCents = quantity * order.unitCents
            + (order.returnedQty + quantity == order.purchasedQty ? order.shippingCents : 0);
        if (!gateway.refund(amountCents, decline)) return "DECLINED";
        order.returnedQty += quantity;
        warehouse.restock(quantity);
        loyalty.reverse(quantity * order.unitCents / 100);
        String result = "REFUNDED:" + amountCents;
        receipts.put(key, result);
        events.add(new ReturnEvent(key, quantity, amountCents));
        return result;
    }
}
"""

POLICY = """final class ReturnPolicy {
    int amountCents(Order order, int quantity) {
        return quantity * order.unitCents
            + (quantity == order.purchasedQty ? order.shippingCents : 0);
    }
}
"""

HEAD_RETURNS = """import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Returns {
    final Order order = new Order();
    final Warehouse warehouse = new Warehouse();
    final RefundGateway gateway = new RefundGateway();
    final Loyalty loyalty = new Loyalty();
    final ReturnPolicy policy = new ReturnPolicy();
    final Map<String,String> receipts = new LinkedHashMap<>();
    final List<ReturnEvent> events = new ArrayList<>();
    String returnItems(String key, int quantity, int ageDays, boolean decline) {
        if (quantity < 1 || ageDays < 0 || ageDays >= 30) return "REJECTED";
        if (order.returnedQty + quantity > order.purchasedQty) return "NO_QUANTITY";
        if (receipts.containsKey(key)) return receipts.get(key);
        int amountCents = policy.amountCents(order, quantity);
        order.returnedQty += quantity;
        warehouse.restock(quantity);
        if (!gateway.refund(amountCents, decline)) return "DECLINED";
        loyalty.reverse(quantity * order.unitCents / 100);
        String result = "REFUNDED:" + amountCents;
        receipts.put(key, result);
        events.add(new ReturnEvent(key, quantity, amountCents));
        return result;
    }
}
"""

PROBE = """import java.util.stream.Collectors;
public final class Probe {
    static void step(Returns service, String scenario, int step, String key,
                     int quantity, int ageDays, boolean decline) {
        String result = service.returnItems(key, quantity, ageDays, decline);
        String keys = service.receipts.keySet().stream().map(k -> "\\"" + k + "\\"")
            .collect(Collectors.joining(",", "[", "]"));
        String events = service.events.stream().map(ReturnEvent::toString)
            .collect(Collectors.joining(",", "[", "]"));
        System.out.println("{\\"case\\":\\"" + scenario + "\\",\\"step\\":" + step
            + ",\\"result\\":\\"" + result + "\\",\\"returnedQty\\":" + service.order.returnedQty
            + ",\\"restockedQty\\":" + service.warehouse.restockedQty
            + ",\\"refundAttempts\\":" + service.gateway.attempts
            + ",\\"successfulRefunds\\":" + service.gateway.successfulRefunds
            + ",\\"refundedCents\\":" + service.gateway.refundedCents
            + ",\\"reversedPoints\\":" + service.loyalty.reversedPoints
            + ",\\"receiptKeys\\":" + keys + ",\\"events\\":" + events + "}");
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
"""

CASES = ("partial_final", "day30", "decline_retry", "replay_full",
         "replay_expired", "too_many", "after_window", "normal")


def run(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)
    record = {"argv": argv, "exit_code": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    if result.returncode:
        raise RuntimeError(record)
    return record


def put(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.out).resolve()
    if root.exists():
        parser.error("output must not already exist")
    root.mkdir(parents=True)
    repo = root / "repo"
    repo.mkdir()
    env = {"created_at": dt.datetime.now().astimezone().isoformat(),
           "python": platform.python_version(), "java": run(["java", "--version"], root),
           "javac": run(["javac", "--version"], root)}
    put(root / "environment.json", json.dumps(env, ensure_ascii=False, indent=2) + "\n")
    run(["git", "init", "-b", "main"], repo)
    run(["git", "config", "user.name", "Scenario Fixture"], repo)
    run(["git", "config", "user.email", "scenario@example.invalid"], repo)
    common = {"SPEC.md": SPEC, "Order.java": ORDER, "Warehouse.java": WAREHOUSE,
              "RefundGateway.java": GATEWAY, "Loyalty.java": LOYALTY,
              "ReturnEvent.java": EVENT, "Probe.java": PROBE}
    for name, content in {**common, "Returns.java": BASE_RETURNS}.items():
        put(repo / name, content)
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "test: establish partial return baseline"], repo)
    base = run(["git", "rev-parse", "HEAD"], repo)["stdout"].strip()
    run(["git", "switch", "-c", "codex/refund-policy-extraction"], repo)
    put(repo / "Returns.java", HEAD_RETURNS)
    put(repo / "ReturnPolicy.java", POLICY)
    run(["git", "add", "Returns.java", "ReturnPolicy.java"], repo)
    run(["git", "commit", "-m", "refactor: extract return refund policy"], repo)
    head = run(["git", "rev-parse", "HEAD"], repo)["stdout"].strip()
    diff = run(["git", "diff", f"{base}...{head}"], repo)["stdout"]
    put(root / "diff.patch", diff)
    evidence = {"base": base, "head": head, "branch": "codex/refund-policy-extraction",
                "cases": list(CASES), "runs": {}, "file_sha256": {}}
    for side, commit in (("base", base), ("head", head)):
        source = root / side
        source.mkdir()
        names = run(["git", "ls-tree", "-r", "--name-only", commit], repo)["stdout"].splitlines()
        for name in names:
            content = run(["git", "show", f"{commit}:{name}"], repo)["stdout"]
            put(source / name, content)
            evidence["file_sha256"][f"{side}/{name}"] = hashlib.sha256(content.encode()).hexdigest()
        build = root / "build" / side
        build.mkdir(parents=True)
        compile_run = run(["javac", "-d", str(build), *map(str, source.glob("*.java"))], root)
        records = []
        for case in CASES:
            execution = run(["java", "-cp", str(build), "Probe", case], root)
            records.append({"case": case, "command": execution,
                            "observed": [json.loads(line) for line in execution["stdout"].splitlines()]})
        evidence["runs"][side] = {"compile": compile_run, "records": records}
    put(root / "execution.json", json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    summary = {case: [entry for entry in evidence["runs"]["base"]["records"] if entry["case"] == case][0]["observed"]
               != [entry for entry in evidence["runs"]["head"]["records"] if entry["case"] == case][0]["observed"]
               for case in CASES}
    put(root / "comparison.json", json.dumps({"different_by_case": summary}, indent=2) + "\n")
    print(json.dumps({"base": base, "head": head, "different_by_case": summary}, indent=2))


if __name__ == "__main__":
    main()
