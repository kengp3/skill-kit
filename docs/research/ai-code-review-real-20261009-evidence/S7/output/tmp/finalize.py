import pathlib,json,hashlib,subprocess,os
r=pathlib.Path('/private/tmp/ai-review-real-20261009/S7');o=r/'output';s=r.parent/'skill'
p=o/'review.md';p.write_text(p.read_text().replace('图中','圖中').replace('顺序','順序').replace('宣称','宣稱').replace('初始讀取命令另存','規範與工具重讀之命令／原始輸出（初讀後補存，不冒充初讀時間）另存'))
files=[s/'SKILL.md',*[s/'references'/x for x in ['deep-review.md','report.md','migration.md','evidence.md']],s/'scripts/review.py',s/'scripts/check_report_hashes.py',r/'project-setting.md',r/'contract.json',r/'targets.json',r/'probe.py']
logs=[]
for f in files:
 args=['cat',str(f)];res=subprocess.run(args,capture_output=True,text=True);logs.append({'command':args,'stdout':res.stdout,'stderr':res.stderr,'exit_code':res.returncode})
(o/'initial-reads.json').write_text(json.dumps({'note':'Final evidence capture reread; initial clock retained separately.','commands':logs},indent=2))
files += [*r.glob('base/*.py'),*r.glob('head/*.py'),*r.glob('repo-base/*.py'),*r.glob('repo-head/*.py')]
files += [p for p in o.rglob('*') if p.is_file() and p.name not in ['hashes.md','hash-check.json','final-review.json']]
files=sorted(set(files))
(o/'hashes.md').write_text('# 本輪 SHA-256 核對索引\n\n'+''.join(f'- [{f.relative_to(r) if f.is_relative_to(r) else f.name}]({f}) SHA-256 `{hashlib.sha256(f.read_bytes()).hexdigest()}`\n' for f in files))
args=['python3',str(s/'scripts/check_report_hashes.py'),str(o/'hashes.md')];res=subprocess.run(args,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));result={'command':args,'stdout':res.stdout,'stderr':res.stderr,'exit_code':res.returncode};(o/'hash-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert res.returncode==0
