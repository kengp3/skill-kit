from pathlib import Path
import sys
p=Path('unavailable-attempts.txt')
n=int(p.read_text()) if p.exists() else 0
p.write_text(str(n+1))
print("temporary service unavailable",file=sys.stderr)
sys.exit(75)
