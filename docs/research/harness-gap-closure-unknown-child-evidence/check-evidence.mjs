// Maintainer-only public App Server readback checks; no product runtime dependency.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
const root = dirname(fileURLToPath(import.meta.url));
const read = name => JSON.parse(readFileSync(join(root, name), 'utf8'));
const live = read('live.json');
const expected = `G05_CHILD_RESULT ${live.caseToken} KEEP_EXISTING_CONTENT`;
function assertCompleted(turns) {
  const turn = turns.find(t => t.id === live.childTurn);
  assert.equal(turn?.status, 'completed', 'original turn terminal, not thread idle/notLoaded');
  assert.ok(turn.items.some(i => i.type === 'agentMessage' && i.text.trim() === expected), 'literal child output from persisted public history');
}
if (process.argv[2] === 'before') {
  assertCompleted(read('before-disconnect-child-turns.json').data);
  throw Error('precondition red must fail while the original child is still waiting');
}
const original = read('before-disconnect-child.json').thread;
const recovered = read('reconnect-child.json').thread;
const turns = read('reconnect-child-turns.json').data;
const originalTurns = read('before-disconnect-child-turns.json').data;
const children = read('reconnect-children.json');
assert.equal(original.id, live.child, 'precondition: real original child ID');
assert.equal(original.ephemeral, false, 'precondition: persistent child');
assert.equal(original.parentThreadId, live.parent, 'precondition: original parent relationship');
assert.ok(originalTurns.some(t => t.id === live.childTurn && t.status === 'inProgress'), 'precondition: child turn active before transport loss');
assert.equal(recovered.id, original.id, 'same child recovered');
assert.equal(recovered.parentThreadId, live.parent, 'same parent recovered');
assert.deepEqual(children.data.map(t => t.id), [original.id], 'exactly one child; no redispatch');
assert.equal(children.nextCursor, null, 'listing reached last page');
assert.deepEqual(read('final-task-children.json').data.map(t => t.id), [original.id], 'final explicit task-child source and parent filter still find one original worker');
assertCompleted(turns);
const fromNewServer = read('new-server-child.json').thread;
assert.equal(fromNewServer.id, original.id, 'new server reads original child identity');
assert.equal(fromNewServer.parentThreadId, live.parent, 'new server preserves original parent relationship');
assertCompleted(read('new-server-child-turns.json').data);
assert.notEqual(live.server2Pid, live.server1Pid, 'separate server identities');
const events = readFileSync(join(root, 'rpc.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const dropped = events.find(e => e.direction === 'controller' && e.event === 'transport-disconnected');
assert.ok(dropped && dropped.serverPid === live.server1Pid && events.some(e => e.event === 'socket-close' && e.client === dropped.client && e.code === dropped.close.code), 'actual owned WebSocket close event, independent of requested close code');
assert.ok(events.some(e => e.client === 'client2' && e.direction === 'client' && e.message.method === 'thread/read' && e.message.params.threadId === live.child), 'new client queried original child');
assert.ok(events.some(e => e.client === 'client3' && e.message?.method === 'thread/list' && e.message.params.cursor), 'actual second page queried on new server');
assert.equal(read('preservation.json').caseInputsUnchanged, true);
assert.equal(read('preservation.json').globalUnchanged, true);
assert.equal(read('process-exit.json').exitConfirmed, true);
assert.equal(read('process-exit.json').pid, live.server3Pid ?? live.server2Pid, 'latest owned server exit, not an older lifecycle receipt');
const parentRaw = readFileSync(join(root, `session-${live.parent}.excerpt.jsonl`), 'utf8').trim().split('\n').map(JSON.parse);
assert.equal(parentRaw.filter(e => e.type === 'response_item' && e.payload.namespace === 'collaboration' && e.payload.name === 'spawn_agent').length, 1, 'one genuine model spawn call, independent of controller listing');
const newOwnerRaw = readFileSync(join(root, `session-${live.newOwner}.excerpt.jsonl`), 'utf8').trim().split('\n').map(JSON.parse);
assert.equal(newOwnerRaw.filter(e => e.type === 'response_item' && e.payload.namespace === 'collaboration' && ['spawn_agent','followup_task','send_message','interrupt_agent'].includes(e.payload.name)).length, 0, 'new owner never redispatched or mutated original agent');
console.log('PASS: original persistent child and original completed turn recovered after owned transport loss, with one child and literal result');
