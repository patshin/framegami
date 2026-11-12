import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {root} from './validate.mjs';
const dist=path.join(root,'dist');let checked=0;
function walk(dir){for(const item of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,item.name);if(item.isDirectory())walk(p);else if(item.name==='index.html'){
const html=fs.readFileSync(p,'utf8');const config=JSON.parse(html.match(/window\.IRO_CONFIG=(\{.*?\});/)[1]);
const rel=path.relative(dist,p).replaceAll(path.sep,'/');
for(const prefix of ['/','/framegami/']){const url='https://owner.github.io'+prefix+rel.replace(/index\.html$/,'');const base=new URL(config.base,url);assert.equal(base.pathname,prefix,'Bad base for '+rel);
for(const match of html.matchAll(/(?:src|href)="([^"#]+\.(?:js|css|svg))"/g)){const target=new URL(match[1],url).pathname;assert(target.startsWith(prefix));const local=path.join(dist,target.slice(prefix.length));assert(fs.existsSync(local),'Missing asset '+local);}}
assert(html.includes('<noscript>'));checked++;}}}
walk(dist);assert(checked>400);fs.writeFileSync(path.join(root,'docs/static-route-results.json'),JSON.stringify({pages:checked,prefixes:['/','/framegami/'],checks:checked*2,result:'PASS',method:'URL resolution and local output-file verification; not a live browser navigation test'},null,2));console.log(`${checked} static routes × 2 prefixes passed asset-path resolution checks.`);
