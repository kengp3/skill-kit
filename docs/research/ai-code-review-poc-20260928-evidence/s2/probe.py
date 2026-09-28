import json
from api import quote
for cents, coupon in [(999, True), (1000, True), (1001, True), (1000, False), (0, True), (-1, True), (1.5, True)]:
    try:
        print(json.dumps({"cents": cents, "coupon": coupon, "result": quote(cents, coupon)}))
    except ValueError as error:
        print(json.dumps({"cents": cents, "coupon": coupon, "error": str(error)}))
