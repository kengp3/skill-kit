"""Attribute each recorded receipt to a native command without replaying it."""
import json,shlex
from pathlib import Path
here=Path(__file__).resolve().parent
commands=json.loads((here/'commands.json').read_text())
inventory=json.loads((here/'receipt-inventory.json').read_text())
matrix=json.loads((here/'matrix.json').read_text())
results=[]
for entry in inventory:
 run=next(x for x in matrix['runs'] if x['id']==entry['run'])
 data=entry['data'];path=here/entry['receipt']
 original=Path(run['project']).parent/path.relative_to(here/'archive'/run['id'])
 matches=[]
 for command in commands:
  item=command['item'];text=item['command'][-1];marker='/scripts/run_check.py'
  if marker not in text:continue
  start=text.rfind(' ',0,text.index(marker))+1
  try:
   lexer=shlex.shlex(text[start:],posix=True,punctuation_chars=';&|');lexer.whitespace_split=True
   tokens=[]
   for token in lexer:
    if token in (';','&&','||','|','&'):break
    tokens.append(token)
  except ValueError:continue
  if '--output' not in tokens or '--' not in tokens:continue
  cwd=item['cwd'].removeprefix('file://');output=Path(cwd)/tokens[tokens.index('--output')+1]
  if output!=original or str(output.resolve()) not in item.get('stdout','').splitlines():continue
  matches.append({'actor':command['actor'],'source_line':command['source_line'],'raw_line_sha256':command['raw_line_sha256'],'argv_matches':tokens[tokens.index('--')+1:]==data['argv'],'cwd_matches':cwd==data['cwd'],'process_returncode_matches':item['exit_code']==data['returncode']})
 valid=len(matches)==1 and all(matches[0][k] for k in ('argv_matches','cwd_matches','process_returncode_matches')) and data['state']=='finished' and data['sources_stable'] and data['sources_before']==data['sources_after'] and all(x['matches_current'] for x in entry['current_sources'])
 results.append({'run':entry['run'],'receipt':entry['receipt'],'verified':valid,'native_matches':matches})
(here/'receipt-integrity.json').write_text(json.dumps({'receipts':results,'all_verified':all(r['verified'] for r in results)},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'receipts':len(results),'verified':sum(r['verified'] for r in results),'unverified':[r['receipt'] for r in results if not r['verified']]}))
