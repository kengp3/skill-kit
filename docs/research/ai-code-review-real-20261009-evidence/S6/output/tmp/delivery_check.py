import json,pathlib
r=pathlib.Path('/private/tmp/ai-review-real-20261009/S6/output')
a=json.loads((r/'run/old.json').read_text())['records'];b=json.loads((r/'run/new.json').read_text())['records']
assert len(a)==len(b)==110
for x,y in zip(a,b):
    for i,j in zip(x['observed']['steps'],y['observed']['steps']):
        assert {k:v for k,v in i.items() if k!='events'}=={k:v for k,v in j.items() if k!='events'}
report=(r/'review.md').read_text(); titles=[x for x in report.splitlines() if x.startswith('## ')]
assert titles[:5]==['## 1. 基本說明','## 2. 範圍說明','## 3. 關聯與流程','## 4. 審查結果與問題','## 5. 結論']
assert titles[-1]=='## 附錄：完整檔案清單'
source=(r/'run/snapshots/new/service.py').read_text().strip(); assert source in report
print('PASS: 110 cases; all non-event observations equal; five chapters and final inventory; exact original source excerpt')
print('Manual report readback: decision, sole open F-001, source/guard/caller, action and closure align; diagrams not rendered; proposed fix not executed.')
