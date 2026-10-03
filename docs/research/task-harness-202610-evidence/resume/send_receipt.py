from pathlib import Path
p = Path(__file__).with_name("deliveries.txt")
with p.open("a") as f:
    f.write("sent receipt\n")
print("sent")
