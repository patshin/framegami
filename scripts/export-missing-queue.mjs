#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {composePrompt,getDisplaySample} from '../src/core.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json'),'utf8'));
const missing=catalog.filter(s=>!getDisplaySample(s));
const result={schema:'iro-image-production-queue-v1',total:catalog.length,remaining:missing.length,benchmark_original:'public/benchmark/B00-original.png',preferred_model:'chatgpt',
 instructions:'Use one full image per style when possible. If supplied as a montage, preserve original montage and exact crop coordinates. The prompt has not been empirically validated.',
 styles:missing.map(s=>({style_id:s.id,name_zh:s.name.zh,name_en:s.name.en,category:s.category,family:s.family,prompt_version:s.version,
 prompt_zh:composePrompt(s,'chatgpt','zh'),prompt_en:composePrompt(s,'chatgpt','en')}))};
const out=process.argv[2]?path.resolve(process.argv[2]):path.join(root,'data/image-production-queue.json');
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('Missing style queue:',missing.length,'=>',out);
