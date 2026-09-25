#!/usr/bin/env python3
"""Build and execute an isolated multi-class Java checkout review scenario."""

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
from pathlib import Path


SPEC = """# Marketplace checkout refactor contract

The change extracts offer calculation into OfferEngine while preserving checkout behavior.
Each case starts with KIT stock 2, ADDON stock 5, empty success keys, zero points and events.
Prices are KIT 1200 cents and ADDON 350 cents. Quantity must be 1..5; unknown SKU is invalid.
For quantity >= 3, tier discount is floor(gross / 10). The coupon gives 150 cents only when
the amount AFTER the tier discount is >= 1000 cents. Payable = afterTier - coupon discount.
All monetary operations use integer cents. Successful points = floor(payable / 100).
Validate SKU/quantity, then check successful key replay before mutable stock availability.
Same key/same request replay returns the original result with no payment, stock, points or event change.
Only after stock availability and successful payment may stock, points, success cache and event change.
Payment decline increments chargeAttempts only and returns DECLINED; same key may retry.
Each success creates one Checkout event: key, sku, quantity, amountCents=payable, points=earned.
No stock means OUT_OF_STOCK without charging. Invalid input raises IllegalArgumentException.
Cases are sequential on independent instances. Keys are nonempty ASCII; identical key always has
the same SKU, quantity and coupon. No concurrency, real payment, persistence or message broker.
Review all source/diff targets plus compile and every step of the eight listed cases:
coupon_boundary, qualified_coupon, decline_retry, replay_exhausted, mixed, invalid,
out_of_stock, points. Required per-step fields: result, stockKit, stockAddon,
chargeAttempts, charges, chargedCents, points, completedKeys, events. Each event needs
key, sku, quantity, amountCents and earnedPoints. Exit code zero does not prove business PASS.
This is a local simulated pull request without a remote platform action.
"""

INVENTORY = """import java.util.LinkedHashMap;
import java.util.Map;
final class Inventory {
    final Map<String,Integer> stock = new LinkedHashMap<>();
    Inventory() { stock.put("KIT", 2); stock.put("ADDON", 5); }
    boolean known(String sku) { return stock.containsKey(sku); }
    boolean available(String sku, int qty) { return stock.get(sku) >= qty; }
    boolean reserve(String sku, int qty) {
        if (!available(sku, qty)) return false;
        stock.put(sku, stock.get(sku) - qty);
        return true;
    }
}
"""

PAYMENT = """final class Payment {
    int chargeAttempts, charges, chargedCents;
    boolean charge(int amountCents, boolean decline) {
        chargeAttempts++;
        if (decline) return false;
        charges++;
        chargedCents += amountCents;
        return true;
    }
}
"""

LEDGER = """final class Ledger {
    int points;
    void earn(int amountCents) { points += amountCents / 100; }
}
"""

EVENT = """final class Event {
    final String key, sku;
    final int quantity, amountCents, earnedPoints;
    Event(String key, String sku, int quantity, int amountCents, int earnedPoints) {
        this.key = key; this.sku = sku; this.quantity = quantity;
        this.amountCents = amountCents; this.earnedPoints = earnedPoints;
    }
    public String toString() {
        return "{\\"key\\":\\"" + key + "\\",\\"sku\\":\\"" + sku
            + "\\",\\"quantity\\":" + quantity + ",\\"amountCents\\":" + amountCents
            + ",\\"earnedPoints\\":" + earnedPoints + "}";
    }
}
"""

BASE_CHECKOUT = """import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Checkout {
    final Inventory inventory = new Inventory();
    final Payment payment = new Payment();
    final Ledger ledger = new Ledger();
    final Map<String,String> completed = new LinkedHashMap<>();
    final List<Event> events = new ArrayList<>();
    String checkout(String key, String sku, int quantity, boolean coupon, boolean decline) {
        if (!inventory.known(sku) || quantity < 1 || quantity > 5)
            throw new IllegalArgumentException("invalid request");
        if (completed.containsKey(key)) return completed.get(key);
        if (!inventory.available(sku, quantity)) return "OUT_OF_STOCK";
        int gross = (sku.equals("KIT") ? 1200 : 350) * quantity;
        int afterTier = gross - (quantity >= 3 ? gross / 10 : 0);
        int payable = afterTier - (coupon && afterTier >= 1000 ? 150 : 0);
        if (!payment.charge(payable, decline)) return "DECLINED";
        inventory.reserve(sku, quantity);
        ledger.earn(payable);
        String result = "OK:" + payable;
        completed.put(key, result);
        events.add(new Event(key, sku, quantity, payable, payable / 100));
        return result;
    }
}
"""

OFFER = """final class OfferEngine {
    int payable(String sku, int quantity, boolean coupon) {
        int gross = (sku.equals("KIT") ? 1200 : 350) * quantity;
        int afterTier = gross - (quantity >= 3 ? gross / 10 : 0);
        return afterTier - (coupon && gross >= 1000 ? 150 : 0);
    }
}
"""

HEAD_CHECKOUT = """import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class Checkout {
    final Inventory inventory = new Inventory();
    final Payment payment = new Payment();
    final Ledger ledger = new Ledger();
    final OfferEngine offers = new OfferEngine();
    final Map<String,String> completed = new LinkedHashMap<>();
    final List<Event> events = new ArrayList<>();
    String checkout(String key, String sku, int quantity, boolean coupon, boolean decline) {
        if (!inventory.known(sku) || quantity < 1 || quantity > 5)
            throw new IllegalArgumentException("invalid request");
        if (!inventory.reserve(sku, quantity)) return "OUT_OF_STOCK";
        if (completed.containsKey(key)) return completed.get(key);
        int payable = offers.payable(sku, quantity, coupon);
        if (!payment.charge(payable, decline)) return "DECLINED";
        ledger.earn(payable);
        String result = "OK:" + payable;
        completed.put(key, result);
        int gross = (sku.equals("KIT") ? 1200 : 350) * quantity;
        events.add(new Event(key, sku, quantity, gross, payable / 100));
        return result;
    }
}
"""

PROBE = """import java.util.stream.Collectors;
public final class Probe {
    static void step(Checkout c, String key, String sku, int quantity, boolean coupon, boolean decline) {
        String result;
        try { result = c.checkout(key, sku, quantity, coupon, decline); }
        catch (IllegalArgumentException e) { result = "IllegalArgumentException"; }
        String keys = c.completed.keySet().stream().map(k -> "\\\"" + k + "\\\"")
            .collect(Collectors.joining(",", "[", "]"));
        String events = c.events.stream().map(Event::toString).collect(Collectors.joining(",", "[", "]"));
        System.out.println("{\\"result\\":\\"" + result + "\\",\\"stockKit\\":" + c.inventory.stock.get("KIT")
            + ",\\"stockAddon\\":" + c.inventory.stock.get("ADDON")
            + ",\\"chargeAttempts\\":" + c.payment.chargeAttempts
            + ",\\"charges\\":" + c.payment.charges
            + ",\\"chargedCents\\":" + c.payment.chargedCents
            + ",\\"points\\":" + c.ledger.points
            + ",\\"completedKeys\\":" + keys + ",\\"events\\":" + events + "}");
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
"""

CASES = ("coupon_boundary", "qualified_coupon", "decline_retry", "replay_exhausted",
         "mixed", "invalid", "out_of_stock", "points")


def command(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
    return {"argv": argv, "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def must_ok(result):
    if result["exit_code"]:
        raise RuntimeError(result)
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.out).resolve()
    if root.exists():
        parser.error("Output must not already exist")
    root.mkdir(parents=True)
    repo, evidence = root / "repo", root / "evidence"
    repo.mkdir(); evidence.mkdir()
    env = {"created_at": dt.datetime.now().astimezone().isoformat(),
           "python": platform.python_version(), "java": must_ok(command(["java", "--version"], root)),
           "javac": must_ok(command(["javac", "--version"], root))}
    write(evidence / "environment.json", json.dumps(env, indent=2))
    must_ok(command(["git", "init", "-b", "main"], repo))
    must_ok(command(["git", "config", "user.name", "Scenario Fixture"], repo))
    must_ok(command(["git", "config", "user.email", "scenario@example.invalid"], repo))
    common = {"Inventory.java": INVENTORY, "Payment.java": PAYMENT,
              "Ledger.java": LEDGER, "Event.java": EVENT, "Probe.java": PROBE,
              "SPEC.md": SPEC}
    for name, content in {**common, "Checkout.java": BASE_CHECKOUT}.items():
        write(repo / name, content)
    must_ok(command(["git", "add", "."], repo))
    must_ok(command(["git", "commit", "-m", "test: establish marketplace checkout baseline"], repo))
    base = must_ok(command(["git", "rev-parse", "HEAD"], repo))["stdout"].strip()
    must_ok(command(["git", "switch", "-c", "codex/offer-refactor"], repo))
    write(repo / "Checkout.java", HEAD_CHECKOUT)
    write(repo / "OfferEngine.java", OFFER)
    must_ok(command(["git", "add", "Checkout.java", "OfferEngine.java"], repo))
    must_ok(command(["git", "commit", "-m", "refactor: extract checkout offer calculation"], repo))
    head = must_ok(command(["git", "rev-parse", "HEAD"], repo))["stdout"].strip()
    diff = must_ok(command(["git", "diff", f"{base}...{head}"], repo))["stdout"]
    write(evidence / "diff.patch", diff)
    for side, commit in (("base", base), ("head", head)):
        target = evidence / side
        target.mkdir()
        names = tuple(common) + ("Checkout.java",) + (("OfferEngine.java",) if side == "head" else ())
        for name in names:
            content = must_ok(command(["git", "show", f"{commit}:{name}"], repo))["stdout"]
            write(target / name, content)
    execution = {"base": base, "head": head, "branch": "codex/offer-refactor", "cases": {}}
    for side in ("base", "head"):
        src = evidence / side
        build = root / f"build-{side}"; build.mkdir()
        sources = [str(p) for p in sorted(src.glob("*.java"))]
        execution["cases"][side] = {"compile": must_ok(command(["javac", "-d", str(build), *sources], root)), "runs": {}}
        for case in CASES:
            result = must_ok(command(["java", "-cp", str(build), "Probe", case], root))
            result["steps"] = [json.loads(line) for line in result["stdout"].splitlines()]
            execution["cases"][side]["runs"][case] = result
    old = execution["cases"]["base"]["runs"]
    new = execution["cases"]["head"]["runs"]
    assert old["coupon_boundary"]["steps"][0]["result"] == "OK:945"
    assert new["coupon_boundary"]["steps"][0]["result"] == "OK:795"
    assert old["decline_retry"]["steps"][0]["stockKit"] == 2
    assert new["decline_retry"]["steps"][0]["stockKit"] == 1
    assert old["replay_exhausted"]["steps"][1]["result"] == "OK:2400"
    assert new["replay_exhausted"]["steps"][1]["result"] == "OUT_OF_STOCK"
    assert old["qualified_coupon"]["steps"][0]["events"][0]["amountCents"] == 1050
    assert new["qualified_coupon"]["steps"][0]["events"][0]["amountCents"] == 1200
    write(evidence / "execution.json", json.dumps(execution, indent=2))
    files = {str(p.relative_to(evidence)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in evidence.rglob("*") if p.is_file()}
    write(evidence / "manifest.json", json.dumps({"base": base, "head": head,
                                                    "branch": execution["branch"], "sha256": files}, indent=2))
    print(json.dumps({"root": str(root), "base": base, "head": head,
                      "cases": len(CASES), "steps_per_side": sum(len(old[c]["steps"]) for c in CASES),
                      "assertions": "passed"}))


if __name__ == "__main__":
    main()
