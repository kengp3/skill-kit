// Maintainer-only real App Server experiment. Never used by candidate skills.
import {spawn, spawnSync} from 'node:child_process';
import {createServer} from 'node:net';
import {createHash, randomUUID} from 'node:crypto';
import {mkdirSync, readFileSync, writeFileSync, appendFileSync, copyFileSync, cpSync, readdirSync, statSync, chmodSync, existsSync, openSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
const command = process.argv[2];
const evidenceRoot = dirname(fileURLToPath(import.meta.url));
const out = command?.startsWith('network-') ? join(evidenceRoot,'provider-preconnect') : evidenceRoot;
if(command?.startsWith('network-'))mkdirSync(out,{recursive:true});
const binary = '/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex';
const candidate = '/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0';
const demo = '/Users/kengp3/Workspaces/mine/demo-002';
const globalState = '/Users/kengp3/.codex';
const pin = '7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e';
const save = (name, data) => writeFileSync(join(out, name), JSON.stringify(data, null, 2) + '\n');
const read = name => JSON.parse(readFileSync(join(out, name), 'utf8'));
const hash = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const log = data => appendFileSync(join(out, 'rpc.jsonl'), JSON.stringify({at: new Date().toISOString(), ...data}) + '\n');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const globalHashes = () => Object.fromEntries(['auth.json', 'config.toml'].map(p => [p, hash(join(globalState, p))]));
let live;
const clients = [];
function contextExcerpt(event, file) {
  const p=event.payload??{};
  const keys=event.type==='session_meta'?['id','session_id','cwd','runtime_workspace_roots','model_provider']:['turn_id','root_turn_id','cwd','model','effort'];
  const payload=Object.fromEntries(keys.filter(k=>k in p).map(k=>[k,p[k]]));
  if(typeof p.source==='string')payload.source=p.source;
  else if(p.source?.subAgent?.thread_spawn){const s=p.source.subAgent.thread_spawn;payload.source={subAgent:{thread_spawn:Object.fromEntries(['parent_thread_id','depth','agent_path','agent_nickname','agent_role'].filter(k=>k in s).map(k=>[k,s[k]]))}};}
  return {file,type:event.type,timestamp:event.timestamp,payload};
}
function publishSession(raw, threadId, suffix='') {
  const name=`session-${threadId}${suffix}`,privateDir=join(live.state,'evidence-full');mkdirSync(privateDir,{recursive:true,mode:0o700});
  const privatePath=join(privateDir,`${name}.jsonl`);writeFileSync(privatePath,raw,{mode:0o600});chmodSync(privatePath,0o600);
  const lines=raw.split(/(?<=\n)/),omitted=[];const preserved=lines.filter((line,n)=>{if(line.trim()&&JSON.parse(line).type==='session_meta'){omitted.push(n+1);return false;}return true;});
  const file=`${name}.excerpt.jsonl`,excerpt=preserved.join('');writeFileSync(join(out,file),excerpt);
  const sha=text=>createHash('sha256').update(text).digest('hex');
  const countTools=text=>text.split('\n').filter(Boolean).map(JSON.parse).filter(e=>e.type==='response_item'&&['function_call','function_call_output','custom_tool_call','custom_tool_call_output'].includes(e.payload.type)).length;
  const indexPath=join(out,'session-excerpts-index.json');const index=existsSync(indexPath)?JSON.parse(readFileSync(indexPath,'utf8')):[];
  const entry={publishedFile:file,kind:'transparent excerpt',originalPrivatePath:privatePath,originalSha256:sha(raw),publishedSha256:sha(excerpt),originalLineCount:lines.filter(Boolean).length,omittedOriginalLines:omitted,omissionReason:'entire session_meta omitted, including creator identities and base instructions',allOtherLinesBytePreserved:true,originalToolRows:countTools(raw),publishedToolRows:countTools(excerpt)};
  save('session-excerpts-index.json',[...index.filter(e=>e.publishedFile!==file),entry]);return file;
}
function snapshot(path, base = path) {
  return Object.fromEntries(readdirSync(path, {withFileTypes: true}).flatMap(e => {
    const p = join(path, e.name);
    if (e.isSymbolicLink()) throw Error(`unexpected symlink: ${p}`);
    if (e.isDirectory()) return Object.entries(snapshot(p, base));
    return [[p.slice(base.length + 1), hash(p)]];
  }));
}
async function prepare() {
  if (existsSync(join(out, 'live.json'))) throw Error('case already exists; preserve and use the recorded identity');
  if (hash(join(candidate, 'runtime-manifest.json')) !== pin) throw Error('candidate pin mismatch');
  const manifest = JSON.parse(readFileSync(join(candidate, 'runtime-manifest.json')));
  for (const [path, expected] of Object.entries(manifest.files)) if (hash(join(candidate, path)) !== expected) throw Error(`candidate mismatch: ${path}`);
  const caseToken = `g05-${command.startsWith('network-')?'network-':''}${randomUUID()}`;
  const root = `/private/tmp/${caseToken}`, project = join(root, 'case'), state = join(root, 'state');
  mkdirSync(project, {recursive: true, mode: 0o700}); mkdirSync(state, {mode: 0o700}); chmodSync(root, 0o700);
  copyFileSync(join(globalState, 'auth.json'), join(state, 'auth.json')); chmodSync(join(state, 'auth.json'), 0o600);
  const config = `cli_auth_credentials_store = "file"\n[features]\nhooks = false\n[projects.${JSON.stringify(project)}]\ntrust_level = "trusted"\n` + ['archify', 'define-task', 'project-setting'].map(n => `\n[[skills.config]]\npath = "/Users/kengp3/.agents/skills/${n}/SKILL.md"\nenabled = false\n`).join('');
  writeFileSync(join(state, 'config.toml'), config, {mode: 0o600});
  for (const name of ['define-task', 'project-setting', 'task-harness', 'ai-code-review']) cpSync(join(candidate, 'skills', name), join(project, '.agents/skills', name), {recursive: true, filter: p => !p.split('/').some(x => x === 'scripts' || x === '__pycache__')});
  for (const name of ['project-setting.md', 'AGENTS.md']) copyFileSync(join(demo, name), join(project, name));
  writeFileSync(join(project, 'preserve.txt'), 'KEEP_EXISTING_CONTENT\n');
  spawnSync('git', ['init', '-q'], {cwd: project});
  const listener = createServer(); await new Promise(r => listener.listen(0, '127.0.0.1', r));
  const port = listener.address().port; await new Promise(r => listener.close(r));
  live = {caseToken, root, project, state, endpoint: `ws://127.0.0.1:${port}`, candidateManifestSha256: pin, preparedAt: new Date().toISOString()};
  save('live.json', live); save('baseline.json', {global: globalHashes(), inputs: snapshot(project), sourceDemo: Object.fromEntries(['AGENTS.md','project-setting.md'].map(n => [n, hash(join(demo,n))])), stateMode: statSync(state).mode & 0o777, authMode: statSync(join(state,'auth.json')).mode & 0o777});
  save('candidate-manifest.json', manifest); save('isolated-config.json', {config, hooksScope: 'disabled in this transport-only case; not V01 hooks acceptance'});
  console.log(JSON.stringify(live));
}
async function server(label) {
  const env = {...process.env, CODEX_HOME: live.state};
  for (const k of ['OPENAI_API_KEY','CODEX_API_KEY','OPENAI_ACCESS_TOKEN','CHATGPT_AUTH_TOKEN','CODEX_REMOTE_TOKEN']) delete env[k];
  const fd = openSync(join(out, `${label}.stderr.log`), 'a');
  const proc = spawn(binary, ['app-server','--listen',live.endpoint], {cwd: live.project, env, detached: true, stdio: ['ignore',fd,fd]}); proc.unref();
  live[`${label}Pid`] = proc.pid; save('live.json', live);
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(live.endpoint.replace('ws:','http:') + '/readyz')).ok) return; } catch {}
    if (proc.exitCode !== null) throw Error(`${label} exited ${proc.exitCode}`);
    await delay(100);
  }
  throw Error('owned listener readiness timeout; inspect recorded PID, do not restart automatically');
}
async function connect(client) {
  const socket = new WebSocket(live.endpoint); const pending = new Map(); const events = []; let serial = 0;
  await new Promise((resolve,reject) => {socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  socket.addEventListener('message', ev => {
    const message = JSON.parse(ev.data); log({client,direction:'server',message}); events.push(message);
    if ('id' in message && !message.method) { const p = pending.get(message.id); if (p) {pending.delete(message.id);clearTimeout(p.timer); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result);} }
    if ('id' in message && message.method) send({id:message.id,error:{code:-32601,message:'Experiment does not supply interactive user authorization'}});
  });
  socket.addEventListener('close', ev => { log({client,direction:'controller',event:'socket-close',code:ev.code}); for (const p of pending.values()) {clearTimeout(p.timer);p.reject(Error('transport closed; operation result unknown'));} pending.clear(); });
  function send(message) {log({client,direction:'client',message});socket.send(JSON.stringify(message));}
  function rpc(method,params = {},timeout = 60000) {const id = ++serial;return new Promise((resolve,reject) => {const timer=setTimeout(()=>{pending.delete(id);reject(Error(`observation timeout for ${method}; not operation terminal`));},timeout);pending.set(id,{resolve,reject,timer});send({id,method,params});});}
  await rpc('initialize',{clientInfo:{name:`g05_${client}`,version:'1.0'},capabilities:{experimentalApi:true}});send({method:'initialized',params:{}});
  const clientHandle = {rpc,events,socket,close:async()=>{socket.close();await delay(100);}}; clients.push(clientHandle); return clientHandle;
}
const threadOptions = () => ({cwd:live.project,runtimeWorkspaceRoots:[live.project],model:'gpt-6.1-sol',ephemeral:false,sandbox:'workspace-write',approvalPolicy:'on-request',approvalsReviewer:'auto_review',config:{model_reasoning_effort:'low'}});
async function pages(c, method, params, pageSize=1) {
  const data = []; let cursor = null; const seen = new Set();
  do {const page=await c.rpc(method,{...params,limit:pageSize,...(cursor?{cursor}:{})});data.push(...page.data);cursor=page.nextCursor;if(cursor && seen.has(cursor))throw Error('repeated cursor');seen.add(cursor);} while(cursor);
  return {data,nextCursor:null};
}
const listChildren = c => pages(c,'thread/list',{cwd:live.project,parentThreadId:live.parent,sourceKinds:['subAgent','subAgentThreadSpawn','subAgentOther','subAgentReview','subAgentCompact']});
const turns = (c,threadId) => pages(c,'thread/turns/list',{threadId,itemsView:'full',sortDirection:'asc'});
function preserve() {
  const before = read('baseline.json'), after = snapshot(live.project);
  save('preservation.json',{caseInputsUnchanged:Object.entries(before.inputs).every(([p,h])=>after[p]===h), globalBefore:before.global,globalAfter:globalHashes(), globalUnchanged:JSON.stringify(before.global)===JSON.stringify(globalHashes()), caseFiles:after, stateRetained:true});
}
async function metadata() {
  await server('server1'); const c=await connect('preflight');
  save('config-read.json',await c.rpc('config/read',{cwd:live.project,includeLayers:true}));
  const skills = await c.rpc('skills/list',{cwds:[live.project],forceReload:true}); save('skills-list.json',skills);
  const enabled = skills.data.flatMap(d=>d.skills).filter(s=>s.enabled);
  const unexpected=enabled.filter(s=>!s.path.startsWith(join(live.project,'.agents/skills/')) && !s.path.startsWith(join(live.state,'skills/.system/')));
  if (unexpected.length) throw Error('unexpected enabled skill sources; inspect preflight');
  save('metadata-preflight.json',{enabled:enabled.map(s=>({name:s.name,path:s.path})),unexpected,serverPid:live.server1Pid,endpoint:live.endpoint,noModelTurnsStarted:true});
  await c.close(); console.log(JSON.stringify({phase:'metadata',pid:live.server1Pid}));
}
async function start() {
  if(live.parent)throw Error('original parent already recorded; query it, do not redispatch');
  const c=await connect('client1');
  const parent=await c.rpc('thread/start',threadOptions());live.parent=parent.thread.id;save('parent-start.json',parent);save('live.json',live);
  const prompt=`這是已確認的專案根 ${live.project}；啟用 task-harness，依本地四個候選技能及 project-setting.md 保存唯一合約 docs/plans/${live.caseToken}.task-contract.md。這是 G05 client transport 斷線實驗，case=${live.caseToken}。唯一成果 T1：由真實 persistent 原生 child 唯讀核對 preserve.txt；只建立一個 child，名稱 g05_reader，fork_turns=none、自足輸入、繼承主責模型與強度。明確授權此次原生派工。child 工作：先用 shell 唯讀讀 preserve.txt，接著最多等待900秒直到本專案 gate.txt 出現（sleep 1 輪詢；不可寫檔、不可建立背景服務、不可再派 agent、不可執行 Node/Python/helper）；gate出現再讀 preserve.txt，最終只回報精確一行 G05_CHILD_RESULT ${live.caseToken} KEEP_EXISTING_CONTENT。你保存真實 handle、T1 in_progress、原工作與查回依據後，本回合結束，不等待 child、不建立gate、不派第二個worker。後續查明前一律先query原child，不因timeout或通知遺失重派。產品模型不得執行 Node/Python/helper。hooks在本case停用，主動做相同合約檢查且不修改hook設定。`;
  save('parent-prompt.json',{prompt});
  const started=await c.rpc('turn/start',{threadId:live.parent,input:[{type:'text',text:prompt}]});live.parentTurn=started.turn.id;save('live.json',live);
  console.log(JSON.stringify({phase:'parent-started',pid:live.server1Pid,parent:live.parent,turn:live.parentTurn}));
  const deadline=Date.now()+900000;
  while(Date.now()<deadline) {
    let children;
    try {children=await listChildren(c);} catch(error) {log({direction:'controller',event:'child-list-query-not-yet-available',error:String(error),parent:live.parent});await delay(2500);continue;}
    if(children.data.length>1)throw Error('more than one child observed');
    if(children.data.length===1) {
      live.child=children.data[0].id;
      let history;
      try {history=await turns(c,live.child);} catch(error) {log({direction:'controller',event:'child-turn-query-not-yet-available',error:String(error),child:live.child});await delay(2500);continue;}
      const active=history.data.find(t=>t.status==='inProgress');
      if(active){live.childTurn=active.id;save('before-disconnect-child.json',await c.rpc('thread/read',{threadId:live.child}));save('before-disconnect-child-turns.json',history);save('before-disconnect-children.json',children);save('live.json',live);break;}
    }
    await delay(2500);
  }
  if(!live.childTurn)throw Error('observation timeout before real child; preserve server and original parent');
  const red = spawnSync(process.execPath, [join(out,'check-evidence.mjs'),'before'], {encoding:'utf8'});
  save('active-child-red-check.json',{argv:[process.execPath,join(out,'check-evidence.mjs'),'before'],exit:red.status,stdout:red.stdout,stderr:red.stderr});
  if(red.status !== 1 || !red.stderr.includes('inProgress'))throw Error('precondition red did not reject the active child');
  const closed = new Promise((resolve,reject) => {const timer=setTimeout(()=>reject(Error('transport close unconfirmed')),5000);c.socket.addEventListener('close',e=>{clearTimeout(timer);resolve({code:e.code,wasClean:e.wasClean});},{once:true});});
  c.socket.close(4001,'owned client transport fault');
  log({direction:'controller',event:'transport-disconnected',client:'client1',serverPid:live.server1Pid,parent:live.parent,child:live.child,childTurn:live.childTurn,close:await closed,boundary:'client-to-app-server only; deliberate WS disconnection, not TCP packet loss or model spawn result loss'});
  await delay(2000);
  const recovered=await connect('client2');save('reconnect-initial-child.json',await recovered.rpc('thread/read',{threadId:live.child}));save('reconnect-initial-child-turns.json',await turns(recovered,live.child));
  writeFileSync(join(live.project,'gate.txt'),live.caseToken+'\n');log({direction:'controller',event:'gate-released-after-query',child:live.child});
  const finish=Date.now()+900000;let history;
  while(Date.now()<finish){history=await turns(recovered,live.child);const t=history.data.find(t=>t.id===live.childTurn);if(t&&['completed','failed','interrupted'].includes(t.status))break;await delay(2500);}
  save('reconnect-child-turns.json',history);save('reconnect-child.json',await recovered.rpc('thread/read',{threadId:live.child}));save('reconnect-children.json',await listChildren(recovered));save('reconnect-parent-turns.json',await turns(recovered,live.parent));
  preserve();await recovered.close();console.log(JSON.stringify({phase:'reconnected',child:live.child,childTurn:live.childTurn}));
}
async function restartRead() {
  const c=await connect('pre-restart'); const childTurns=await turns(c,live.child),parentTurns=await turns(c,live.parent);
  if(childTurns.data.some(t=>t.status==='inProgress')||parentTurns.data.some(t=>t.status==='inProgress'))throw Error('original turn still active; no server restart');
  await c.close();process.kill(live.server1Pid,'SIGTERM');
  for(let n=0;n<100;n++){try{process.kill(live.server1Pid,0);await delay(100);}catch{break;}}
  try{process.kill(live.server1Pid,0);throw Error('server1 exit unconfirmed');}catch(e){if(e.code!=='ESRCH')throw e;}
  log({direction:'controller',event:'server1-exit-confirmed',serverPid:live.server1Pid,originalTurnsTerminal:true});
  await server('server2');const c2=await connect('client3');save('new-server-child.json',await c2.rpc('thread/read',{threadId:live.child}));save('new-server-child-turns.json',await turns(c2,live.child));save('new-server-children.json',await listChildren(c2));save('new-server-parent-turns.json',await turns(c2,live.parent));save('new-server-all-own-threads.json',await pages(c2,'thread/list',{cwd:live.project,sourceKinds:['vscode','cli','appServer','subAgent','subAgentThreadSpawn','subAgentOther']}));await c2.close();preserve();console.log(JSON.stringify({phase:'new-server-read',pid:live.server2Pid,child:live.child}));
}
async function networkTurn() {
  if(live.parent)throw Error('network request already recorded; query the existing identity');
  const c=await connect('network-client');const parent=await c.rpc('thread/start',threadOptions());live.parent=parent.thread.id;save('parent-start.json',parent);save('live.json',live);
  const prompt=`已確認專案根 ${live.project}。這是自有程序provider預連線拒絕測試，只回覆精確一行 G05_PROVIDER_EGRESS_CHECK；不使用工具、不建立agent、不寫檔。`;
  save('parent-prompt.json',{prompt});const started=await c.rpc('turn/start',{threadId:live.parent,input:[{type:'text',text:prompt}]});live.parentTurn=started.turn.id;save('live.json',live);
  console.log(JSON.stringify({phase:'provider-preconnect-started',pid:live.server1Pid,thread:live.parent,turn:live.parentTurn}));
  const deadline=Date.now()+300000;let history;
  while(Date.now()<deadline){history=await turns(c,live.parent);const t=history.data.find(t=>t.id===live.parentTurn);if(t&&['completed','failed','interrupted'].includes(t.status))break;await delay(2000);}
  save('provider-turns.json',history);preserve();await c.close();console.log(JSON.stringify({phase:'provider-preconnect-observed',turn:history.data.find(t=>t.id===live.parentTurn)}));
}
async function query() {
  const c=await connect('query-original');
  save('query-parent.json',await c.rpc('thread/read',{threadId:live.parent}));
  save('query-parent-turns.json',await turns(c,live.parent));
  if(live.child){save('query-child.json',await c.rpc('thread/read',{threadId:live.child}));save('query-child-turns.json',await turns(c,live.child));}
  preserve();await c.close();console.log(JSON.stringify({phase:'query-original',parent:live.parent,turns:read('query-parent-turns.json').data.map(t=>({id:t.id,status:t.status,error:t.error}))}));
}
async function collect() {
  const c=await connect('collect-original');const all=await pages(c,'thread/list',{cwd:live.project,sourceKinds:['cli','vscode','exec','appServer','subAgent','subAgentReview','subAgentCompact','subAgentThreadSpawn','subAgentOther','unknown']},100);save('final-own-threads.json',all);
  if(live.child)save('final-task-children.json',await pages(c,'thread/list',{cwd:live.project,parentThreadId:live.parent,sourceKinds:['subAgentThreadSpawn']},100));
  const known=[live.parent,live.child,live.newOwner].filter(Boolean);
  const contexts=[];
  for(const threadId of new Set([...all.data.map(t=>t.id),...known])){
    const current=await c.rpc('thread/read',{threadId}),history=await turns(c,threadId);save(`final-${threadId}.json`,{thread:current.thread,turns:history});
    if(history.data.some(t=>t.status==='inProgress'))throw Error('owned turn still active; no process shutdown');
    if(!known.includes(threadId))continue;
    const path=current.thread.path;if(!path?.startsWith(join(live.state,'sessions/')))throw Error('unexpected session path outside owned state');
    const raw=readFileSync(path,'utf8'),publishedFile=publishSession(raw,threadId);
    for(const line of raw.trim().split('\n')){const event=JSON.parse(line);if(['session_meta','turn_context'].includes(event.type))contexts.push(contextExcerpt(event,publishedFile));}
  }
  save('session-contexts.json',contexts);if(existsSync(join(live.project,'docs')))cpSync(join(live.project,'docs'),join(out,live.ownerCorrectionTurn?'artifacts-after-owner-correction':'artifacts','docs'),{recursive:true,force:false,errorOnExist:true});
  preserve();await c.close();const pid=live.server3Pid??live.server2Pid??live.server1Pid;process.kill(pid,'SIGTERM');
  let exited=false;for(let n=0;n<100;n++){try{process.kill(pid,0);await delay(100);}catch(e){if(e.code==='ESRCH'){exited=true;break;}throw e;}}
  save('process-exit.json',{pid,signal:'SIGTERM',exitConfirmed:exited,allKnownTurnsTerminal:true,stateRetained:true,authInEvidence:false});
  if(!exited)throw Error('owned server exit not confirmed');console.log(JSON.stringify({phase:'collected',pid,exitConfirmed:exited,threads:all.data.map(t=>t.id)}));
}
async function newOwner() {
  if(!live.server2Pid||live.newOwner)throw Error('new server required, or new owner already recorded; query existing identity');
  const c=await connect('new-owner-client');const started=await c.rpc('thread/start',threadOptions());live.newOwner=started.thread.id;save('new-owner-start.json',started);save('live.json',live);
  const prompt=`已確認根目錄 ${live.project}。明確啟用task-harness續作既有同任務，唯一合約 docs/plans/${live.caseToken}.task-contract.md。你是同state、新server下的全新主責thread，並非原parent：原parent=${live.parent}，原child原生handle=/root/g05_reader，child thread=${live.child}，原child turn=${live.childTurn}。先讀project-setting.md、原合約及技能規則；先用宿主現有唯讀原生能力查原child handle、原turn終態與成果，請實際用list_agents等查原身分。不可以spawn/followup/send_message/interrupt，不重派、重做或改模型，不跑CLI/Node/Python/helper，不讀state或全機sessions、不建立假工具。若原生能力不能跨主責root查原child，保留unknown，保存你實際查詢與限制，不能把list為空/idle/notLoaded當作原child完成或不存在，也不能以合約記載當live證據。此回合只驗證查回能力；可把直接觀察和限制保存到同一合約，原T1尚未核實則保持未完成。結束回合。`;
  save('new-owner-prompt.json',{prompt});const turn=await c.rpc('turn/start',{threadId:live.newOwner,input:[{type:'text',text:prompt}]});live.newOwnerTurn=turn.turn.id;save('live.json',live);
  console.log(JSON.stringify({phase:'new-owner-started',pid:live.server2Pid,thread:live.newOwner,turn:live.newOwnerTurn}));
  const deadline=Date.now()+900000;let history;
  while(Date.now()<deadline){
    try{history=await turns(c,live.newOwner);}catch(error){log({direction:'controller',event:'new-owner-history-not-yet-available',error:String(error)});await delay(2500);continue;}
    const t=history.data.find(t=>t.id===live.newOwnerTurn);if(t&&['completed','failed','interrupted'].includes(t.status))break;await delay(2500);
  }
  save('new-owner-turns.json',history);save('new-owner-children-of-original.json',await listChildren(c));await c.close();preserve();console.log(JSON.stringify({phase:'new-owner-observed',thread:live.newOwner,status:history.data.find(t=>t.id===live.newOwnerTurn)?.status}));
}
async function prepareOwnerResume() {
  if(!live.newOwner||live.server3Pid)throw Error('known persisted new owner required; do not replace its identity');
  publishSession(readFileSync(join(live.state,'evidence-full',`session-${live.newOwner}.jsonl`),'utf8'),live.newOwner,'-before-correction');
  copyFileSync(join(out,'preservation.json'),join(out,'preservation-before-correction.json'));
  copyFileSync(join(out,'process-exit.json'),join(out,'process-exit-before-correction.json'));
  await server('server3');const c=await connect('owner-resume-preflight');const {ephemeral,...options}=threadOptions();
  save('new-owner-resume.json',await c.rpc('thread/resume',{threadId:live.newOwner,...options}));
  save('new-owner-resume-before-turns.json',await turns(c,live.newOwner));await c.close();console.log(JSON.stringify({phase:'same-owner-resume-prepared',pid:live.server3Pid,thread:live.newOwner,noNewTurn:true}));
}
async function ownerCorrection() {
  if(!live.server3Pid||live.ownerCorrectionTurn)throw Error('prepare same owner resume first, or query the existing correction turn');
  const c=await connect('owner-correction');
  const prompt=`明確續作同一任務與同一合約，澄清上一回合限制：禁止CLI是禁止額外啟動codex、外部dispatcher或helper，不禁止宿主既有的檔案工具、shell cat/rg等普通唯讀檢查；仍禁止Python/Node/helper、讀isolated state或任何全機sessions、codexCLI query，以及spawn/followup/send/interrupt原agent。先實際讀根目錄project-setting.md、原合約docs/plans/${live.caseToken}.task-contract.md、task-harness及必要技能規則，再查本案既有業務成果與原handle。上一回合原生list_agents僅看見當前/root、原/root/g05_reader前綴結果[]，此scope限制保留，不當成child不存在或完成。控制器沒有在此提供原child結果；只依你真能讀到的本地成果與現有原生查詢分開判斷。原child的即時狀態/原turn終態/返回成果仍無直接能力核對時保持unknown，不能以preserve輸入內容或合約記載替代；不要重做T1。可讀寫唯一原合約，保存本次實際能核對和不能核對項目，保持未核實T1未完成，結束本回合。`;
  save('owner-correction-prompt.json',{prompt});const result=await c.rpc('turn/start',{threadId:live.newOwner,input:[{type:'text',text:prompt}]});live.ownerCorrectionTurn=result.turn.id;save('live.json',live);
  console.log(JSON.stringify({phase:'same-owner-correction-started',pid:live.server3Pid,thread:live.newOwner,turn:live.ownerCorrectionTurn}));
  const deadline=Date.now()+900000;let history;
  while(Date.now()<deadline){try{history=await turns(c,live.newOwner);}catch(error){log({direction:'controller',event:'owner-correction-history-not-yet-available',error:String(error)});await delay(2500);continue;}const t=history.data.find(t=>t.id===live.ownerCorrectionTurn);if(t&&['completed','failed','interrupted'].includes(t.status))break;await delay(2500);}
  save('owner-correction-turns.json',history);await c.close();preserve();console.log(JSON.stringify({phase:'same-owner-correction-observed',thread:live.newOwner,status:history.data.find(t=>t.id===live.ownerCorrectionTurn)?.status}));
}
try {
  if(command==='prepare'||command==='network-prepare')await prepare();
  else{live=read('live.json');if(command==='metadata'||command==='network-metadata')await metadata();else if(command==='start')await start();else if(command==='restart-read')await restartRead();else if(command==='network-turn')await networkTurn();else if(command==='new-owner')await newOwner();else if(command==='prepare-owner-resume')await prepareOwnerResume();else if(command==='owner-correction')await ownerCorrection();else if(command==='query'||command==='network-query')await query();else if(command==='collect'||command==='network-collect')await collect();else throw Error('unknown experiment command');}
}catch(error){save(`error-${command}.json`,{error:String(error),stack:error.stack,at:new Date().toISOString(),live});console.error(String(error));for(const c of clients)await c.close();process.exitCode=1;}
