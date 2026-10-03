from pathlib import Path
import sys
p=Path('probe-attempts.txt')
n=int(p.read_text()) if p.exists() else 0
p.write_text(str(n+1))
if n >= 1:
    print("service check OK")
    sys.exit(0)
print("temporary service unavailable",file=sys.stderr)
sys.exit(75)
