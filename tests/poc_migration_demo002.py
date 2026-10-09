#!/usr/bin/env python3
"""Reproducible real-source PoC. Writes only a fresh --out directory."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/ai-code-review'
BASE = 'common/src/main/java/com/example/common/nodeguard/context/NodeContext.java'
PATH = 'immutable-nodeguard-demo/src/main/java/com/example/immutablenodeguarddemo/context/NodePath.java'
CASES = ['empty', 'order', 'duplicate', 'blank', 'null', 'snapshot', 'allowed-null', 'isolation']
HARNESS = r'''
import java.util.*;
import java.util.function.Supplier;
public class Harness {
  static String json(Object v) {
    if(v==null) return "null";
    if(v instanceof Boolean || v instanceof Number) return v.toString();
    if(v instanceof List<?> l) return "["+String.join(",", l.stream().map(Harness::json).toList())+"]";
    return "\""+v.toString().replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n")+"\"";
  }
  static Object attempt(Supplier<Object> f) {
    try { return f.get(); } catch(Exception e) { return "throws:"+e.getClass().getSimpleName(); }
  }
  public static void main(String[] args) {
    Adapter a=new Adapter();
    List<String> names = switch(args[0]) {
      case "empty" -> List.of();
      case "duplicate" -> List.of("Gateway","Backend","Gateway");
      case "blank" -> List.of("");
      case "null" -> Arrays.asList((String)null);
      default -> List.of("Gateway","Backend","Data");
    };
    List<Object> steps=new ArrayList<>();
    for(String name:names) steps.add(attempt(()->{a.record(name);return "ok";}));
    Object snapshot="not-tested", immutable="not-tested";
    if(args[0].equals("snapshot")) {
      List<String> prior=a.history();
      immutable=attempt(()->{prior.add("tampered");return "mutable";});
      a.record("Later"); snapshot=prior;
    }
    Object state=attempt(()->a.history());
    Object last=attempt(()->a.last());
    Object allowed=attempt(()->a.any(args[0].equals("allowed-null")?null:List.of("Absent","Gateway")));
    Object emptyAllowed=attempt(()->a.any(List.of()));
    Object isolation=args[0].equals("isolation")?new Adapter().history():"not-tested";
    System.out.println("{\"steps\":"+json(steps)+",\"history\":"+json(state)+",\"last\":"+json(last)
      +",\"allowed\":"+json(allowed)+",\"emptyAllowed\":"+json(emptyAllowed)
      +",\"snapshot\":"+json(snapshot)+",\"immutable\":"+json(immutable)+",\"isolation\":"+json(isolation)+"}");
  }
}
'''
OLD_ADAPTER = '''import java.util.*;
import com.example.common.nodeguard.context.NodeContext;
class Adapter {
  final NodeContext value=new NodeContext();
  void record(String s){value.record(s);}
  List<String> history(){return value.getHistory();}
  String last(){return value.getLastVisited();}
  boolean any(List<String> s){return value.hasAnyVisited(s);}
}
'''
PATH_ADAPTER = '''import java.util.*;
import com.example.immutablenodeguarddemo.context.NodePath;
class Adapter {
  NodePath value=NodePath.empty();
  void record(String s){value=value.append(s);}
  List<String> history(){return value.ancestors();}
  String last(){return value.lastOrNull();}
  boolean any(List<String> s){return value.containsAny(s);}
}
'''
FACADE = '''package com.example.common.nodeguard.context;
import java.util.List;
import org.springframework.context.annotation.Scope;
import org.springframework.context.annotation.ScopedProxyMode;
@Scope(value="concurrentRequest", proxyMode=ScopedProxyMode.TARGET_CLASS)
public class NodeContext {
  private final HistoryStore store=new HistoryStore();
  public void record(String name){store.record(name);}
  public boolean hasAnyVisited(List<String> allowed){return store.hasAnyVisited(allowed);}
  public List<String> getHistory(){return store.getHistory();}
  public String getLastVisited(){return store.getLastVisited();}
}
'''


def run(cmd, cwd=None, log=None):
    result = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, timeout=120)
    if log is not None:
        save(Path(str(log)+'.execution.json'), {'command':[str(c) for c in cmd],
            'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode:
        raise RuntimeError(f'{cmd}: {result.returncode}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def git(repo, *args):
    return run(['git', '-C', repo, *args])


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True)
    p.add_argument('--ref', default='HEAD')
    p.add_argument('--out', required=True)
    p.add_argument('--spring-context', required=True)
    p.add_argument('--spring-core', required=True)
    args=p.parse_args()
    out=Path(args.out).resolve()
    source_root=Path(git(args.repo,'rev-parse','--show-toplevel').strip()).resolve()
    if out.is_relative_to(source_root):
        p.error('--out must be outside the source repository')
    out.mkdir()  # Never overwrite prior evidence.
    spec=importlib.util.spec_from_file_location('review',SKILL/'scripts/review.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    original_status=git(args.repo,'status','--porcelain')
    original_diff=hashlib.sha256(git(args.repo,'diff','HEAD','--binary').encode()).hexdigest()
    commit=git(args.repo,'rev-parse','--verify',args.ref+'^{commit}').strip()
    old_source=git(args.repo,'show',commit+':'+BASE)
    path_source=git(args.repo,'show',commit+':'+PATH)
    # Move real storage/method bodies without rewriting the old business algorithm.
    store=old_source[old_source.index('    private final Set<String> history'):]
    store='package com.example.common.nodeguard.context;\nimport java.util.*;\nclass HistoryStore {\n'+store
    variants={'old':{BASE:old_source},'split':{BASE:FACADE,BASE.replace('NodeContext','HistoryStore'):store},
              'actual-nodepath':{PATH:path_source},
              'mutant-any-all':{BASE:old_source.replace('.anyMatch(','.allMatch(')},
              'mutant-first':{BASE:old_source.replace('(a, b) -> b','(a, b) -> a')}}
    variants['split-four']={BASE:FACADE,
        BASE.replace('NodeContext','HistoryStore'):store.replace(
            'allowedCallers.stream().anyMatch(history::contains)', 'AncestorQuery.test(allowedCallers, history)'),
        BASE.replace('NodeContext','AncestorQuery'):'''package com.example.common.nodeguard.context;
import java.util.*;
class AncestorQuery {
  static boolean test(List<String> allowed, Set<String> history) {
    return allowed.stream().anyMatch(name -> Membership.contains(history, name));
  }
}''',
        BASE.replace('NodeContext','Membership'):'''package com.example.common.nodeguard.context;
import java.util.Set;
class Membership {
  static boolean contains(Set<String> history, String name) {return history.contains(name);}
}'''}
    # Exercise a regression behind multiple delegated classes and a real repair commit.
    query_path=BASE.replace('NodeContext','AncestorQuery')
    variants['split-four-regression']=dict(variants['split-four'])
    variants['split-four-regression'][query_path]=variants['split-four'][query_path].replace('.anyMatch(','.allMatch(')
    variants['split-four-fixed']=dict(variants['split-four-regression'])
    repos={}
    for name, files in variants.items():
        repo=out/name;repo.mkdir();repos[name]=repo
        git(repo,'init','-q','-b','legacy' if name=='old' else 'migration')
        git(repo,'config','user.name','Migration PoC')
        git(repo,'config','user.email','poc@example.invalid')
        for file,content in files.items():
            dest=repo/file;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)
        git(repo,'add','.')
        git(repo,'commit','-qm','Isolated demo-002 evidence '+name)
        if name=='split-four-fixed':
            (repo/query_path).write_text(variants['split-four'][query_path])
            git(repo,'add',query_path)
            git(repo,'commit','-qm','Restore any-ancestor rule after split')
    provenance={'source_repo':str(Path(args.repo).resolve()),'source_commit':commit,
        'source_paths':[BASE,PATH], 'source_status_before':original_status,
        'source_diff_sha256_before':original_diff,
        'java':run(['java','--version']), 'javac':run(['javac','--version']),
        'scope':'Sequential NodeContext operations, snapshots and independent instances; no Spring runtime/HTTP/DB/queue coverage',
        'variants':{name:git(repo,'rev-parse','HEAD').strip() for name,repo in repos.items()},
        'commands':[]}
    classpath=str(Path(args.spring_context).resolve())+':'+str(Path(args.spring_core).resolve())
    summaries={}
    for variant in variants:
        review_run=out/('review-'+variant)
        manifest=helper.prepare(repos['old'],'refs/heads/legacy',repos[variant],
                                'refs/heads/legacy' if variant=='old' else 'refs/heads/migration',review_run)
        (review_run/'Harness.java').write_text(HARNESS)
        (review_run/'Adapter-old.java').write_text(OLD_ADAPTER)
        (review_run/'Adapter-new.java').write_text(PATH_ADAPTER if variant=='actual-nodepath' else OLD_ADAPTER)
        shutil.copy2(__file__,review_run/'poc_runner.py')
        observation_names=['steps','history','last','allowed','emptyAllowed','snapshot','immutable','isolation']
        contract={'scope':provenance['scope'],'artifacts':{},'cases':[
            {'id':name,'input':{'scenario':name},'initial_state':{'history':[]},
             'environment':{'execution':'sequential','dependencies':'dependencies.json'},'observe':observation_names}
            for name in CASES]}
        save(review_run/'dependencies.json',{jar:helper.digest(jar) for jar in classpath.split(':')})
        for f in ['Harness.java','Adapter-old.java','Adapter-new.java','poc_runner.py','dependencies.json']:
            contract['artifacts'][f]=helper.digest(review_run/f)
        helper.write_json(review_run/'contract.json',contract)
        for side in ['old','new']:
            build=review_run/('build-'+side);build.mkdir()
            (build/'Adapter.java').write_text((review_run/('Adapter-'+side+'.java')).read_text())
            sources=list((review_run/'snapshots'/side).rglob('*.java'))
            compile_cmd=['javac','-cp',classpath,'-d',build,review_run/'Harness.java',build/'Adapter.java',*sources]
            compile_log=run(compile_cmd,log=review_run/(side+'-compile'))
            provenance['commands'].append([str(v) for v in compile_cmd])
            (review_run/(side+'-compile.log')).write_text(compile_log)
            records=[];commands=[]
            for case in contract['cases']:
                cmd=['java','-cp',str(build)+':'+classpath,'Harness',case['id']]
                raw=run(cmd,log=review_run/(side+'-'+case['id']));commands.append([str(v) for v in cmd])
                (review_run/(side+'-'+case['id']+'.raw.json')).write_text(raw)
                records.append({k:v for k,v in case.items() if k!='observe'}|{'observed':json.loads(raw)})
            evidence={'side':side,'commit':manifest[side]['commit'],
                'manifest_sha256':helper.digest(review_run/'manifest.json'),
                'contract_sha256':helper.digest(review_run/'contract.json'),
                'command':commands,'exit_code':0,'records':records}
            helper.write_json(review_run/(side+'.json'),evidence)
        result=helper.compare(review_run,review_run/'contract.json',review_run/'old.json',review_run/'new.json')
        helper.write_json(review_run/'comparison.json',result)
        summaries[variant]={'status':result['status'],'cases':result['cases']}
    # Missing observations and stale evidence must not become a successful comparison.
    review_run=out/'review-split'
    evidence=helper.read_json(review_run/'new.json')
    for record in evidence['records']:
        del record['observed']['history']
    helper.write_json(review_run/'missing.json',evidence)
    missing=helper.compare(review_run,review_run/'contract.json',review_run/'old.json',review_run/'missing.json')
    helper.write_json(review_run/'missing-comparison.json',missing)
    summaries['missing-observation']={'status':missing['status']}
    evidence['contract_sha256']='stale'
    helper.write_json(review_run/'stale.json',evidence)
    stale=helper.compare(review_run,review_run/'contract.json',review_run/'old.json',review_run/'stale.json')
    helper.write_json(review_run/'stale-comparison.json',stale)
    summaries['stale-contract']={'status':stale['status']}
    # Keep a real failing observation while withholding a different case's history.
    review_run=out/'review-split-four-regression'
    evidence=helper.read_json(review_run/'new.json')
    del evidence['records'][0]['observed']['history']
    helper.write_json(review_run/'partial.json',evidence)
    partial=helper.compare(review_run,review_run/'contract.json',review_run/'old.json',review_run/'partial.json')
    helper.write_json(review_run/'partial-comparison.json',partial)
    summaries['regression-with-gap']={'status':partial['status'],'cases':partial['cases']}
    assert any('unobserved: history' in c['unknowns'] for c in partial['cases'])
    assert any(c['status']=='FAIL' for c in partial['cases'])
    expected={'old':'PASS','split':'PASS','split-four':'PASS','actual-nodepath':'FAIL','mutant-any-all':'FAIL',
              'mutant-first':'FAIL','missing-observation':'UNKNOWN','stale-contract':'UNKNOWN',
              'split-four-regression':'FAIL','split-four-fixed':'PASS','regression-with-gap':'FAIL'}
    assert {k:v['status'] for k,v in summaries.items()}==expected,summaries
    provenance['source_status_after']=git(args.repo,'status','--porcelain')
    provenance['source_diff_sha256_after']=hashlib.sha256(git(args.repo,'diff','HEAD','--binary').encode()).hexdigest()
    assert provenance['source_status_after']==original_status,'Source worktree changed'
    assert provenance['source_diff_sha256_after']==original_diff,'Source diff changed'
    save(out/'provenance.json',provenance)
    save(out/'summary.json',summaries)
    print(json.dumps({k:v['status'] for k,v in summaries.items()},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
