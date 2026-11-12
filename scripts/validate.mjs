import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {composePrompt,safeHTTPS,MODELS,LANGS} from '../src/core.mjs';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const readJSON=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
export const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function validateCatalog(data=readJSON('data/catalog.json'),cats=readJSON('data/categories.json'),sources=readJSON('data/sources.json'),benchmark=readJSON('data/benchmark.json')) {
 const errors=[],ids=new Set(),texts=new Set(),categories=new Map(cats.map(x=>[x.id,x])),sourceIds=new Set(sources.map(x=>x.id)),sourceIllustrationOwners=new Map();
 for(const s of sources)if(!safeHTTPS(s.url))errors.push('Unsafe source URL: '+s.id);
 for(const s of data){
  const err=m=>errors.push(s.id+': '+m);
  if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s.id)||ids.has(s.id))err('Invalid or duplicate ID');ids.add(s.id);
  if(!categories.has(s.category)||!categories.get(s.category)?.families[s.family])err('Unknown category/family');
  for(const field of ['name','technique','avoid','limits'])for(const lang of ['zh','en'])if(typeof s[field]?.[lang]!=='string'||!s[field][lang].trim())err('Missing localized '+field+'.'+lang);
  if(s.technique?.en?.split(/\s+/).length<15)err('Insufficient technique specificity');
  const text=s.technique.en+'|'+s.avoid.en;if(texts.has(text))err('Duplicate technique');texts.add(text);
  if(!Array.isArray(s.sources)||!s.sources.length||s.sources.some(x=>!sourceIds.has(x)))err('Missing source references');
  if(!Array.isArray(s.examples))err('Missing example list');
  for(const model of ['chatgpt','gemini','flux'])for(const lang of ['zh','en']){
    const p=composePrompt(s,model,lang);if(p.length<(lang==='zh'?240:650))err('Prompt too short for its language');
    if(/undefined|\[object Object\]/.test(p))err('Broken prompt composition');
  }
  for(const sample of s.examples||[]){
   if(!sample.accepted)continue;
   if(!MODELS.includes(sample.model)||!LANGS.includes(sample.lang))err('Accepted sample needs an explicit supported model and prompt language');
   if(sample.styleId!==s.id)err('Example is attached to the wrong style');
   if(sample.requestKind!=='image-edit'||sample.singleIndependentOutput!==true)err('Example must be one independent image-edit output, not a montage crop');
   if(!benchmark.path||!benchmark.sha256) {err('Accepted sample has no frozen benchmark');continue;}
   if(sample.promptVersion!==s.version)err('Stale sample prompt version');
   if(sample.originalSha256!==benchmark.sha256)err('Wrong original image');
   if(!sample.path||path.isAbsolute(sample.path)||sample.path.split('/').includes('..')){err('Unsafe example path');continue;}
   const image=path.join(root,'public',sample.path);
   if(!fs.existsSync(image)){err('Missing example image');continue;}
   if(hash(image)!==sample.outputSha256)err('Example hash mismatch');
   if(!sample.promptPath||sample.promptPath.split('/').includes('..')||path.isAbsolute(sample.promptPath)){err('Missing prompt evidence path');continue;}
   const promptPath=path.join(root,sample.promptPath);
   if(!fs.existsSync(promptPath)||hash(promptPath)!==sample.promptSha256)err('Missing or mismatched actual prompt evidence');
   else if(MODELS.includes(sample.model)&&LANGS.includes(sample.lang)){
    const actual=fs.readFileSync(promptPath,'utf8').trimEnd();
    if(actual!==composePrompt(s,sample.model,sample.lang))err('Actual submitted prompt does not match this preset; keep it as a separate unaccepted experiment');
   }
   if(!sample.date||!sample.environment||!sample.reviewer)err('Incomplete provenance');
   if(!['identity','composition','style','wholeScene','anatomy'].every(k=>sample.review?.[k]===true))err('Incomplete visual review');
  }
  const accepted=s.examples?.filter(x=>x.accepted)||[];
  for(const ill of s.illustrations||[]){
   if(ill.styleId!==s.id)err('Illustration assignment does not match style ID');
   if(ill.generationRecordStatus==='unavailable' && (ill.kind!=='same-input-showcase'||ill.generationId!==null||ill.accepted!==false||ill.promptVerified!==false))err('Incomplete generation record must remain an unvalidated independent showcase');
   if(ill.promptVerified===true)err('Illustration cannot be marked as an exact-prompt test');
   if(!ill.path||path.isAbsolute(ill.path)||ill.path.split('/').includes('..')){err('Unsafe illustration path');continue;}
   const ip=path.join(root,'public',ill.path);
   if(!fs.existsSync(ip)||hash(ip)!==ill.outputSha256)err('Missing or changed illustration bytes');
   if(ill.thumbnailPath){
     if(path.isAbsolute(ill.thumbnailPath)||ill.thumbnailPath.split('/').includes('..'))err('Unsafe illustration thumbnail path');
     else {const tp=path.join(root,'public',ill.thumbnailPath); if(!fs.existsSync(tp)||hash(tp)!==ill.thumbnailSha256)err('Missing or changed illustration thumbnail bytes');}
   }
   // Imported source files remain inspectable and must match their SHA-256.
   if(ill.sourceImagePath){
     const rel=ill.sourceImagePath;
     if(typeof rel!=='string'||!rel.startsWith('evidence/imported-packs/')||path.isAbsolute(rel)||rel.split('/').includes('..'))err('Unsafe imported source path');
     else {const p=path.join(root,rel);if(!fs.existsSync(p)||hash(p)!==ill.sourceOutputSha256)err('Missing or changed imported raw source');}
   }
   if(ill.kind==='montage-derived-preview') {
     if(ill.accepted!==false||ill.promptVerified!==false||ill.singleIndependentOutput!==false||ill.originalId!==null||ill.originalSha256!==null)err('Montage crop must remain explicitly provisional and have no B00 edit claim');
     for(const [field,digest] of [['sourceMontagePath','sourceMontageSha256'],['sourceCropPath','sourceOutputSha256']]) {
       const rel=ill[field];
       if(!rel||path.isAbsolute(rel)||rel.split('/').includes('..')){err('Unsafe montage evidence path');continue;}
       const ep=path.join(root,rel);
       if(!fs.existsSync(ep)||hash(ep)!==ill[digest])err('Missing or changed montage source evidence');
     }
     if(!Array.isArray(ill.cropBox)||ill.cropBox.length!==4||ill.cropBox.some(n=>!Number.isInteger(n)||n<0))err('Missing original montage crop rectangle');
     if(!ill.generationId||!ill.sourcePanelLabel)err('Missing generated-montage provenance');
   }else if(ill.kind==='procedural-style-study') {
     if(ill.accepted!==false||![true,false].includes(ill.displayApproved)||ill.promptVerified!==false)err('Procedural study must remain explicitly unvalidated');
     if(ill.requestKind!=='deterministic-computer-graphics'||ill.model!=='local-procedural'||ill.singleIndependentOutput!==false)err('Procedural study must not claim model generation');
     if(benchmark.sha256&&ill.originalSha256!==benchmark.sha256)err('Procedural study does not match frozen B00 source');
     const rel=ill.toolSourcePath;
     if(!rel||path.isAbsolute(rel)||rel.split('/').includes('..'))err('Unsafe procedural source path');
     else {const program=path.join(root,rel);if(!fs.existsSync(program)||hash(program)!==ill.toolSourceSha256)err('Missing or changed procedural generation program');}
     if(!ill.reviewNote?.zh||!ill.reviewNote?.en)err('Missing bilingual procedural preview disclosure');
   }else if(benchmark.sha256&&ill.originalSha256!==benchmark.sha256)err('Illustration reference does not match benchmark original');
   if(ill.sourceOutputSha256){const prev=sourceIllustrationOwners.get(ill.sourceOutputSha256); if(prev&&prev!==s.id)err('One generated output cannot be assigned to multiple styles'); else sourceIllustrationOwners.set(ill.sourceOutputSha256,s.id);}
  }
  if(s.status==='exampled'&&!accepted.length)err('Example badge without an accepted example');
  if(s.testedModels?.some(m=>!accepted.some(e=>e.model===m)))err('Model validation without image evidence');
  for(const m of MODELS){if(!['untested','exampled'].includes(s.modelStatus?.[m]))err('Invalid model status');if(s.modelStatus?.[m]==='exampled'&&!accepted.some(e=>e.model===m))err('Model status badge without image evidence');}
 }
 if(benchmark.path){if(path.isAbsolute(benchmark.path)||benchmark.path.includes('\\')||benchmark.path.split('/').includes('..'))errors.push('Unsafe benchmark path');else{const p=path.join(root,'public',benchmark.path);if(!fs.existsSync(p)||hash(p)!==benchmark.sha256)errors.push('Benchmark file/hash mismatch');}}
 return {errors,stats:{styles:data.length,categories:cats.length,families:new Set(data.map(s=>s.category+'/'+s.family)).size,sources:sources.length,examples:data.reduce((n,s)=>n+s.examples.filter(x=>x.accepted).length,0),exampledStyles:data.filter(s=>s.examples.some(x=>x.accepted)).length}};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){const result=validateCatalog();if(result.errors.length){console.error(result.errors.join('\n'));process.exit(1);}console.log(JSON.stringify(result.stats,null,2));console.log('Content schema passed. This does not certify image quality.');}
