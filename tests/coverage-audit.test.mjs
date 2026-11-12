import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {root,readJSON} from '../scripts/validate.mjs';
import {getDisplaySample} from '../src/core.mjs';

const reportPath=path.join(root,'evidence/image-coverage.json');
const getReport=()=>JSON.parse(fs.readFileSync(reportPath,'utf8'));

test('gallery audit recomputes source-aware coverage (independent AI, montage, procedural)',()=>{
  execFileSync(process.execPath,[path.join(root,'scripts/gallery-coverage.mjs')],{cwd:root,encoding:'utf8'});
  const c=getReport();
  const catalog=readJSON('data/catalog.json'),active=catalog.map(getDisplaySample),k=(kind)=>active.filter(x=>x?.kind===kind).length;
  assert.deepEqual({total:c.total,withImages:c.withImages,independent:c.independentShowcases,montage:c.provisionalMontageCrops,procedural:c.proceduralStudies,missing:c.missing,accepted:c.exactPromptValidated},
    {total:213,withImages:active.filter(Boolean).length,independent:k('same-input-showcase'),montage:k('montage-derived-preview'),procedural:k('procedural-style-study'),missing:active.filter(x=>!x).length,accepted:0});
});

test('procedural studies never count as independent AI image edits',()=>{
  const c=getReport();
  const algorithms=c.entries.filter(x=>x.imageSource==='deterministic-B00-processing');
  assert.equal(algorithms.length,readJSON('data/catalog.json').filter(x=>getDisplaySample(x)?.kind==='procedural-style-study').length);
  for(const x of algorithms){
    assert.equal(x.status,'PROCEDURAL_B00_STUDY_NOT_AI_GENERATED');
    assert.equal(x.independentlyGenerated,false);
    assert.equal(x.promptVerified,false);
    assert(x.imagePath?.endsWith('.webp'));
  }
});

test('montage crops never count as independent image edits',()=>{
  const entries=getReport().entries.filter(x=>x.imageSource==='cropped-generated-montage');
  assert.equal(entries.length,readJSON('data/catalog.json').filter(x=>getDisplaySample(x)?.kind==='montage-derived-preview').length);
  assert(entries.every(x=>!x.independentlyGenerated && !x.promptVerified));
});

test('unillustrated styles remain unmodified and report missing images',()=>{
  const entries=getReport().entries.filter(x=>x.status==='MISSING_IMAGE');
  assert.equal(entries.length,readJSON('data/catalog.json').filter(x=>!getDisplaySample(x)).length);
  assert(entries.every(x=>!x.imagePath && !x.independentlyGenerated));
});
