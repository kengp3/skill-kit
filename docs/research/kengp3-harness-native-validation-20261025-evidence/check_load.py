"""Read native plugin/skill/hook state without starting a model or thread."""
import json, os, selectors, subprocess, sys, time
from pathlib import Path
settings=json.loads(Path('/tmp/kengp3-harness-native-run.json').read_text())
phase=sys.argv[1]
assert phase in ('loaded','disabled','reloaded','removed')
plugin_id='kengp3-harness@kengp3-harness-local'
env=os.environ.copy()
env['CODEX_HOME']=settings['state']
for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):
    env.pop(key,None)
project=settings['project']
records=[]
with (Path(settings['evidence'])/(phase+'-server.stderr')).open('w') as errors:
    process=subprocess.Popen([settings['codex'],'app-server','--stdio'],cwd=project,env=env,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors)
    selector=selectors.DefaultSelector()
    selector.register(process.stdout,selectors.EVENT_READ)
    buffer=b''
    def rpc(method,params):
        global buffer
        rid=len(records)+1
        request={'id':rid,'method':method,'params':params}
        process.stdin.write((json.dumps(request)+'\n').encode())
        process.stdin.flush()
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            while b'\n' in buffer:
                line,buffer=buffer.split(b'\n',1)
                if not line:continue
                response=json.loads(line)
                if response.get('id')==rid:
                    records.append({'request':request,'response':response})
                    assert 'error' not in response,response
                    return response['result']
            for key,_ in selector.select(.2):
                data=os.read(key.fd,65536)
                if not data:raise RuntimeError('Unexpected app-server EOF')
                buffer+=data
        raise TimeoutError(method)
    try:
        rpc('initialize',{'clientInfo':{'name':'kengp3_native_validation','version':'1.0.0'},
                          'capabilities':{'experimentalApi':True}})
        process.stdin.write(b'{"method":"initialized","params":{}}\n')
        process.stdin.flush()
        details=rpc('plugin/read',{'marketplacePath':str(Path(settings['catalog'])/'.agents/plugins/marketplace.json'),
                                   'pluginName':'kengp3-harness'})['plugin']
        skills=rpc('skills/list',{'cwds':[project],'forceReload':True})['data']
        hooks=rpc('hooks/list',{'cwds':[project]})['data']
        loaded_skills=[x for row in skills for x in row['skills'] if x.get('pluginId')==plugin_id]
        loaded_hooks=[x for row in hooks for x in row['hooks'] if x.get('pluginId')==plugin_id]
        assert all(not row['errors'] for row in skills),skills
        assert all(not row['errors'] and not row['warnings'] for row in hooks),hooks
        enabled=phase in ('loaded','reloaded')
        assert details['summary']['installed']==(phase!='removed'),details['summary']
        assert details['summary']['enabled']==enabled,details['summary']
        if enabled:
            assert {x['name'] for x in loaded_skills}=={'kengp3-harness:'+n for n in ('define-task','project-setting','task-harness','ai-code-review')}
            assert len(loaded_hooks)==3
            assert {x['eventName'] for x in loaded_hooks}=={'sessionStart','userPromptSubmit','stop'}
            cache=Path(settings['state'])/'plugins/cache/kengp3-harness-local/kengp3-harness/0.2.1'
            assert all(x['enabled'] and Path(x['path']).is_relative_to(cache) for x in loaded_skills)
            assert all(x['enabled'] and x['source']=='plugin' and Path(x['sourcePath']).is_relative_to(cache) for x in loaded_hooks)
            assert all(x['trustStatus']=='untrusted' for x in loaded_hooks)
            assert all(str(cache/'hooks/task_harness.py') in x['command'] for x in loaded_hooks)
        else:
            assert not any(x['enabled'] for x in loaded_skills),loaded_skills
            assert not any(x['enabled'] for x in loaded_hooks),loaded_hooks
        print(json.dumps({'phase':phase,'installed':details['summary']['installed'],'enabled':enabled,
            'skills':[x['name'] for x in loaded_skills],
            'hooks':[{'event':x['eventName'],'enabled':x['enabled'],'trust':x['trustStatus']} for x in loaded_hooks]},ensure_ascii=False))
    finally:
        (Path(settings['evidence'])/(phase+'-rpc.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        selector.close()
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)
        print('owned app-server exit:',process.returncode)
