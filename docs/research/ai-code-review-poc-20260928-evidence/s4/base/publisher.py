def submit(bus, order_id):
    payload = {"type": "OrderAccepted", "order_id": order_id}
    if not bus.publish(payload):
        raise RuntimeError("publish rejected")
    return "accepted"
