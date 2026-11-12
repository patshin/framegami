import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {readJSON,root,validateCatalog,hash} from '../scripts/validate.mjs';
import {getDisplaySample,getAcceptedExample,buildSearchIndex,searchStyles,readQuery} from '../src/core.mjs';
const catalog=readJSON('data/catalog.json'),categories=readJSON('data/categories.json'),index=buildSearchIndex(catalog,categories),benchmark=readJSON('data/benchmark.json');
test('v03 unified source original actually exists and matches its hash',()=>assert.equal(hash(root+'/public/'+benchmark.path),benchmark.sha256));
test('v03 all 213 canonical styles are retained',()=>assert.equal(catalog.length,213));
test('v03 featured image sources are internally consistent',()=>{const active=catalog.map(s=>getDisplaySample(s)).filter(Boolean);assert(active.length>=105);assert(active.every(x=>['same-input-showcase','montage-derived-preview','procedural-style-study'].includes(x.kind)));assert.equal(active.length+catalog.filter(s=>!getDisplaySample(s)).length,catalog.length);});
test('v03 missing styles match live image records',()=>assert.equal(searchStyles(index,{status:'missing-images'}).length,catalog.filter(s=>!getDisplaySample(s)).length));
test('v03 image filter and prompt-verified filter are distinct',()=>{assert.equal(searchStyles(index,{status:'images'}).length,catalog.filter(s=>getDisplaySample(s)).length);assert.equal(searchStyles(index,{status:'examples'}).length,0);});
test('v03 style illustrations do not certify current prompts',()=>assert(catalog.every(s=>getAcceptedExample(s)===null)));
test('v03 image-availability filters can be linked',()=>assert.equal(readQuery('?status=images').status,'images'));
test('v03 pending-asset filter can be linked',()=>assert.equal(readQuery('?status=missing-images').status,'missing-images'));
test('v03 duplicate generated outputs cannot fill different style cards',()=>{const copy=structuredClone(catalog),sampled=copy.filter(s=>s.illustrations.length);sampled[1].illustrations[0].sourceOutputSha256=sampled[0].illustrations[0].sourceOutputSha256;assert(validateCatalog(copy).errors.some(x=>x.includes('multiple styles')));});
test('v03 a wrong style assignment fails',()=>{const copy=structuredClone(catalog);copy[0].illustrations[0].styleId='wrong';assert(validateCatalog(copy).errors.some(x=>x.includes('assignment')));});
test('v03 illustration cannot be called an exact prompt test',()=>{const copy=structuredClone(catalog);copy[0].illustrations[0].promptVerified=true;assert(validateCatalog(copy).errors.some(x=>x.includes('exact-prompt')));});
test('v03 an unsafe image path is rejected',()=>{const copy=structuredClone(catalog);copy[0].illustrations[0].path='../sample.webp';assert(validateCatalog(copy).errors.some(x=>x.includes('Unsafe illustration')));});
test('v03 stale or changed illustration bytes fail integrity checks',()=>{const copy=structuredClone(catalog);copy[0].illustrations[0].outputSha256='0'.repeat(64);assert(validateCatalog(copy).errors.some(x=>x.includes('changed illustration')));});
test('v03 a source-reference mismatch fails',()=>{const copy=structuredClone(catalog);copy[0].illustrations[0].originalSha256='0'.repeat(64);assert(validateCatalog(copy).errors.some(x=>x.includes('reference does not match')));});
test('v03 Gemini and FLUX do not inherit a tested flag from the image sample',()=>{for(const m of ['gemini','flux']){assert(getDisplaySample(catalog[0],m,'en'));assert.equal(getAcceptedExample(catalog[0],m,'en'),null);assert.equal(catalog[0].modelStatus[m],'untested');}});
test('v03 standalone preview embeds the source and WebP case assets',()=>{const h=fs.readFileSync(root+'/IRO-preview.html','utf8');assert(h.includes('data:image/webp;base64,'));assert(h.includes('data:image/png;base64,'));assert(!h.includes('a_wide_high_resolution'));});
for(const s of catalog.filter(s=>getDisplaySample(s))){test('v03 '+s.id+' has distinct valid thumbnail and full-image assets',()=>{const im=getDisplaySample(s);for(const p of [im.path,im.thumbnailPath]){const bytes=fs.readFileSync(root+'/public/'+p);assert.equal(bytes.subarray(0,4).toString(),'RIFF');assert.equal(bytes.subarray(8,12).toString(),'WEBP');}assert.equal(im.width/im.height,(()=>{const [w,h]=im.aspectRatio.split(':').map(Number);return w/h;})());assert.notEqual(im.path,im.thumbnailPath);if(im.generationRecordStatus==='unavailable'){
 assert.equal(im.generationId,null);
 assert.equal(im.kind,'same-input-showcase');
 assert.equal(im.accepted,false);
 assert.equal(im.promptVerified,false);
 assert.equal(getAcceptedExample(s),null);
 }else assert(im.generationId);});}

test('v04 cropped montage previews have independently auditable provenance',()=>{for(const s of catalog.filter(s=>getDisplaySample(s)?.kind==='montage-derived-preview')){const x=getDisplaySample(s);assert.equal(x.singleIndependentOutput,false);assert.equal(x.promptVerified,false);assert.equal(x.originalSha256,null);assert.equal(hash(root+'/'+x.sourceMontagePath),x.sourceMontageSha256);assert.equal(hash(root+'/'+x.sourceCropPath),x.sourceOutputSha256);assert.equal(x.cropBox.length,4);}});
test('v04 provisional images cannot claim accepted prompt-evidence status',()=>{for(const s of catalog.filter(s=>getDisplaySample(s)?.kind==='montage-derived-preview')){const x=getDisplaySample(s);assert.equal(getAcceptedExample(s),null);assert.equal(s.modelStatus.chatgpt,'untested');}});
