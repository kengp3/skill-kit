def make_payload(order_id):
    return {"type": "OrderAccepted", "order_id": order_id}

def submit(bus, order_id):
    if not bus.publish(make_payload(order_id)):
        raise RuntimeError("publish rejected")
    return "accepted"
