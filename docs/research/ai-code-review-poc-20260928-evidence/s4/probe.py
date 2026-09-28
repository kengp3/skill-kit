import json
from publisher import submit
class FakeBus:
    def __init__(self, acknowledge):
        self.acknowledge = acknowledge
        self.calls = []
    def publish(self, payload):
        self.calls.append(payload)
        return self.acknowledge
for acknowledge in (True, False):
    bus = FakeBus(acknowledge)
    try:
        result = {"result": submit(bus, "o-1")}
    except RuntimeError as error:
        result = {"error": str(error)}
    print(json.dumps({"acknowledge": acknowledge, "calls": bus.calls, **result}))
