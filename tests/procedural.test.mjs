import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {readJSON,root,validateCatalog,hash} from '../scripts/validate.mjs';
import {getAcceptedExample,buildSearchIndex,searchStyles} from '../src/core.mjs';
const catalog=readJSON('data/catalog.json');
const selected=catalog.filter(x=>(x.illustrations||[]).some(y=>y.kind==='procedural-style-study'));
const b=readJSON('data/benchmark.json');

test('B00 programmatic studies cover ten distinct previously blank IDs',()=>{
 assert.equal(catalog.length,213);
 assert(selected.length>=30);
 assert.equal(new Set(selected.map(x=>x.id)).size,selected.length);
 assert(catalog.filter(x=>x.illustrations.some(i=>i.displayApproved)).length>=105);
 assert.equal(catalog.filter(x=>!x.illustrations.some(i=>i.displayApproved)).length,213-catalog.filter(x=>x.illustrations.some(i=>i.displayApproved)).length);
 assert.equal(searchStyles(buildSearchIndex(catalog,readJSON('data/categories.json')),{status:'images'}).length,catalog.filter(x=>x.illustrations.some(i=>i.displayApproved)).length);
});
test('B00 programmatic studies are not claimed as model examples',()=>{
 for(const s of selected){
  const x=s.illustrations.find(x=>x.kind==='procedural-style-study');
  assert.equal(x.accepted,false);
  assert.equal(x.promptVerified,false);
  assert.equal(x.model,'local-procedural');
  assert.equal(x.requestKind,'deterministic-computer-graphics');
  assert.equal(x.singleIndependentOutput,false);
  assert.equal(x.originalSha256,b.sha256);
  assert.equal(getAcceptedExample(s),null);
  assert.deepEqual(s.testedModels,[]);
 }
});
test('procedural results and previews have unique current bytes',()=>{
 const hashes=new Set();
 for(const s of selected){
  const x=s.illustrations.find(x=>x.kind==='procedural-style-study');
  assert.equal(hash(root+'/public/'+x.path),x.outputSha256);
  assert.equal(hash(root+'/public/'+x.thumbnailPath),x.thumbnailSha256);
  assert.equal(hash(root+'/'+x.toolSourcePath),x.toolSourceSha256);
  assert(!hashes.has(x.outputSha256));hashes.add(x.outputSha256);
 }
 assert.deepEqual(validateCatalog().errors,[]);
});
test('procedural examples cannot forge image-model validation',()=>{
 const copy=structuredClone(catalog);
 const a=copy.find(x=>x.id==='pixel-1bit').illustrations.find(x=>x.kind==='procedural-style-study');
 a.accepted=true;
 assert(validateCatalog(copy).errors.some(x=>x.includes('Procedural study must remain explicitly unvalidated')));
});
test('procedural preview code cannot go stale unnoticed',()=>{
 const copy=structuredClone(catalog);
 copy.find(x=>x.id==='pixel-cga').illustrations[0].toolSourceSha256='0'.repeat(64);
 assert(validateCatalog(copy).errors.some(x=>x.includes('changed procedural generation program')));
});
