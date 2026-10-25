// Qualification only: no provider sampling, credentials, or system policy changes.
import {createConnection} from 'node:net';
import assert from 'node:assert/strict';
const loopback = await fetch('http://127.0.0.1:61195/readyz');
const outbound = await new Promise(resolve => {
  // TEST-NET avoids DNS ambiguity and cannot be mistaken for a live provider request.
  const socket = createConnection({host:'192.0.2.1',port:443});
  socket.setTimeout(5000);
  socket.once('connect',()=>{socket.destroy();resolve({connected:true});});
  socket.once('error',error=>resolve({connected:false,code:error.code,message:error.message}));
  socket.once('timeout',()=>{socket.destroy();resolve({connected:false,code:'OBSERVATION_TIMEOUT'});});
});
console.log(JSON.stringify({at:new Date().toISOString(),pid:process.pid,loopbackStatus:loopback.status,outbound}));
assert.equal(loopback.status,200,'owned loopback endpoint remains accessible');
assert.equal(outbound.connected,false,'external network denied for owned process');
assert.equal(outbound.code,'EPERM','OS network permission denial, not provider/application response');
