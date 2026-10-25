"""Maintainer-only isolated native capability probe; no model/authentication copied."""
import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import time

EVIDENCE = Path(__file__).resolve().parent
ROOT = Path(tempfile.mkdtemp(prefix='unified-native-probe-'))
STATE = ROOT / 'state'
PROJECT = ROOT / 'project'
STATE.mkdir()
PROJECT.mkdir()
(STATE / 'config.toml').write_text('cli_auth_credentials_store = "file"\n[features]\nhooks = true\n[analytics]\nenabled = false\n')
(STATE / 'hooks.json').write_text(json.dumps({'hooks': {'SessionStart': [{'hooks': [{'type': 'command', 'command': 'echo UNIFIED_T01_STATIC_SESSIONSTART', 'timeout': 5}]}]}}))
ENV = os.environ.copy()
ENV['CODEX_HOME'] = str(STATE)
for k in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN'):
    ENV.pop(k, None)

records = []
errors = (EVIDENCE / 'native-server.stderr').open('w')
process = subprocess.Popen(['codex','app-server','--stdio'],cwd=PROJECT,env=ENV,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors)
selector = selectors.DefaultSelector()
selector.register(process.stdout,selectors.EVENT_READ)
buffer = b''
next_id = 0

def read_until(rid, timeout=15):
    global buffer
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        while b'\n' in buffer:
            raw,buffer=buffer.split(b'\n',1)
            if not raw: continue
            msg=json.loads(raw)
            records.append({'direction':'server','message':msg})
            if msg.get('id')==rid and ('result' in msg or 'error' in msg):return msg
            if 'id' in msg and 'method' in msg:
                response={'id':msg['id'],'error':{'code':-32601,'message':'probe does not authorize server operations'}}
                process.stdin.write((json.dumps(response)+'\n').encode());process.stdin.flush()
                records.append({'direction':'client','message':response})
        for key,_ in selector.select(.1):
            data=os.read(key.fd,65536)
            if not data: raise RuntimeError('server EOF')
            buffer+=data
    raise TimeoutError(rid)

def rpc(method,params):
    global next_id
    next_id+=1
    msg={'id':next_id,'method':method,'params':params}
    records.append({'direction':'client','message':msg})
    process.stdin.write((json.dumps(msg)+'\n').encode());process.stdin.flush()
    return read_until(next_id)

summary={'isolationRoot':str(ROOT),'authenticationCopied':False,'explicitAuthEnvRemoved':True}
try:
    summary['initialize']=rpc('initialize',{'clientInfo':{'name':'unified_t01','version':'1.0'},'capabilities':{'experimentalApi':True}})
    process.stdin.write(b'{"method":"initialized","params":{}}\n');process.stdin.flush()
    summary['account']=rpc('account/read',{'refreshToken':False})
    summary['hooks']=rpc('hooks/list',{'cwds':[str(PROJECT)]})
    summary['models']=rpc('model/list',{})
    summary['thread']=rpc('thread/start',{'cwd':str(PROJECT),'ephemeral':True,'sandbox':'read-only','approvalPolicy':'never','model':'gpt-6.1-sol','config':{'model_reasoning_effort':'low'}})
    result=summary['thread'].get('result',{})
    thread=result.get('thread',{}).get('id')
    if thread:
        summary['threadRead']=rpc('thread/read',{'threadId':thread,'includeTurns':True})
    # A real authentication failure is observable without making a model request with credentials.
    if thread and summary['account'].get('result',{}).get('account') is None:
        summary['turn']=rpc('turn/start',{'threadId':thread,'input':[{'type':'text','text':'Reply only T01_OK. Do not use tools.'}]})
        deadline=time.monotonic()+8
        terminal=False
        while time.monotonic()<deadline and not terminal:
            while b'\n' in buffer:
                raw,buffer=buffer.split(b'\n',1)
                if not raw:continue
                msg=json.loads(raw);records.append({'direction':'server','message':msg})
                if msg.get('method')=='turn/completed':terminal=True
            if terminal:break
            for key,_ in selector.select(.1):
                data=os.read(key.fd,65536)
                if not data:terminal=True;break
                buffer+=data
        summary['turnTerminalObserved']=terminal
except Exception as exc:
    summary['probeError']=str(exc)
finally:
    process.stdin.close()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate();process.wait(timeout=5)
    summary['ownedProcessExit']=process.returncode
    selector.close();errors.close()
    (EVIDENCE/'native-rpc.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    (EVIDENCE/'native-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('initialize','models','hooks','thread','threadRead','turn')},ensure_ascii=False))
    print('RPC records:',len(records))
