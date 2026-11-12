// Writes jobs and prompt hashes. DOES NOT call an image model or mark any test passed.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
import {root,readJSON} from './validate.mjs';import {composePrompt,MODELS,LANGS} from '../src/core.mjs';
const model=process.argv[2]||'chatgpt',lang=process.argv[3]||'en';
if(!MODELS.includes(model)||!LANGS.includes(lang))throw new Error('Usage: node scripts/prepare-examples.mjs [chatgpt|gemini|flux] [zh|en]');
const b=readJSON('data/benchmark.json');if(!b.sha256||!b.path)throw new Error('First freeze a qualifying standalone B00 original.');
const list=readJSON('data/catalog.json');fs.mkdirSync(path.join(root,'evidence/jobs'),{recursive:true});
const jobs=list.map(s=>{const prompt=composePrompt(s,model,lang)+'\n',promptPath=`evidence/jobs/${s.id}.${model}.${lang}.txt`;fs.writeFileSync(path.join(root,promptPath),prompt);return {styleId:s.id,model,lang,requestKind:'image-edit',singleIndependentOutput:false,promptVersion:s.version,originalPath:b.path,originalSha256:b.sha256,promptPath,promptSha256:crypto.createHash('sha256').update(prompt).digest('hex'),status:'PENDING_GENERATION',outputPath:null,review:null};});
fs.writeFileSync(path.join(root,`evidence/jobs-${model}-${lang}.json`),JSON.stringify(jobs,null,2)+'\n');
console.log(`${jobs.length} pending jobs written. Nothing generated; nothing verified.`);
