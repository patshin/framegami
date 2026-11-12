import test from 'node:test';
import assert from 'node:assert/strict';
import {readJSON,validateCatalog} from '../scripts/validate.mjs';
import {getDisplaySample} from '../src/core.mjs';
const catalog=readJSON('data/catalog.json'), by=new Map(catalog.map(x=>[x.id,x]));
const added=['egg-tempera','sanguine-chalk','ink-stipple','etching-line','rinpa-gold','city-pop-airbrush','patchwork','hammered-metal'];
test('eight new styles and two replacement showcases are correctly indexed',()=>{
 for(const id of [...added,'pixel-1bit','thermal-palette']){
   const x=getDisplaySample(by.get(id));assert.equal(x.kind,'same-input-showcase');
   assert.equal(x.requestKind,'standalone-same-scene-generation');
   assert.equal(x.promptVerified,false);assert.equal(x.accepted,false);
 }
 assert(catalog.filter(s=>getDisplaySample(s)).length>=105);
});
test('original procedural image records survive both upgrades',()=>{
 for(const id of ['pixel-1bit','thermal-palette']){
   const xs=by.get(id).illustrations;
   assert.equal(xs.length,2);assert.equal(xs[1].kind,'procedural-style-study');
   assert.match(xs[1].path,/procedural-v1\.webp$/);
 }
});
test('all image records still validate with no forged prompt-verified status',()=>{
 assert.deepEqual(validateCatalog().errors,[]);
 assert.equal(catalog.filter(s=>(s.examples||[]).some(x=>x.accepted)).length,0);
});
