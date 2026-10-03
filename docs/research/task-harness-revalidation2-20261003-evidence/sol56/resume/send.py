from pathlib import Path
p=Path("deliveries.txt")
p.write_text(p.read_text()+"delivery attempted\n")
print("submitted")
