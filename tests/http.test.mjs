/** Real HTTP-origin delivery checks. These are not browser navigation tests. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {once} from 'node:events';
import {createStaticServer,normalizePrefix} from '../scripts/serve.mjs';
import {readJSON,root} from '../scripts/validate.mjs';
const styles=readJSON('data/catalog.json');
const routes=[''];for(const lang of ['zh','en']){routes.push(lang+'/');for(const p of ['about','workbench','favorites','custom','compare'])routes.push(lang+'/'+p+'/');for(const s of styles)routes.push(lang+'/style/'+s.id+'/');}
const evidence={kind:'node-real-http-not-browser',routesPerPrefix:routes.length,requests:0,prefixes:[],checks:[]};
async function start(prefix=''){const server=createStaticServer({prefix});server.listen(0,'127.0.0.1');await once(server,'listening');return {server,base:`http://127.0.0.1:${server.address().port}`};}
async function request(url,opts){evidence.requests++;return fetch(url,opts);}
for(const prefix of ['', '/framegami'])test(`HTTP delivers every generated route at ${prefix||'root'}`,async()=>{
 const {server,base}=await start(prefix);
 try{
  for(const route of routes){const r=await request(base+prefix+'/'+route);assert.equal(r.status,200,route);assert.match(r.headers.get('content-type'),/text\/html/);const html=await r.text();assert(html.includes('window.IRO_CONFIG'),route);assert(html.includes('Framegami'),route);}
  for(const file of ['assets/app.js','assets/styles.css','assets/catalog.js','assets/favicon.svg','build-info.json']){const r=await request(base+prefix+'/'+file);assert.equal(r.status,200,file);assert(r.headers.get('content-type'));await r.arrayBuffer();}
  evidence.prefixes.push({prefix:prefix||'/',pages:routes.length,assets:5,status:'PASS'});
 }finally{server.closeAllConnections();server.close();}
});
test('HTTP 404 remains a styled self-contained document at deep paths',async()=>{const {server,base}=await start('/framegami');try{const r=await request(base+'/framegami/zh/style/missing/deeper/');assert.equal(r.status,404);const html=await r.text();assert(html.includes('PAGE NOT FOUND'));assert(!html.includes('src="./assets'));evidence.checks.push('deep404');}finally{server.closeAllConnections();server.close();}});
test('HTTP directory redirects preserve query parameters',async()=>{const {server,base}=await start();try{const r=await request(base+'/zh?q=pixel',{redirect:'manual'});assert.equal(r.status,301);assert.equal(r.headers.get('location'),'/zh/?q=pixel');await r.text();evidence.checks.push('query-preserving-redirect');}finally{server.closeAllConnections();server.close();}});
test('HTTP refuses mutation methods',async()=>{const {server,base}=await start();try{const r=await request(base+'/',{method:'POST',body:'not a backend'});assert.equal(r.status,405);assert.equal(r.headers.get('allow'),'GET, HEAD');await r.text();evidence.checks.push('post405');}finally{server.closeAllConnections();server.close();}});
test('HTTP HEAD returns headers without body',async()=>{const {server,base}=await start();try{const r=await request(base+'/',{method:'HEAD'});assert.equal(r.status,200);assert(+r.headers.get('content-length')>100);assert.equal(await r.text(),'');evidence.checks.push('head');}finally{server.closeAllConnections();server.close();}});
test('HTTP rejects encoded traversal outside dist',async()=>{const {server,base}=await start();try{const r=await request(base+'/%2e%2e%2fpackage.json');assert.equal(r.status,403);await r.text();evidence.checks.push('encoded-traversal');}finally{server.closeAllConnections();server.close();}});
test('HTTP rejects null bytes',async()=>{const {server,base}=await start();try{const r=await request(base+'/%00');assert.equal(r.status,400);await r.text();evidence.checks.push('null-byte');}finally{server.closeAllConnections();server.close();}});
test('HTTP prefix matching does not alias other repositories',async()=>{const {server,base}=await start('/framegami');try{const r=await request(base+'/other/zh/');assert.equal(r.status,404);await r.text();evidence.checks.push('prefix-boundary');}finally{server.closeAllConnections();server.close();}});
test('HTTP configuration rejects unsafe prefixes',()=>{for(const s of ['/../secret','/a//b','/a\\b','//evil'])assert.throws(()=>normalizePrefix(s));assert.equal(normalizePrefix('/framegami/'),'/framegami');});
test.after(()=>{fs.writeFileSync(root+'/docs/http-results.json',JSON.stringify(evidence,null,2)+'\n');});
